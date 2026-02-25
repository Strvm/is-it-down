from fastapi import FastAPI, Request, Response
from starlette.background import BackgroundTask, BackgroundTasks

from is_it_down.api.bigquery_store import get_bigquery_api_store

_SERVICES_PREFIX_PARTS = ("v1", "services")
_NON_DETAIL_SEGMENTS = frozenset({"uptime", "checker-trends"})


def _service_slug_from_path(path: str) -> str | None:
    parts = tuple(part for part in path.split("/") if part)
    if len(parts) != 3:
        return None
    if parts[:2] != _SERVICES_PREFIX_PARTS:
        return None
    slug = parts[2]
    if not slug or slug in _NON_DETAIL_SEGMENTS:
        return None
    return slug


def _resolve_client_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip() or None
    if request.client is None:
        return None
    return request.client.host


def _append_background_task(response: Response, task: BackgroundTask) -> None:
    if response.background is None:
        response.background = task
        return

    tasks = BackgroundTasks()
    tasks.add_task(response.background)
    tasks.add_task(task)
    response.background = tasks


def register_service_detail_tracking_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def service_detail_tracking_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
        response = await call_next(request)

        if request.method != "GET" or response.status_code >= 400:
            return response

        slug = _service_slug_from_path(request.url.path)
        if slug is None:
            return response

        store = get_bigquery_api_store()
        tracking_task = BackgroundTask(
            store.track_service_detail_view,
            service_key=slug,
            request_path=request.url.path,
            request_method=request.method,
            user_agent=request.headers.get("user-agent"),
            referer=request.headers.get("referer"),
            client_ip=_resolve_client_ip(request),
        )
        _append_background_task(response, tracking_task)
        return response

import json
from typing import Any, Final

import httpx

from is_it_down.core.models import ServiceStatus

_STATUSPAGE_DEGRADED: Final[set[str]] = {"minor", "major"}
_STATUSPAGE_DOWN: Final[set[str]] = {"critical", "maintenance"}


def response_latency_ms(response: httpx.Response) -> int:
    return int(response.elapsed.total_seconds() * 1000)


def status_from_http(response: httpx.Response) -> ServiceStatus:
    if response.status_code >= 500:
        return "down"
    if response.status_code >= 400:
        return "degraded"
    return "up"


def apply_statuspage_indicator(base_status: ServiceStatus, indicator: str | None) -> ServiceStatus:
    if indicator in _STATUSPAGE_DOWN:
        return "down"
    if indicator in _STATUSPAGE_DEGRADED:
        return "degraded"
    return base_status


def _truncated_text(value: str, *, max_chars: int) -> tuple[str, bool]:
    if len(value) <= max_chars:
        return value, False
    return value[:max_chars], True


def build_response_debug_blob(
    response: httpx.Response,
    *,
    body_char_limit: int = 1000,
) -> dict[str, Any]:
    debug: dict[str, Any] = {
        "status_code": response.status_code,
        "reason_phrase": response.reason_phrase,
        "url": str(response.request.url) if response.request is not None else None,
        "content_type": response.headers.get("content-type", ""),
    }

    try:
        body = response.text
    except Exception as exc:  # pragma: no cover - defensive path
        debug["body_read_error"] = str(exc)
        return debug

    if not body:
        debug["body_preview"] = ""
        return debug

    body_preview, body_truncated = _truncated_text(body, max_chars=body_char_limit)
    debug["body_preview"] = body_preview
    debug["body_truncated"] = body_truncated

    content_type = debug["content_type"] or ""
    if "json" in content_type.lower():
        try:
            payload = response.json()
            payload_text = json.dumps(payload, sort_keys=True)
            json_preview, json_truncated = _truncated_text(payload_text, max_chars=body_char_limit)
            debug["json_preview"] = json_preview
            debug["json_truncated"] = json_truncated
        except Exception:
            pass

    return debug


def add_non_up_debug_metadata(
    *,
    metadata: dict[str, Any],
    status: ServiceStatus,
    response: httpx.Response,
    body_char_limit: int = 1000,
) -> dict[str, Any]:
    if status == "up":
        return metadata
    metadata.setdefault(
        "debug",
        build_response_debug_blob(response, body_char_limit=body_char_limit),
    )
    return metadata

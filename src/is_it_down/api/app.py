import uvicorn
from fastapi import FastAPI

from is_it_down.api.routes.incidents import router as incidents_router
from is_it_down.api.routes.services import router as services_router
from is_it_down.api.routes.stream import router as stream_router
from is_it_down.api.service_tracking_middleware import register_service_detail_tracking_middleware
from is_it_down.logging import configure_logging
from is_it_down.settings import get_settings


def create_app() -> FastAPI:
    app = FastAPI(title="is-it-down", version="0.1.0")
    register_service_detail_tracking_middleware(app)

    @app.get("/healthz", tags=["internal"])
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(services_router)
    app.include_router(incidents_router)
    app.include_router(stream_router)

    return app


app = create_app()


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    uvicorn.run(
        "is_it_down.api.app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.env == "local",
        factory=False,
    )

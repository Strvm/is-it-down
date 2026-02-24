import asyncio
import json
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from is_it_down.db.models import ServiceSnapshot
from is_it_down.db.session import get_sessionmaker

router = APIRouter(prefix="/v1", tags=["stream"])


def _snapshot_to_event(snapshot: ServiceSnapshot) -> dict[str, Any]:
    return {
        "snapshot_id": snapshot.id,
        "service_id": snapshot.service_id,
        "observed_at": snapshot.observed_at.isoformat(),
        "status": snapshot.status,
        "raw_score": snapshot.raw_score,
        "effective_score": snapshot.effective_score,
        "dependency_impacted": snapshot.dependency_impacted,
        "attribution_confidence": snapshot.attribution_confidence,
        "probable_root_service_id": snapshot.probable_root_service_id,
    }


@router.get("/stream")
async def stream_updates() -> StreamingResponse:
    async def event_generator() -> Any:
        session_factory = get_sessionmaker()
        last_id = 0

        async with session_factory() as session:
            max_seen = await session.scalar(
                select(ServiceSnapshot.id).order_by(ServiceSnapshot.id.desc()).limit(1)
            )
            if max_seen:
                last_id = max_seen

        while True:
            async with session_factory() as session:
                snapshots = (
                    await session.scalars(
                        select(ServiceSnapshot)
                        .where(ServiceSnapshot.id > last_id)
                        .order_by(ServiceSnapshot.id.asc())
                        .limit(200)
                    )
                ).all()

            if snapshots:
                for snapshot in snapshots:
                    last_id = snapshot.id
                    payload = json.dumps(_snapshot_to_event(snapshot))
                    yield f"event: snapshot\\ndata: {payload}\\n\\n"
            else:
                heartbeat = json.dumps({"ts": datetime.now(UTC).isoformat()})
                yield f": heartbeat {heartbeat}\\n\\n"

            await asyncio.sleep(2)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

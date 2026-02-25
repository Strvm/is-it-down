"""Provide functionality for `is_it_down.api.routes.stream`."""

import asyncio
import json
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from is_it_down.api.bigquery_store import SnapshotEvent, get_bigquery_api_store

router = APIRouter(prefix="/v1", tags=["stream"])


def _snapshot_to_event(snapshot: SnapshotEvent) -> dict[str, Any]:
    """Snapshot to event.
    
    Args:
        snapshot: The snapshot value.
    
    Returns:
        The resulting value.
    """
    return {
        "snapshot_id": snapshot.snapshot_id,
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
    """Stream updates.
    
    Returns:
        The resulting value.
    """
    async def event_generator() -> Any:
        """Event generator.
        
        Yields:
            The values produced by the generator.
        """
        store = get_bigquery_api_store()
        last_seen = await store.latest_observed_at()
        if last_seen is None:
            last_seen = datetime.now(UTC)

        while True:
            snapshots = await store.snapshot_events_since(last_seen, limit=200)

            if snapshots:
                for snapshot in snapshots:
                    if snapshot.observed_at > last_seen:
                        last_seen = snapshot.observed_at
                    payload = json.dumps(_snapshot_to_event(snapshot))
                    yield f"event: snapshot\\ndata: {payload}\\n\\n"
            else:
                heartbeat = json.dumps({"ts": datetime.now(UTC).isoformat()})
                yield f": heartbeat {heartbeat}\\n\\n"

            await asyncio.sleep(2)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from is_it_down.api.deps import db_session_dep
from is_it_down.api.schemas import IncidentSummary
from is_it_down.db.models import Incident

router = APIRouter(prefix="/v1/incidents", tags=["incidents"])


@router.get("", response_model=list[IncidentSummary])
async def list_incidents(
    status: str = Query(default="open", pattern=r"^(open|resolved|all)$"),
    session: AsyncSession = Depends(db_session_dep),
) -> list[IncidentSummary]:
    stmt = select(Incident)
    if status != "all":
        stmt = stmt.where(Incident.status == status)

    stmt = stmt.order_by(Incident.started_at.desc()).limit(500)
    incidents = (await session.scalars(stmt)).all()

    return [
        IncidentSummary(
            incident_id=incident.id,
            service_id=incident.service_id,
            status=incident.status,
            started_at=incident.started_at,
            resolved_at=incident.resolved_at,
            peak_severity=incident.peak_severity,
            probable_root_service_id=incident.probable_root_service_id,
            confidence=incident.confidence,
            summary=incident.summary,
        )
        for incident in incidents
    ]

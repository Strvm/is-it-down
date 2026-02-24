from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from is_it_down.api.deps import db_session_dep
from is_it_down.api.schemas import CheckRunSummary, ServiceDetail, ServiceSummary, SnapshotPoint
from is_it_down.core.time import parse_history_window
from is_it_down.db.models import CheckRun, Service, ServiceCheck, ServiceSnapshot

router = APIRouter(prefix="/v1/services", tags=["services"])


@router.get("", response_model=list[ServiceSummary])
async def list_services(session: AsyncSession = Depends(db_session_dep)) -> list[ServiceSummary]:
    latest_snapshots = (
        select(
            ServiceSnapshot.service_id.label("service_id"),
            ServiceSnapshot.status.label("status"),
            ServiceSnapshot.raw_score.label("raw_score"),
            ServiceSnapshot.effective_score.label("effective_score"),
            ServiceSnapshot.observed_at.label("observed_at"),
            ServiceSnapshot.dependency_impacted.label("dependency_impacted"),
            ServiceSnapshot.attribution_confidence.label("attribution_confidence"),
            ServiceSnapshot.probable_root_service_id.label("probable_root_service_id"),
            func.row_number()
            .over(partition_by=ServiceSnapshot.service_id, order_by=ServiceSnapshot.observed_at.desc())
            .label("row_num"),
        )
        .subquery()
    )

    stmt = (
        select(
            Service.id,
            Service.slug,
            Service.name,
            latest_snapshots.c.status,
            latest_snapshots.c.raw_score,
            latest_snapshots.c.effective_score,
            latest_snapshots.c.observed_at,
            latest_snapshots.c.dependency_impacted,
            latest_snapshots.c.attribution_confidence,
            latest_snapshots.c.probable_root_service_id,
        )
        .join(
            latest_snapshots,
            and_(latest_snapshots.c.service_id == Service.id, latest_snapshots.c.row_num == 1),
            isouter=True,
        )
        .where(Service.is_active.is_(True))
        .order_by(Service.slug.asc())
    )

    rows = (await session.execute(stmt)).all()
    now = datetime.now(UTC)
    summaries: list[ServiceSummary] = []
    for row in rows:
        status = row.status or "up"
        raw_score = float(row.raw_score or 100.0)
        effective_score = float(row.effective_score or raw_score)
        observed_at = row.observed_at or now

        summaries.append(
            ServiceSummary(
                service_id=row.id,
                slug=row.slug,
                name=row.name,
                status=status,
                raw_score=raw_score,
                effective_score=effective_score,
                observed_at=observed_at,
                dependency_impacted=bool(row.dependency_impacted or False),
                attribution_confidence=float(row.attribution_confidence or 0.0),
                probable_root_service_id=row.probable_root_service_id,
            )
        )

    return summaries


@router.get("/{slug}", response_model=ServiceDetail)
async def get_service_detail(slug: str, session: AsyncSession = Depends(db_session_dep)) -> ServiceDetail:
    service = await session.scalar(select(Service).where(Service.slug == slug, Service.is_active.is_(True)))
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")

    snapshot = await session.scalar(
        select(ServiceSnapshot)
        .where(ServiceSnapshot.service_id == service.id)
        .order_by(ServiceSnapshot.observed_at.desc())
        .limit(1)
    )

    if snapshot is None:
        fallback_snapshot = ServiceSummary(
            service_id=service.id,
            slug=service.slug,
            name=service.name,
            status="up",
            raw_score=100.0,
            effective_score=100.0,
            observed_at=datetime.now(UTC),
            dependency_impacted=False,
            attribution_confidence=0.0,
            probable_root_service_id=None,
        )
    else:
        fallback_snapshot = ServiceSummary(
            service_id=service.id,
            slug=service.slug,
            name=service.name,
            status=snapshot.status,
            raw_score=snapshot.raw_score,
            effective_score=snapshot.effective_score,
            observed_at=snapshot.observed_at,
            dependency_impacted=snapshot.dependency_impacted,
            attribution_confidence=snapshot.attribution_confidence,
            probable_root_service_id=snapshot.probable_root_service_id,
        )

    latest_runs = (
        select(
            CheckRun.check_id.label("check_id"),
            CheckRun.status.label("status"),
            CheckRun.observed_at.label("observed_at"),
            CheckRun.latency_ms.label("latency_ms"),
            CheckRun.http_status.label("http_status"),
            CheckRun.error_code.label("error_code"),
            CheckRun.error_message.label("error_message"),
            CheckRun.metadata_json.label("metadata_json"),
            func.row_number()
            .over(partition_by=CheckRun.check_id, order_by=CheckRun.observed_at.desc())
            .label("row_num"),
        )
        .where(CheckRun.service_id == service.id)
        .subquery()
    )

    runs_stmt = (
        select(
            ServiceCheck.check_key,
            latest_runs.c.status,
            latest_runs.c.observed_at,
            latest_runs.c.latency_ms,
            latest_runs.c.http_status,
            latest_runs.c.error_code,
            latest_runs.c.error_message,
            latest_runs.c.metadata_json,
        )
        .outerjoin(
            latest_runs,
            and_(latest_runs.c.check_id == ServiceCheck.id, latest_runs.c.row_num == 1),
        )
        .where(ServiceCheck.service_id == service.id)
        .where(ServiceCheck.enabled.is_(True))
    )

    runs = (await session.execute(runs_stmt)).all()

    latest_checks: list[CheckRunSummary] = []
    for row in runs:
        if row.status is None or row.observed_at is None:
            continue
        latest_checks.append(
            CheckRunSummary(
                check_key=row.check_key,
                status=row.status,
                observed_at=row.observed_at,
                latency_ms=row.latency_ms,
                http_status=row.http_status,
                error_code=row.error_code,
                error_message=row.error_message,
                metadata=row.metadata_json or {},
            )
        )

    return ServiceDetail(
        service_id=service.id,
        slug=service.slug,
        name=service.name,
        description=service.description,
        snapshot=fallback_snapshot,
        latest_checks=latest_checks,
    )


@router.get("/{slug}/history", response_model=list[SnapshotPoint])
async def get_service_history(
    slug: str,
    window: str = Query(default="24h", pattern=r"^[1-9][0-9]*[hdm]$"),
    session: AsyncSession = Depends(db_session_dep),
) -> list[SnapshotPoint]:
    service = await session.scalar(select(Service).where(Service.slug == slug, Service.is_active.is_(True)))
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")

    cutoff = datetime.now(UTC) - parse_history_window(window)

    stmt = (
        select(ServiceSnapshot)
        .where(ServiceSnapshot.service_id == service.id)
        .where(ServiceSnapshot.observed_at >= cutoff)
        .order_by(ServiceSnapshot.observed_at.asc())
    )

    snapshots = (await session.scalars(stmt)).all()
    return [
        SnapshotPoint(
            observed_at=snapshot.observed_at,
            status=snapshot.status,
            raw_score=snapshot.raw_score,
            effective_score=snapshot.effective_score,
            dependency_impacted=snapshot.dependency_impacted,
        )
        for snapshot in snapshots
    ]

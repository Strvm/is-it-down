"""Provide functionality for `is_it_down.worker.service`."""

import asyncio
from collections import defaultdict
from datetime import UTC, datetime
from socket import gethostname
from uuid import uuid4

import httpx
import structlog
from pydantic import BaseModel
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from is_it_down.checkers.registry import registry
from is_it_down.core.attribution import attribute_dependency
from is_it_down.core.models import CheckResult, DependencySignal
from is_it_down.core.scoring import status_from_score, weighted_service_score
from is_it_down.db.models import (
    CheckRun,
    Incident,
    IncidentEvent,
    ServiceCheck,
    ServiceDependency,
    ServiceSnapshot,
)
from is_it_down.db.session import get_sessionmaker
from is_it_down.logging import configure_logging
from is_it_down.settings import get_settings
from is_it_down.worker.queue import claim_jobs, mark_job_done, mark_job_retry_or_fail

logger = structlog.get_logger(__name__)


class ClaimedJob(BaseModel):
    """Represent `ClaimedJob`."""

    id: int
    service_id: int
    check_id: int


def _severity_rank(status: str) -> int:
    """Severity rank.
    
    Args:
        status: The status value.
    
    Returns:
        The resulting value.
    """
    mapping = {"up": 0, "degraded": 1, "down": 2}
    return mapping.get(status, 0)


async def _latest_service_check_results(
    session: AsyncSession,
    service_id: int,
) -> tuple[list[CheckResult], dict[str, float]]:
    """Latest service check results.
    
    Args:
        session: The session value.
        service_id: The service id value.
    
    Returns:
        The resulting value.
    """
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
        .where(CheckRun.service_id == service_id)
        .subquery()
    )

    stmt = (
        select(
            ServiceCheck.check_key,
            ServiceCheck.weight,
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
        .where(ServiceCheck.service_id == service_id)
        .where(ServiceCheck.enabled.is_(True))
    )

    rows = (await session.execute(stmt)).all()

    results: list[CheckResult] = []
    weights_by_check: dict[str, float] = {}
    for row in rows:
        check_key = row.check_key
        weights_by_check[check_key] = row.weight

        if row.status is None or row.observed_at is None:
            continue

        results.append(
            CheckResult(
                check_key=check_key,
                status=row.status,
                observed_at=row.observed_at,
                latency_ms=row.latency_ms,
                http_status=row.http_status,
                error_code=row.error_code,
                error_message=row.error_message,
                metadata=row.metadata_json or {},
            )
        )

    return results, weights_by_check


async def _dependency_signals(session: AsyncSession, service_id: int) -> list[DependencySignal]:
    """Dependency signals.
    
    Args:
        session: The session value.
        service_id: The service id value.
    
    Returns:
        The resulting value.
    """
    latest_snapshots = select(
        ServiceSnapshot.service_id.label("service_id"),
        ServiceSnapshot.status.label("status"),
        func.row_number()
        .over(partition_by=ServiceSnapshot.service_id, order_by=ServiceSnapshot.observed_at.desc())
        .label("row_num"),
    ).subquery()

    stmt = (
        select(
            ServiceDependency.depends_on_service_id,
            ServiceDependency.dependency_type,
            ServiceDependency.weight,
            latest_snapshots.c.status,
        )
        .outerjoin(
            latest_snapshots,
            and_(
                latest_snapshots.c.service_id == ServiceDependency.depends_on_service_id,
                latest_snapshots.c.row_num == 1,
            ),
        )
        .where(ServiceDependency.service_id == service_id)
    )

    rows = (await session.execute(stmt)).all()
    signals: list[DependencySignal] = []
    for row in rows:
        if row.status is None:
            continue
        signals.append(
            DependencySignal(
                dependency_service_id=row.depends_on_service_id,
                dependency_status=row.status,
                dependency_type=row.dependency_type,
                weight=row.weight,
            )
        )

    return signals


async def _sync_incident_state(
    session: AsyncSession,
    *,
    service_id: int,
    status: str,
    observed_at: datetime,
    probable_root_service_id: int | None,
    confidence: float,
) -> None:
    """Sync incident state.
    
    Args:
        session: The session value.
        service_id: The service id value.
        status: The status value.
        observed_at: The observed at value.
        probable_root_service_id: The probable root service id value.
        confidence: The confidence value.
    """
    open_incident_stmt = (
        select(Incident)
        .where(Incident.service_id == service_id)
        .where(Incident.status == "open")
        .order_by(Incident.started_at.desc())
        .limit(1)
    )
    open_incident = await session.scalar(open_incident_stmt)

    if status == "up":
        if open_incident is None:
            return

        open_incident.status = "resolved"
        open_incident.resolved_at = observed_at
        session.add(
            IncidentEvent(
                incident_id=open_incident.id,
                event_type="resolved",
                payload_json={"resolved_at": observed_at.isoformat()},
            )
        )
        return

    if open_incident is None:
        incident = Incident(
            service_id=service_id,
            status="open",
            started_at=observed_at,
            peak_severity=status,
            probable_root_service_id=probable_root_service_id,
            confidence=confidence,
            summary=f"Service entered {status} state",
        )
        session.add(incident)
        await session.flush()
        session.add(
            IncidentEvent(
                incident_id=incident.id,
                event_type="opened",
                payload_json={"status": status, "confidence": confidence},
            )
        )
        return

    if _severity_rank(status) > _severity_rank(open_incident.peak_severity):
        open_incident.peak_severity = status

    open_incident.probable_root_service_id = probable_root_service_id
    open_incident.confidence = confidence

    session.add(
        IncidentEvent(
            incident_id=open_incident.id,
            event_type="updated",
            payload_json={"status": status, "confidence": confidence},
        )
    )


async def _recompute_service_snapshot(
    session: AsyncSession,
    *,
    service_id: int,
    observed_at: datetime,
) -> None:
    """Recompute service snapshot.
    
    Args:
        session: The session value.
        service_id: The service id value.
        observed_at: The observed at value.
    """
    check_results, weights_by_check = await _latest_service_check_results(session, service_id)

    raw_score = weighted_service_score(check_results, weights_by_check)
    status = status_from_score(raw_score)

    dependency_signals = await _dependency_signals(session, service_id)
    attribution = attribute_dependency(status, dependency_signals)

    effective_score = raw_score
    if attribution.dependency_impacted:
        effective_score = min(
            100.0,
            raw_score + (100.0 - raw_score) * (0.15 + 0.35 * attribution.attribution_confidence),
        )

    snapshot = ServiceSnapshot(
        service_id=service_id,
        observed_at=observed_at,
        raw_score=raw_score,
        effective_score=round(effective_score, 2),
        status=status,
        dependency_impacted=attribution.dependency_impacted,
        attribution_confidence=attribution.attribution_confidence,
        probable_root_service_id=attribution.probable_root_service_id,
    )
    session.add(snapshot)

    await _sync_incident_state(
        session,
        service_id=service_id,
        status=status,
        observed_at=observed_at,
        probable_root_service_id=attribution.probable_root_service_id,
        confidence=attribution.attribution_confidence,
    )


async def _process_claimed_job(
    claimed_job: ClaimedJob,
    *,
    session_factory: async_sessionmaker[AsyncSession],
    client: httpx.AsyncClient,
    per_service_semaphores: dict[int, asyncio.Semaphore],
    global_semaphore: asyncio.Semaphore,
) -> None:
    """Process claimed job.
    
    Args:
        claimed_job: The claimed job value.
        session_factory: The session factory value.
        client: The client value.
        per_service_semaphores: The per service semaphores value.
        global_semaphore: The global semaphore value.
    """
    service_semaphore = per_service_semaphores[claimed_job.service_id]

    async with global_semaphore, service_semaphore:
        try:
            async with session_factory() as session:
                check = await session.get(ServiceCheck, claimed_job.check_id)
                if check is None or not check.enabled:
                    await mark_job_done(session, claimed_job.id)
                    await session.commit()
                    return

                check_cls = registry.get(check.class_path)
                checker = check_cls()
                checker.timeout_seconds = check.timeout_seconds
                checker.weight = check.weight

                result = await checker.execute(client)

                session.add(
                    CheckRun(
                        job_id=claimed_job.id,
                        service_id=claimed_job.service_id,
                        check_id=claimed_job.check_id,
                        status=result.status,
                        latency_ms=result.latency_ms,
                        http_status=result.http_status,
                        error_code=result.error_code,
                        error_message=result.error_message,
                        metadata_json=result.metadata,
                        observed_at=result.observed_at,
                    )
                )

                await _recompute_service_snapshot(
                    session,
                    service_id=claimed_job.service_id,
                    observed_at=result.observed_at,
                )

                await mark_job_done(session, claimed_job.id)
                await session.commit()

                logger.info(
                    "worker.job_processed",
                    job_id=claimed_job.id,
                    service_id=claimed_job.service_id,
                    check_id=claimed_job.check_id,
                    result_status=result.status,
                )
        except Exception:
            logger.exception(
                "worker.job_failed",
                job_id=claimed_job.id,
                service_id=claimed_job.service_id,
                check_id=claimed_job.check_id,
            )
            async with session_factory() as retry_session:
                await mark_job_retry_or_fail(
                    retry_session,
                    job_id=claimed_job.id,
                    now=datetime.now(UTC),
                )
                await retry_session.commit()


def _default_worker_id() -> str:
    """Default worker id.
    
    Returns:
        The resulting value.
    """
    return f"{gethostname()}-{uuid4().hex[:12]}"


async def run_worker_batch(
    session_factory: async_sessionmaker[AsyncSession] | None = None,
    *,
    worker_id: str | None = None,
    client: httpx.AsyncClient | None = None,
    batch_size: int | None = None,
    lease_seconds: int | None = None,
    per_service_semaphores: dict[int, asyncio.Semaphore] | None = None,
    global_semaphore: asyncio.Semaphore | None = None,
) -> int:
    """Run worker batch.
    
    Args:
        session_factory: The session factory value.
        worker_id: The worker id value.
        client: The client value.
        batch_size: The batch size value.
        lease_seconds: The lease seconds value.
        per_service_semaphores: The per service semaphores value.
        global_semaphore: The global semaphore value.
    
    Returns:
        The resulting value.
    """
    settings = get_settings()

    if session_factory is None:
        session_factory = get_sessionmaker()
    if worker_id is None:
        worker_id = _default_worker_id()
    if batch_size is None:
        batch_size = settings.worker_batch_size
    if lease_seconds is None:
        lease_seconds = settings.worker_lease_seconds
    if global_semaphore is None:
        global_semaphore = asyncio.Semaphore(settings.worker_concurrency)
    if per_service_semaphores is None:
        per_service_semaphores = defaultdict(lambda: asyncio.Semaphore(settings.per_service_concurrency))

    own_client = client is None
    if client is None:
        timeout = httpx.Timeout(settings.default_http_timeout_seconds)
        headers = {"User-Agent": settings.user_agent}
        client = httpx.AsyncClient(timeout=timeout, headers=headers, follow_redirects=True)

    try:
        now = datetime.now(UTC)
        async with session_factory() as session:
            leased = await claim_jobs(
                session,
                now=now,
                worker_id=worker_id,
                batch_size=batch_size,
                lease_seconds=lease_seconds,
            )
            claimed_jobs = [ClaimedJob(id=job.id, service_id=job.service_id, check_id=job.check_id) for job in leased]
            await session.commit()

        if not claimed_jobs:
            return 0

        await asyncio.gather(
            *[
                _process_claimed_job(
                    claimed_job,
                    session_factory=session_factory,
                    client=client,
                    per_service_semaphores=per_service_semaphores,
                    global_semaphore=global_semaphore,
                )
                for claimed_job in claimed_jobs
            ]
        )
        return len(claimed_jobs)
    finally:
        if own_client:
            await client.aclose()


async def run_worker_loop(session_factory: async_sessionmaker[AsyncSession] | None = None) -> None:
    """Run worker loop.
    
    Args:
        session_factory: The session factory value.
    """
    settings = get_settings()
    configure_logging(settings.log_level)

    worker_id = _default_worker_id()
    logger.info(
        "worker.starting",
        worker_id=worker_id,
        batch_size=settings.worker_batch_size,
        concurrency=settings.worker_concurrency,
    )

    if session_factory is None:
        session_factory = get_sessionmaker()

    global_semaphore = asyncio.Semaphore(settings.worker_concurrency)
    per_service_semaphores: dict[int, asyncio.Semaphore] = defaultdict(
        lambda: asyncio.Semaphore(settings.per_service_concurrency)
    )

    timeout = httpx.Timeout(settings.default_http_timeout_seconds)
    headers = {"User-Agent": settings.user_agent}

    async with httpx.AsyncClient(timeout=timeout, headers=headers, follow_redirects=True) as client:
        while True:
            processed_count = await run_worker_batch(
                session_factory=session_factory,
                worker_id=worker_id,
                client=client,
                batch_size=settings.worker_batch_size,
                lease_seconds=settings.worker_lease_seconds,
                per_service_semaphores=per_service_semaphores,
                global_semaphore=global_semaphore,
            )

            if processed_count == 0:
                await asyncio.sleep(settings.worker_poll_seconds)

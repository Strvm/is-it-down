import random
from datetime import datetime, timedelta

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from is_it_down.db.models import CheckJob


def retry_delay_seconds(attempt: int) -> float:
    capped = min(60, 2 ** max(0, attempt - 1))
    return capped + random.uniform(0, 0.5)


async def claim_jobs(
    session: AsyncSession,
    *,
    now: datetime,
    worker_id: str,
    batch_size: int,
    lease_seconds: int,
) -> list[CheckJob]:
    claimable = or_(
        CheckJob.status == "queued",
        and_(CheckJob.status == "leased", CheckJob.lease_expires_at.is_not(None), CheckJob.lease_expires_at < now),
    )

    stmt = (
        select(CheckJob)
        .where(claimable)
        .where(CheckJob.scheduled_for <= now)
        .order_by(CheckJob.scheduled_for.asc())
        .limit(batch_size)
        .with_for_update(skip_locked=True)
    )

    jobs = (await session.scalars(stmt)).all()
    if not jobs:
        return []

    lease_expires_at = now + timedelta(seconds=lease_seconds)
    for job in jobs:
        job.status = "leased"
        job.worker_id = worker_id
        job.lease_expires_at = lease_expires_at
        job.attempt += 1

    return jobs


async def mark_job_done(session: AsyncSession, job_id: int) -> None:
    job = await session.get(CheckJob, job_id)
    if job is None:
        return

    job.status = "done"
    job.lease_expires_at = None


async def mark_job_retry_or_fail(
    session: AsyncSession,
    *,
    job_id: int,
    now: datetime,
) -> None:
    job = await session.get(CheckJob, job_id)
    if job is None:
        return

    if job.attempt >= job.max_attempts:
        job.status = "failed"
        job.lease_expires_at = None
        return

    job.status = "queued"
    job.worker_id = None
    job.lease_expires_at = None
    job.scheduled_for = now + timedelta(seconds=retry_delay_seconds(job.attempt))

"""Provide functionality for `is_it_down.scheduler.service`."""

import asyncio
from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from is_it_down.db.models import CheckJob, Service, ServiceCheck
from is_it_down.db.session import get_sessionmaker
from is_it_down.logging import configure_logging
from is_it_down.settings import get_settings

logger = structlog.get_logger(__name__)


def _idempotency_key(check_id: int, scheduled_for: datetime) -> str:
    """Idempotency key.
    
    Args:
        check_id: The check id value.
        scheduled_for: The scheduled for value.
    
    Returns:
        The resulting value.
    """
    return f"{check_id}:{int(scheduled_for.timestamp())}"


def _compute_next_due(previous_due: datetime, now: datetime, interval_seconds: int) -> datetime:
    """Compute next due.
    
    Args:
        previous_due: The previous due value.
        now: The now value.
        interval_seconds: The interval seconds value.
    
    Returns:
        The resulting value.
    """
    next_due = previous_due
    step = timedelta(seconds=interval_seconds)
    while next_due <= now:
        next_due += step
    return next_due


async def enqueue_due_checks(
    session: AsyncSession,
    *,
    now: datetime,
    max_attempts: int,
    batch_size: int,
) -> int:
    """Enqueue due checks.
    
    Args:
        session: The session value.
        now: The now value.
        max_attempts: The max attempts value.
        batch_size: The batch size value.
    
    Returns:
        The resulting value.
    """
    due_stmt = (
        select(ServiceCheck)
        .join(Service, Service.id == ServiceCheck.service_id)
        .where(Service.is_active.is_(True))
        .where(ServiceCheck.enabled.is_(True))
        .where(ServiceCheck.next_due_at <= now)
        .order_by(ServiceCheck.next_due_at.asc())
        .limit(batch_size)
        .with_for_update(skip_locked=True)
    )

    due_checks = (await session.scalars(due_stmt)).all()
    if not due_checks:
        return 0

    scheduled_count = 0
    for check in due_checks:
        scheduled_for = check.next_due_at
        insert_stmt = (
            insert(CheckJob)
            .values(
                service_id=check.service_id,
                check_id=check.id,
                scheduled_for=scheduled_for,
                status="queued",
                attempt=0,
                max_attempts=max_attempts,
                idempotency_key=_idempotency_key(check.id, scheduled_for),
            )
            .on_conflict_do_nothing(index_elements=["idempotency_key"])
        )
        result = await session.execute(insert_stmt)
        scheduled_count += result.rowcount or 0

        check.next_due_at = _compute_next_due(
            previous_due=scheduled_for,
            now=now,
            interval_seconds=check.interval_seconds,
        )

    return scheduled_count


async def run_scheduler_loop(session_factory: async_sessionmaker[AsyncSession] | None = None) -> None:
    """Run scheduler loop.
    
    Args:
        session_factory: The session factory value.
    """
    settings = get_settings()
    configure_logging(settings.log_level)

    logger.info(
        "scheduler.starting",
        tick_seconds=settings.scheduler_tick_seconds,
        batch_size=settings.scheduler_batch_size,
    )

    if session_factory is None:
        session_factory = get_sessionmaker()

    while True:
        loop_started = datetime.now(UTC)
        try:
            async with session_factory() as session:
                queued = await enqueue_due_checks(
                    session,
                    now=loop_started,
                    max_attempts=settings.worker_max_attempts,
                    batch_size=settings.scheduler_batch_size,
                )
                await session.commit()

            logger.info("scheduler.tick", queued=queued)
        except Exception:
            logger.exception("scheduler.tick_failed")

        elapsed = (datetime.now(UTC) - loop_started).total_seconds()
        sleep_for = max(0.1, settings.scheduler_tick_seconds - elapsed)
        await asyncio.sleep(sleep_for)

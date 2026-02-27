"""Provide functionality for `is_it_down.scripts.run_scheduled_checks`."""

import argparse
import asyncio
import json
import os
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import structlog
from google.cloud import bigquery

from is_it_down.api.cache_warm import warm_api_cache
from is_it_down.checkers.base import BaseServiceChecker, ServiceRunResult
from is_it_down.checkers.proxy import clear_proxy_resolution_cache
from is_it_down.logging import configure_logging
from is_it_down.scripts.checker_runtime import (
    discover_service_checkers,
    iter_service_checker_runs,
    resolve_service_checker_targets,
    service_checker_path,
)
from is_it_down.settings import get_settings

logger = structlog.get_logger(__name__)
_CLOUD_RUN_TASK_INDEX_ENV = "CLOUD_RUN_TASK_INDEX"
_CLOUD_RUN_TASK_COUNT_ENV = "CLOUD_RUN_TASK_COUNT"


def _build_parser() -> argparse.ArgumentParser:
    """Build parser.
    
    Returns:
        The resulting value.
    """
    parser = argparse.ArgumentParser(
        prog="is-it-down-run-scheduled-checks",
        description="Run service checkers and write results to BigQuery.",
    )
    parser.add_argument(
        "targets",
        nargs="*",
        help=(
            "Optional service checker key (for example 'cloudflare') or class path "
            "(for example 'is_it_down.checkers.services.cloudflare.CloudflareServiceChecker'). "
            "If omitted, all discovered service checkers are executed."
        ),
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if any check result is not 'up'.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Execute checks and log summary without inserting rows into BigQuery.",
    )
    parser.add_argument(
        "--default-proxy-url",
        default=None,
        help=(
            "Optional direct proxy URL used when checks set proxy_setting='default'. "
            "Useful for local runs without Secret Manager access."
        ),
    )
    return parser


def _resolve_cloud_run_task_metadata() -> tuple[int, int] | None:
    """Resolve Cloud Run task metadata.

    Returns:
        `(task_index, task_count)` when available and valid, otherwise `None`.
    """
    task_index_value = os.getenv(_CLOUD_RUN_TASK_INDEX_ENV)
    task_count_value = os.getenv(_CLOUD_RUN_TASK_COUNT_ENV)
    if task_index_value is None and task_count_value is None:
        return None

    if task_index_value is None or task_count_value is None:
        logger.warning(
            "checker_job.task_sharding_disabled_missing_task_metadata",
            cloud_run_task_index=task_index_value,
            cloud_run_task_count=task_count_value,
        )
        return None

    try:
        task_index = int(task_index_value)
        task_count = int(task_count_value)
    except ValueError:
        logger.warning(
            "checker_job.task_sharding_disabled_invalid_task_metadata",
            cloud_run_task_index=task_index_value,
            cloud_run_task_count=task_count_value,
        )
        return None

    if task_count <= 0:
        logger.warning(
            "checker_job.task_sharding_disabled_invalid_task_count",
            cloud_run_task_index=task_index,
            cloud_run_task_count=task_count,
        )
        return None

    if task_index < 0 or task_index >= task_count:
        logger.warning(
            "checker_job.task_sharding_disabled_invalid_task_index",
            cloud_run_task_index=task_index,
            cloud_run_task_count=task_count,
        )
        return None

    return task_index, task_count


def _shard_service_checker_classes(
    service_checker_classes: Sequence[type[BaseServiceChecker]],
    *,
    task_index: int,
    task_count: int,
) -> list[type[BaseServiceChecker]]:
    """Shard service checker classes for a Cloud Run Job task.

    Args:
        service_checker_classes: All checker classes sorted in deterministic order.
        task_index: The zero-based Cloud Run Job task index.
        task_count: The total number of Cloud Run Job tasks for this execution.

    Returns:
        The checker classes assigned to this task.

    Raises:
        ValueError: If `task_count` is not positive.
    """
    if task_count <= 0:
        raise ValueError("task_count must be greater than 0.")

    total_checker_count = len(service_checker_classes)
    base_shard_size = total_checker_count // task_count
    remainder = total_checker_count % task_count

    # Distribute the remainder one-by-one to the first tasks for an even split.
    shard_size = base_shard_size + (1 if task_index < remainder else 0)
    start = task_index * base_shard_size + min(task_index, remainder)
    end = start + shard_size
    return list(service_checker_classes[start:end])


def _resolve_service_checker_classes(
    targets: list[str],
    *,
    task_metadata: tuple[int, int] | None = None,
) -> list[type[BaseServiceChecker]]:
    """Resolve service checker classes.
    
    Args:
        targets: The targets value.
        task_metadata: Optional Cloud Run Job task metadata tuple.
    
    Returns:
        The resulting value.
    """
    if targets:
        return resolve_service_checker_targets(targets)

    discovered = discover_service_checkers()
    service_checker_classes = [discovered[key] for key in sorted(discovered)]
    if task_metadata is None:
        return service_checker_classes

    task_index, task_count = task_metadata
    sharded_service_checker_classes = _shard_service_checker_classes(
        service_checker_classes,
        task_index=task_index,
        task_count=task_count,
    )

    logger.info(
        "checker_job.task_shard_assigned",
        cloud_run_task_index=task_index,
        cloud_run_task_count=task_count,
        total_checker_count=len(service_checker_classes),
        assigned_checker_count=len(sharded_service_checker_classes),
    )
    return sharded_service_checker_classes


def _build_bigquery_rows_for_run(
    service_checker_cls: type[BaseServiceChecker],
    run_result: ServiceRunResult,
    *,
    run_id: str,
    execution_id: str | None,
    ingested_at: datetime,
) -> list[dict[str, Any]]:
    """Build bigquery rows.
    
    Args:
        service_checker_cls: The service checker cls value.
        run_result: The run result value.
        run_id: The run id value.
        execution_id: The execution id value.
        ingested_at: The ingested at value.
    
    Returns:
        The resulting value.
    """
    ingested_at_iso = ingested_at.isoformat()
    checker_class = service_checker_path(service_checker_cls)
    rows: list[dict[str, Any]] = []
    for check_result in run_result.check_results:
        metadata_json: str | None = None
        if check_result.metadata:
            metadata_json = json.dumps(check_result.metadata, sort_keys=True)

        rows.append(
            {
                "run_id": run_id,
                "execution_id": execution_id,
                "service_key": run_result.service_key,
                "checker_class": checker_class,
                "check_key": check_result.check_key,
                "status": check_result.status,
                "observed_at": check_result.observed_at.isoformat(),
                "latency_ms": check_result.latency_ms,
                "http_status": check_result.http_status,
                "error_code": check_result.error_code,
                "error_message": check_result.error_message,
                "metadata_json": metadata_json,
                "ingested_at": ingested_at_iso,
            }
        )

    return rows


def _insert_rows(rows: list[dict[str, Any]]) -> None:
    """Insert rows.
    
    Args:
        rows: The rows value.
    
    Raises:
        RuntimeError: If an error occurs while executing this function.
    """
    if not rows:
        logger.info("checker_job.no_rows_to_insert")
        return

    settings = get_settings()
    client = bigquery.Client(project=settings.bigquery_project_id or None)
    project_id = settings.bigquery_project_id or client.project
    if not project_id:
        raise RuntimeError(
            "BigQuery project ID is required. Set IS_IT_DOWN_BIGQUERY_PROJECT_ID or use authenticated default project."
        )

    table_id = f"{project_id}.{settings.bigquery_dataset_id}.{settings.bigquery_table_id}"
    errors = client.insert_rows_json(table_id, rows)
    if errors:
        raise RuntimeError(f"BigQuery insert failed: {errors}")

    logger.info("checker_job.rows_inserted", table_id=table_id, row_count=len(rows))


async def _run_once(*, targets: list[str], strict: bool, dry_run: bool) -> None:
    """Run once.
    
    Args:
        targets: The targets value.
        strict: The strict value.
        dry_run: The dry run value.
    
    Raises:
        RuntimeError: If an error occurs while executing this function.
        SystemExit: If an error occurs while executing this function.
    """
    settings = get_settings()
    configure_logging(settings.log_level)

    task_metadata = _resolve_cloud_run_task_metadata()
    service_checker_classes = _resolve_service_checker_classes(targets, task_metadata=task_metadata)
    if not service_checker_classes:
        if task_metadata is not None and not targets:
            logger.info(
                "checker_job.no_assigned_checkers_for_task",
                cloud_run_task_index=task_metadata[0],
                cloud_run_task_count=task_metadata[1],
            )
            return
        raise RuntimeError("No service checkers discovered.")

    cloud_run_task_index: int | None = None
    cloud_run_task_count: int | None = None
    if task_metadata is not None:
        cloud_run_task_index, cloud_run_task_count = task_metadata

    logger.info(
        "checker_job.starting",
        checker_count=len(service_checker_classes),
        dry_run=dry_run,
        cloud_run_task_index=cloud_run_task_index,
        cloud_run_task_count=cloud_run_task_count,
    )

    run_id = uuid4().hex
    execution_id = os.getenv("CLOUD_RUN_EXECUTION")
    ingested_at = datetime.now(UTC)
    service_count = 0
    check_count = 0
    non_up_count = 0
    has_non_up_result = False
    insert_batch_size = max(1, settings.checker_insert_batch_size)
    row_buffer: list[dict[str, Any]] = []

    async for service_checker_cls, run_result in iter_service_checker_runs(
        service_checker_classes,
        concurrent=True,
        concurrency_limit=settings.checker_concurrency,
    ):
        service_count += 1

        checker_non_up_count = 0
        for check_result in run_result.check_results:
            check_count += 1
            if check_result.status != "up":
                checker_non_up_count += 1

        non_up_count += checker_non_up_count
        has_non_up_result = has_non_up_result or checker_non_up_count > 0

        if dry_run:
            continue

        row_buffer.extend(
            _build_bigquery_rows_for_run(
                service_checker_cls,
                run_result,
                run_id=run_id,
                execution_id=execution_id,
                ingested_at=ingested_at,
            )
        )
        if len(row_buffer) >= insert_batch_size:
            _insert_rows(row_buffer)
            row_buffer = []

    if not dry_run and row_buffer:
        _insert_rows(row_buffer)

    logger.info(
        "checker_job.completed",
        run_id=run_id,
        service_count=service_count,
        check_count=check_count,
        non_up_count=non_up_count,
    )

    if not dry_run:
        is_cloud_run_task_execution = task_metadata is not None
        should_warm_cache_for_execution_mode = (
            not is_cloud_run_task_execution or settings.api_cache_warm_on_cloud_run_checker_job
        )
        should_warm_cache = (
            should_warm_cache_for_execution_mode and (task_metadata is None or task_metadata[0] == 0)
        )

        if settings.api_cache_enabled and settings.api_cache_warm_on_checker_job and should_warm_cache:
            try:
                warmed_key_count = await warm_api_cache()
                logger.info("checker_job.cache_warm_completed", warmed_key_count=warmed_key_count)
            except Exception:
                logger.warning("checker_job.cache_warm_failed", exc_info=True)
        elif settings.api_cache_enabled and settings.api_cache_warm_on_checker_job and is_cloud_run_task_execution:
            logger.info(
                "checker_job.cache_warm_skipped_cloud_run_task_execution",
                cloud_run_task_index=cloud_run_task_index,
                cloud_run_task_count=cloud_run_task_count,
                api_cache_warm_on_cloud_run_checker_job=settings.api_cache_warm_on_cloud_run_checker_job,
            )
        elif settings.api_cache_enabled and settings.api_cache_warm_on_checker_job:
            logger.info(
                "checker_job.cache_warm_skipped_non_primary_task",
                cloud_run_task_index=cloud_run_task_index,
                cloud_run_task_count=cloud_run_task_count,
            )

    if strict and has_non_up_result:
        raise SystemExit(1)


def main() -> None:
    """Run the entrypoint."""
    parser = _build_parser()
    args = parser.parse_args()

    if args.default_proxy_url is not None:
        os.environ["IS_IT_DOWN_DEFAULT_CHECKER_PROXY_URL"] = args.default_proxy_url
        get_settings.cache_clear()
        clear_proxy_resolution_cache()

    asyncio.run(_run_once(targets=args.targets, strict=args.strict, dry_run=args.dry_run))


if __name__ == "__main__":
    main()

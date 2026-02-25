import argparse
import asyncio
import json
import os
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import httpx
import structlog
from google.cloud import bigquery

from is_it_down.checkers.base import BaseServiceChecker, ServiceRunResult
from is_it_down.checkers.proxy import clear_proxy_resolution_cache
from is_it_down.logging import configure_logging
from is_it_down.scripts.run_service_checker import (
    discover_service_checkers,
    resolve_service_checker_targets,
)
from is_it_down.settings import get_settings

logger = structlog.get_logger(__name__)


def _service_checker_path(service_checker_cls: type[BaseServiceChecker]) -> str:
    return f"{service_checker_cls.__module__}.{service_checker_cls.__name__}"


def _build_parser() -> argparse.ArgumentParser:
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


def _resolve_service_checker_classes(targets: list[str]) -> list[type[BaseServiceChecker]]:
    if targets:
        return resolve_service_checker_targets(targets)

    discovered = discover_service_checkers()
    return [discovered[key] for key in sorted(discovered)]


async def _execute_service_checkers(
    service_checker_classes: list[type[BaseServiceChecker]],
) -> list[tuple[type[BaseServiceChecker], ServiceRunResult]]:
    settings = get_settings()
    timeout = httpx.Timeout(settings.default_http_timeout_seconds)
    semaphore = asyncio.Semaphore(settings.checker_concurrency)

    async with httpx.AsyncClient(
        timeout=timeout,
        headers={"User-Agent": settings.user_agent},
        follow_redirects=True,
    ) as client:

        async def _run_one(
            service_checker_cls: type[BaseServiceChecker],
        ) -> tuple[type[BaseServiceChecker], ServiceRunResult]:
            async with semaphore:
                return service_checker_cls, await service_checker_cls().run_all(client)

        return await asyncio.gather(*[_run_one(service_checker_cls) for service_checker_cls in service_checker_classes])


def _build_bigquery_rows(
    runs: list[tuple[type[BaseServiceChecker], ServiceRunResult]],
    *,
    run_id: str,
    execution_id: str | None,
    ingested_at: datetime,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    ingested_at_iso = ingested_at.isoformat()

    for service_checker_cls, run_result in runs:
        checker_class = _service_checker_path(service_checker_cls)
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


def _has_non_up_result(runs: list[tuple[type[BaseServiceChecker], ServiceRunResult]]) -> bool:
    return any(check_result.status != "up" for _, run_result in runs for check_result in run_result.check_results)


async def _run_once(*, targets: list[str], strict: bool, dry_run: bool) -> None:
    settings = get_settings()
    configure_logging(settings.log_level)

    service_checker_classes = _resolve_service_checker_classes(targets)
    if not service_checker_classes:
        raise RuntimeError("No service checkers discovered.")

    logger.info(
        "checker_job.starting",
        checker_count=len(service_checker_classes),
        dry_run=dry_run,
    )

    runs = await _execute_service_checkers(service_checker_classes)

    run_id = uuid4().hex
    execution_id = os.getenv("CLOUD_RUN_EXECUTION")
    rows = _build_bigquery_rows(
        runs,
        run_id=run_id,
        execution_id=execution_id,
        ingested_at=datetime.now(UTC),
    )

    check_count = sum(len(run_result.check_results) for _, run_result in runs)
    non_up_count = sum(
        1 for _, run_result in runs for check_result in run_result.check_results if check_result.status != "up"
    )

    logger.info(
        "checker_job.completed",
        run_id=run_id,
        service_count=len(runs),
        check_count=check_count,
        non_up_count=non_up_count,
    )

    if not dry_run:
        _insert_rows(rows)

    if strict and _has_non_up_result(runs):
        raise SystemExit(1)


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.default_proxy_url is not None:
        os.environ["IS_IT_DOWN_DEFAULT_CHECKER_PROXY_URL"] = args.default_proxy_url
        get_settings.cache_clear()
        clear_proxy_resolution_cache()

    asyncio.run(_run_once(targets=args.targets, strict=args.strict, dry_run=args.dry_run))


if __name__ == "__main__":
    main()

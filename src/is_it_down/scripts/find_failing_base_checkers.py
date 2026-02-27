"""Provide functionality for `is_it_down.scripts.find_failing_base_checkers`."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from google.cloud import bigquery

from is_it_down.settings import Settings, get_settings

_DEFAULT_LOOKBACK_HOURS = 48
_DEFAULT_SAMPLE_LIMIT = 3
_DEFAULT_MAX_GROUPS = 100
_MAX_METADATA_PREVIEW_CHARS = 200


@dataclass(frozen=True)
class FailingSample:
    """Represent one failing check row sample."""

    observed_at: datetime | None
    status: str
    latency_ms: int | None
    http_status: int | None
    error_code: str | None
    error_message: str | None
    metadata_json: str | None
    run_id: str | None
    execution_id: str | None


@dataclass(frozen=True)
class FailingGroup:
    """Represent one grouped failing check summary."""

    service_key: str
    check_key: str
    failing_count: int
    degraded_count: int
    down_count: int
    first_seen: datetime | None
    last_seen: datetime | None
    samples: list[FailingSample]


def _build_parser() -> argparse.ArgumentParser:
    """Build parser.

    Returns:
        The resulting value.
    """
    parser = argparse.ArgumentParser(
        prog="find-failing-base-checkers",
        description="Query BigQuery for degraded/down BaseChecks in the selected lookback window.",
    )
    parser.add_argument(
        "--lookback-hours",
        type=int,
        default=_DEFAULT_LOOKBACK_HOURS,
        help="How many past hours to query (default: 48).",
    )
    parser.add_argument(
        "--sample-limit",
        type=int,
        default=_DEFAULT_SAMPLE_LIMIT,
        help="Max sample rows to show per failing BaseCheck group (default: 3).",
    )
    parser.add_argument(
        "--max-groups",
        type=int,
        default=_DEFAULT_MAX_GROUPS,
        help="Maximum grouped failing BaseChecks to return (default: 100).",
    )
    parser.add_argument(
        "--service-key",
        action="append",
        default=[],
        help="Optional service key filter. Repeat to provide multiple keys.",
    )
    parser.add_argument(
        "--check-key",
        action="append",
        default=[],
        help="Optional check key filter. Repeat to provide multiple keys.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit structured JSON output.",
    )
    return parser


def _ensure_utc(value: datetime | None) -> datetime | None:
    """Ensure utc.

    Args:
        value: The value value.

    Returns:
        The resulting value.
    """
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _to_datetime(value: Any) -> datetime | None:
    """To datetime.

    Args:
        value: The value value.

    Returns:
        The resulting value.
    """
    if isinstance(value, datetime):
        return _ensure_utc(value)
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
        return _ensure_utc(parsed)
    return None


def _to_optional_int(value: Any) -> int | None:
    """To optional int.

    Args:
        value: The value value.

    Returns:
        The resulting value.
    """
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _to_optional_str(value: Any) -> str | None:
    """To optional str.

    Args:
        value: The value value.

    Returns:
        The resulting value.
    """
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return str(value)


def _mapping_from_row(value: Any) -> dict[str, Any]:
    """Mapping from row.

    Args:
        value: The value value.

    Returns:
        The resulting value.
    """
    if isinstance(value, Mapping):
        return dict(value)

    items_method = getattr(value, "items", None)
    if callable(items_method):
        return dict(items_method())
    return {}


def _resolve_table_id(client: bigquery.Client, settings: Settings) -> str:
    """Resolve table id.

    Args:
        client: The client value.
        settings: The settings value.

    Raises:
        RuntimeError: If an error occurs while executing this function.

    Returns:
        The resulting value.
    """
    project_id = settings.bigquery_project_id or client.project
    if not project_id:
        raise RuntimeError(
            "BigQuery project ID is required. Set IS_IT_DOWN_BIGQUERY_PROJECT_ID or use authenticated default project."
        )
    return f"{project_id}.{settings.bigquery_dataset_id}.{settings.bigquery_table_id}"


def _build_query(table_id: str) -> str:
    """Build query.

    Args:
        table_id: The table id value.

    Returns:
        The resulting value.
    """
    return f"""
    WITH filtered AS (
      SELECT
        service_key,
        check_key,
        run_id,
        execution_id,
        observed_at,
        status,
        latency_ms,
        http_status,
        error_code,
        error_message,
        metadata_json
      FROM `{table_id}`
      WHERE observed_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @lookback_hours HOUR)
        AND status IN ('degraded', 'down')
        AND (@has_service_filters = FALSE OR service_key IN UNNEST(@service_keys))
        AND (@has_check_filters = FALSE OR check_key IN UNNEST(@check_keys))
    ),
    grouped AS (
      SELECT
        service_key,
        check_key,
        COUNT(1) AS failing_count,
        COUNTIF(status = 'degraded') AS degraded_count,
        COUNTIF(status = 'down') AS down_count,
        MIN(observed_at) AS first_seen,
        MAX(observed_at) AS last_seen,
        ARRAY_AGG(
          STRUCT(
            observed_at,
            status,
            latency_ms,
            http_status,
            error_code,
            error_message,
            metadata_json,
            run_id,
            execution_id
          )
          ORDER BY observed_at DESC
          LIMIT @sample_limit
        ) AS samples
      FROM filtered
      GROUP BY service_key, check_key
    )
    SELECT
      service_key,
      check_key,
      failing_count,
      degraded_count,
      down_count,
      first_seen,
      last_seen,
      samples
    FROM grouped
    ORDER BY failing_count DESC, down_count DESC, last_seen DESC
    LIMIT @max_groups
    """


def _build_query_parameters(
    *,
    lookback_hours: int,
    sample_limit: int,
    max_groups: int,
    service_keys: Sequence[str],
    check_keys: Sequence[str],
) -> list[bigquery.ArrayQueryParameter | bigquery.ScalarQueryParameter]:
    """Build query parameters.

    Args:
        lookback_hours: The lookback hours value.
        sample_limit: The sample limit value.
        max_groups: The max groups value.
        service_keys: The service keys value.
        check_keys: The check keys value.

    Returns:
        The resulting value.
    """
    return [
        bigquery.ScalarQueryParameter("lookback_hours", "INT64", lookback_hours),
        bigquery.ScalarQueryParameter("sample_limit", "INT64", sample_limit),
        bigquery.ScalarQueryParameter("max_groups", "INT64", max_groups),
        bigquery.ScalarQueryParameter("has_service_filters", "BOOL", bool(service_keys)),
        bigquery.ScalarQueryParameter("has_check_filters", "BOOL", bool(check_keys)),
        bigquery.ArrayQueryParameter("service_keys", "STRING", list(service_keys)),
        bigquery.ArrayQueryParameter("check_keys", "STRING", list(check_keys)),
    ]


def _parse_sample(sample_row: Any) -> FailingSample:
    """Parse sample.

    Args:
        sample_row: The sample row value.

    Returns:
        The resulting value.
    """
    row = _mapping_from_row(sample_row)
    return FailingSample(
        observed_at=_to_datetime(row.get("observed_at")),
        status=_to_optional_str(row.get("status")) or "unknown",
        latency_ms=_to_optional_int(row.get("latency_ms")),
        http_status=_to_optional_int(row.get("http_status")),
        error_code=_to_optional_str(row.get("error_code")),
        error_message=_to_optional_str(row.get("error_message")),
        metadata_json=_to_optional_str(row.get("metadata_json")),
        run_id=_to_optional_str(row.get("run_id")),
        execution_id=_to_optional_str(row.get("execution_id")),
    )


def _parse_group_row(group_row: Any) -> FailingGroup:
    """Parse group row.

    Args:
        group_row: The group row value.

    Returns:
        The resulting value.
    """
    row = _mapping_from_row(group_row)
    raw_samples = row.get("samples")
    samples: list[FailingSample] = []
    if isinstance(raw_samples, list):
        samples = [_parse_sample(sample) for sample in raw_samples]

    return FailingGroup(
        service_key=_to_optional_str(row.get("service_key")) or "-",
        check_key=_to_optional_str(row.get("check_key")) or "-",
        failing_count=_to_optional_int(row.get("failing_count")) or 0,
        degraded_count=_to_optional_int(row.get("degraded_count")) or 0,
        down_count=_to_optional_int(row.get("down_count")) or 0,
        first_seen=_to_datetime(row.get("first_seen")),
        last_seen=_to_datetime(row.get("last_seen")),
        samples=samples,
    )


def _query_failing_base_checks(
    *,
    client: bigquery.Client,
    table_id: str,
    lookback_hours: int,
    sample_limit: int,
    max_groups: int,
    service_keys: Sequence[str],
    check_keys: Sequence[str],
) -> list[FailingGroup]:
    """Query failing base checks.

    Args:
        client: The client value.
        table_id: The table id value.
        lookback_hours: The lookback hours value.
        sample_limit: The sample limit value.
        max_groups: The max groups value.
        service_keys: The service keys value.
        check_keys: The check keys value.

    Returns:
        The resulting value.
    """
    query = _build_query(table_id)
    parameters = _build_query_parameters(
        lookback_hours=lookback_hours,
        sample_limit=sample_limit,
        max_groups=max_groups,
        service_keys=service_keys,
        check_keys=check_keys,
    )
    job_config = bigquery.QueryJobConfig(query_parameters=parameters)
    rows = client.query(query, job_config=job_config).result()
    return [_parse_group_row(row) for row in rows]


def _format_datetime(value: datetime | None) -> str:
    """Format datetime.

    Args:
        value: The value value.

    Returns:
        The resulting value.
    """
    ensured = _ensure_utc(value)
    if ensured is None:
        return "-"
    return ensured.isoformat()


def _truncate(value: str | None, limit: int) -> str:
    """Truncate.

    Args:
        value: The value value.
        limit: The limit value.

    Returns:
        The resulting value.
    """
    if not value:
        return "-"
    if len(value) <= limit:
        return value
    return f"{value[: limit - 3]}..."


def _render_human_report(
    *,
    groups: Sequence[FailingGroup],
    table_id: str,
    lookback_hours: int,
    service_keys: Sequence[str],
    check_keys: Sequence[str],
    generated_at: datetime,
) -> str:
    """Render human report.

    Args:
        groups: The groups value.
        table_id: The table id value.
        lookback_hours: The lookback hours value.
        service_keys: The service keys value.
        check_keys: The check keys value.
        generated_at: The generated at value.

    Returns:
        The resulting value.
    """
    service_filter = ", ".join(service_keys) if service_keys else "(all)"
    check_filter = ", ".join(check_keys) if check_keys else "(all)"

    lines = [
        "Failing BaseChecks (degraded/down)",
        f"Generated at: {_format_datetime(generated_at)}",
        f"Table: {table_id}",
        f"Lookback: last {lookback_hours}h",
        f"Service filter: {service_filter}",
        f"Check filter: {check_filter}",
        "",
    ]

    if not groups:
        lines.append("No degraded/down BaseCheck rows found for the selected filters and window.")
        return "\n".join(lines)

    for index, group in enumerate(groups, start=1):
        lines.append(
            f"{index}. {group.service_key}.{group.check_key} "
            f"(failing={group.failing_count}, degraded={group.degraded_count}, down={group.down_count})"
        )
        lines.append(f"   first_seen={_format_datetime(group.first_seen)}")
        lines.append(f"   last_seen={_format_datetime(group.last_seen)}")
        if not group.samples:
            lines.append("   samples: none")
            lines.append("")
            continue

        lines.append("   samples:")
        for sample_index, sample in enumerate(group.samples, start=1):
            error_text = " | ".join(
                part for part in [sample.error_code, sample.error_message] if part and part.strip()
            ) or "-"
            lines.append(
                "   "
                f"{sample_index}) observed_at={_format_datetime(sample.observed_at)} status={sample.status} "
                f"latency_ms={sample.latency_ms if sample.latency_ms is not None else '-'} "
                f"http_status={sample.http_status if sample.http_status is not None else '-'} "
                f"run_id={sample.run_id or '-'} execution_id={sample.execution_id or '-'}"
            )
            lines.append(f"      error={_truncate(error_text, 180)}")
            lines.append(f"      metadata={_truncate(sample.metadata_json, _MAX_METADATA_PREVIEW_CHARS)}")
        lines.append("")

    return "\n".join(lines)


def _sample_payload(sample: FailingSample) -> dict[str, Any]:
    """Sample payload.

    Args:
        sample: The sample value.

    Returns:
        The resulting value.
    """
    return {
        "observed_at": _format_datetime(sample.observed_at),
        "status": sample.status,
        "latency_ms": sample.latency_ms,
        "http_status": sample.http_status,
        "error_code": sample.error_code,
        "error_message": sample.error_message,
        "metadata_json": sample.metadata_json,
        "run_id": sample.run_id,
        "execution_id": sample.execution_id,
    }


def _group_payload(group: FailingGroup) -> dict[str, Any]:
    """Group payload.

    Args:
        group: The group value.

    Returns:
        The resulting value.
    """
    return {
        "service_key": group.service_key,
        "check_key": group.check_key,
        "failing_count": group.failing_count,
        "degraded_count": group.degraded_count,
        "down_count": group.down_count,
        "first_seen": _format_datetime(group.first_seen),
        "last_seen": _format_datetime(group.last_seen),
        "samples": [_sample_payload(sample) for sample in group.samples],
    }


def _json_payload(
    *,
    groups: Sequence[FailingGroup],
    table_id: str,
    lookback_hours: int,
    service_keys: Sequence[str],
    check_keys: Sequence[str],
    generated_at: datetime,
) -> dict[str, Any]:
    """Json payload.

    Args:
        groups: The groups value.
        table_id: The table id value.
        lookback_hours: The lookback hours value.
        service_keys: The service keys value.
        check_keys: The check keys value.
        generated_at: The generated at value.

    Returns:
        The resulting value.
    """
    return {
        "generated_at": _format_datetime(generated_at),
        "lookback_hours": lookback_hours,
        "table_id": table_id,
        "filters": {
            "service_keys": list(service_keys),
            "check_keys": list(check_keys),
        },
        "groups": [_group_payload(group) for group in groups],
    }


def _run(args: argparse.Namespace) -> int:
    """Run.

    Args:
        args: The args value.

    Raises:
        ValueError: If an error occurs while executing this function.

    Returns:
        The resulting value.
    """
    if args.lookback_hours <= 0:
        raise ValueError("--lookback-hours must be greater than 0.")
    if args.sample_limit <= 0:
        raise ValueError("--sample-limit must be greater than 0.")
    if args.max_groups <= 0:
        raise ValueError("--max-groups must be greater than 0.")

    settings = get_settings()
    client = bigquery.Client(project=settings.bigquery_project_id or None)
    table_id = _resolve_table_id(client, settings)
    groups = _query_failing_base_checks(
        client=client,
        table_id=table_id,
        lookback_hours=args.lookback_hours,
        sample_limit=args.sample_limit,
        max_groups=args.max_groups,
        service_keys=args.service_key,
        check_keys=args.check_key,
    )

    generated_at = datetime.now(UTC)
    if args.json:
        payload = _json_payload(
            groups=groups,
            table_id=table_id,
            lookback_hours=args.lookback_hours,
            service_keys=args.service_key,
            check_keys=args.check_key,
            generated_at=generated_at,
        )
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(
            _render_human_report(
                groups=groups,
                table_id=table_id,
                lookback_hours=args.lookback_hours,
                service_keys=args.service_key,
                check_keys=args.check_key,
                generated_at=generated_at,
            )
        )
    return 0


def main() -> None:
    """Run the entrypoint.

    Raises:
        SystemExit: If an error occurs while executing this function.
    """
    parser = _build_parser()
    args = parser.parse_args()

    try:
        exit_code = _run(args)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()

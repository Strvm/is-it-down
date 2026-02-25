"""Provide functionality for `is_it_down.api.bigquery_store`."""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from typing import Any
from urllib.parse import quote
from uuid import uuid4

import structlog
from google.cloud import bigquery
from pydantic import BaseModel, ConfigDict

from is_it_down.api.schemas import (
    BaseCheckUptimeSummary,
    CheckerTrendPoint,
    CheckRunSummary,
    IncidentSummary,
    RelatedServiceSummary,
    ServiceCheckerTrendSummary,
    ServiceDetail,
    ServiceSummary,
    ServiceUptimeSummary,
    SnapshotPoint,
)
from is_it_down.checkers.base import BaseServiceChecker
from is_it_down.checkers.registry import registry
from is_it_down.core.models import CheckResult, ServiceStatus
from is_it_down.core.scoring import status_from_score, weighted_service_score
from is_it_down.settings import get_settings

_SERVICE_LOOKBACK_DAYS = 7
_INCIDENT_LOOKBACK_DAYS = 14
_MAX_INCIDENTS = 500
_DEPENDENCY_ALIGNMENT_WINDOW = timedelta(minutes=45)
_SERVICE_VIEW_ORDER_WINDOW = timedelta(hours=1)
_VALID_STATUSES: set[str] = {"up", "degraded", "down"}
_DEFAULT_LOGO_FOREGROUND = "#0f172a"
_DEFAULT_LOGO_BACKGROUND = "#e2e8f0"
logger = structlog.get_logger(__name__)


class ServiceDefinition(BaseModel):
    """Represent `ServiceDefinition`."""

    model_config = ConfigDict(frozen=True)

    service_id: int
    slug: str
    name: str
    logo_url: str
    official_status_url: str | None
    description: str | None
    check_weights: dict[str, float]
    dependencies: tuple[str, ...]


class SnapshotEvent(BaseModel):
    """Represent `SnapshotEvent`."""

    model_config = ConfigDict(frozen=True)

    snapshot_id: int
    service_id: int
    observed_at: datetime
    status: ServiceStatus
    raw_score: float
    effective_score: float
    dependency_impacted: bool
    attribution_confidence: float
    probable_root_service_id: int | None


def _stable_int(value: str) -> int:
    """Stable int.
    
    Args:
        value: The value value.
    
    Returns:
        The resulting value.
    """
    return int(hashlib.sha1(value.encode("utf-8")).hexdigest()[:8], 16)


def _normalize_status(value: str | None) -> ServiceStatus:
    """Normalize status.
    
    Args:
        value: The value value.
    
    Returns:
        The resulting value.
    """
    if value in _VALID_STATUSES:
        return value
    return "up"


def _status_severity(status: ServiceStatus) -> int:
    """Status severity.
    
    Args:
        status: The status value.
    
    Returns:
        The resulting value.
    """
    severity = {"up": 0, "degraded": 1, "down": 2}
    return severity[status]


def _ensure_utc(dt: datetime | None) -> datetime | None:
    """Ensure utc.
    
    Args:
        dt: The dt value.
    
    Returns:
        The resulting value.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def _service_name_from_checker(
    service_key: str,
    checker_cls: type[BaseServiceChecker] | None,
) -> str:
    """Service name from checker.
    
    Args:
        service_key: The service key value.
        checker_cls: The checker cls value.
    
    Returns:
        The resulting value.
    """
    if checker_cls is not None:
        class_name = checker_cls.__name__
        if class_name.endswith("ServiceChecker"):
            display = class_name[: -len("ServiceChecker")]
            if display:
                return display
    return service_key.replace("_", " ").replace("-", " ").title()


def _default_logo_data_uri(service_key: str) -> str:
    """Default logo data uri.
    
    Args:
        service_key: The service key value.
    
    Returns:
        The resulting value.
    """
    label = (service_key[:2] or "?").upper()
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='96' height='96' viewBox='0 0 96 96'>"
        f"<rect width='96' height='96' rx='20' fill='{_DEFAULT_LOGO_BACKGROUND}'/>"
        f"<text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' "
        f"font-family='Arial, sans-serif' font-size='32' font-weight='700' fill='{_DEFAULT_LOGO_FOREGROUND}'>"
        f"{label}</text></svg>"
    )
    return f"data:image/svg+xml,{quote(svg)}"


def _fallback_service_definition(service_key: str) -> ServiceDefinition:
    """Fallback service definition.
    
    Args:
        service_key: The service key value.
    
    Returns:
        The resulting value.
    """
    return ServiceDefinition(
        service_id=_stable_int(service_key),
        slug=service_key,
        name=_service_name_from_checker(service_key, None),
        logo_url=_default_logo_data_uri(service_key),
        official_status_url=None,
        description=None,
        check_weights={},
        dependencies=(),
    )


def _sort_service_summaries_by_views(
    summaries: list[ServiceSummary],
    view_counts_by_slug: dict[str, int],
) -> list[ServiceSummary]:
    """Sort service summaries by views.
    
    Args:
        summaries: The summaries value.
        view_counts_by_slug: The view counts by slug value.
    
    Returns:
        The resulting value.
    """
    return sorted(
        summaries,
        key=lambda summary: (-view_counts_by_slug.get(summary.slug, 0), summary.slug),
    )


@lru_cache
def discovered_service_definitions() -> dict[str, ServiceDefinition]:
    """Discovered service definitions.
    
    Returns:
        The resulting value.
    """
    discovered = sorted(registry.discover_service_checkers(), key=lambda checker: checker.service_key)
    definitions: dict[str, ServiceDefinition] = {}

    for checker_cls in discovered:
        checker = checker_cls()
        check_weights: dict[str, float] = {}
        checks = checker.resolve_check_weights(list(checker.build_checks()))
        for check in checks:
            check_weights[check.check_key] = float(check.weight or 1.0)

        service_key = checker.service_key
        definitions[service_key] = ServiceDefinition(
            service_id=_stable_int(service_key),
            slug=service_key,
            name=_service_name_from_checker(service_key, checker_cls),
            logo_url=checker.logo_url,
            official_status_url=checker.official_uptime,
            description=None,
            check_weights=check_weights,
            dependencies=tuple(checker.dependency_service_keys()),
        )

    return definitions


def _build_check_result_from_row(row: dict[str, Any]) -> CheckResult:
    """Build check result from row.
    
    Args:
        row: The row value.
    
    Returns:
        The resulting value.
    """
    observed_at = _ensure_utc(row.get("observed_at")) or datetime.now(UTC)
    status = _normalize_status(row.get("status"))
    latency_ms = row.get("latency_ms")
    if latency_ms is not None:
        latency_ms = int(latency_ms)

    return CheckResult(
        check_key=str(row["check_key"]),
        status=status,
        observed_at=observed_at,
        latency_ms=latency_ms,
    )


def _metadata_from_json(raw: str | None) -> dict[str, Any]:
    """Metadata from json.
    
    Args:
        raw: The raw value.
    
    Returns:
        The resulting value.
    """
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except (TypeError, ValueError):
        return {}
    if isinstance(parsed, dict):
        return parsed
    return {}


def _compute_raw_score(
    service: ServiceDefinition,
    check_rows: list[dict[str, Any]],
) -> tuple[float, ServiceStatus]:
    """Compute raw score.
    
    Args:
        service: The service value.
        check_rows: The check rows value.
    
    Returns:
        The resulting value.
    """
    if not check_rows:
        return 100.0, "up"

    check_results = [_build_check_result_from_row(row) for row in check_rows]
    raw_score = weighted_service_score(check_results, service.check_weights)
    return raw_score, status_from_score(raw_score)


def _health_score_from_status(status: str | None) -> float:
    """Health score from status.
    
    Args:
        status: The status value.
    
    Returns:
        The resulting value.
    """
    normalized = _normalize_status(status)
    if normalized == "up":
        return 100.0
    if normalized == "degraded":
        return 60.0
    return 0.0


def _service_definition_for_key(service_key: str) -> ServiceDefinition:
    """Service definition for key.
    
    Args:
        service_key: The service key value.
    
    Returns:
        The resulting value.
    """
    return discovered_service_definitions().get(service_key) or _fallback_service_definition(service_key)


def _infer_dependency_attribution(
    *,
    service_summary: ServiceSummary,
    summaries_by_key: dict[str, ServiceSummary],
) -> tuple[bool, float, int | None]:
    """Infer dependency attribution.
    
    Args:
        service_summary: The service summary value.
        summaries_by_key: The summaries by key value.
    
    Returns:
        The resulting value.
    """
    impacted_dependencies = _likely_related_dependencies(
        service_summary=service_summary,
        summaries_by_key=summaries_by_key,
    )

    if not impacted_dependencies:
        return False, 0.0, None

    probable_root = max(
        impacted_dependencies,
        key=lambda summary: (_status_severity(summary.status), summary.observed_at),
    )
    base_confidence = 0.8 if probable_root.status == "down" else 0.65
    confidence = min(0.95, base_confidence + max(0, len(impacted_dependencies) - 1) * 0.07)
    return True, round(confidence, 3), probable_root.service_id


def _apply_dependency_attribution(summaries: list[ServiceSummary]) -> list[ServiceSummary]:
    """Apply dependency attribution.
    
    Args:
        summaries: The summaries value.
    
    Returns:
        The resulting value.
    """
    summaries_by_key = {summary.slug: summary for summary in summaries}
    enriched: list[ServiceSummary] = []

    for summary in summaries:
        dependency_impacted, attribution_confidence, probable_root_service_id = _infer_dependency_attribution(
            service_summary=summary,
            summaries_by_key=summaries_by_key,
        )
        enriched.append(
            summary.model_copy(
                update={
                    "dependency_impacted": dependency_impacted,
                    "attribution_confidence": attribution_confidence,
                    "probable_root_service_id": probable_root_service_id,
                }
            )
        )

    return enriched


def _likely_related_dependencies(
    *,
    service_summary: ServiceSummary,
    summaries_by_key: dict[str, ServiceSummary],
) -> list[ServiceSummary]:
    """Likely related dependencies.
    
    Args:
        service_summary: The service summary value.
        summaries_by_key: The summaries by key value.
    
    Returns:
        The resulting value.
    """
    if service_summary.status == "up":
        return []

    definition = discovered_service_definitions().get(service_summary.slug)
    if definition is None or not definition.dependencies:
        return []

    related: list[ServiceSummary] = []
    for dependency_key in definition.dependencies:
        dependency_summary = summaries_by_key.get(dependency_key)
        if dependency_summary is None:
            continue
        if dependency_summary.status == "up":
            continue

        observed_delta = abs(service_summary.observed_at - dependency_summary.observed_at)
        if observed_delta > _DEPENDENCY_ALIGNMENT_WINDOW:
            continue

        related.append(dependency_summary)

    return sorted(
        related,
        key=lambda summary: (_status_severity(summary.status), summary.observed_at),
        reverse=True,
    )


def _incident_id(service_key: str, started_at: datetime) -> int:
    """Incident id.
    
    Args:
        service_key: The service key value.
        started_at: The started at value.
    
    Returns:
        The resulting value.
    """
    return _stable_int(f"{service_key}:{started_at.isoformat()}")


class BigQueryApiStore:
    """Represent `BigQueryApiStore`."""

    def __init__(self, client: bigquery.Client) -> None:
        """Initialize the instance.
        
        Args:
            client: The client value.
        
        Raises:
            RuntimeError: If an error occurs while executing this function.
        """
        settings = get_settings()
        project_id = settings.bigquery_project_id or client.project
        if not project_id:
            raise RuntimeError("BigQuery project ID is required. Set IS_IT_DOWN_BIGQUERY_PROJECT_ID or configure ADC.")

        self._client = client
        self._table_id = f"{project_id}.{settings.bigquery_dataset_id}.{settings.bigquery_table_id}"
        self._tracking_table_id = (
            f"{project_id}.{settings.tracking_bigquery_dataset_id}.{settings.tracking_bigquery_table_id}"
        )

    async def _query(
        self,
        query: str,
        parameters: list[bigquery.ScalarQueryParameter] | None = None,
    ) -> list[dict[str, Any]]:
        """Query.
        
        Args:
            query: The query value.
            parameters: The parameters value.
        
        Returns:
            The resulting value.
        """
        return await asyncio.to_thread(self._query_sync, query, parameters or [])

    def _query_sync(
        self,
        query: str,
        parameters: list[bigquery.ScalarQueryParameter],
    ) -> list[dict[str, Any]]:
        """Query sync.
        
        Args:
            query: The query value.
            parameters: The parameters value.
        
        Returns:
            The resulting value.
        """
        job_config = bigquery.QueryJobConfig(query_parameters=parameters)
        rows = self._client.query(query, job_config=job_config).result()
        return [dict(row.items()) for row in rows]

    async def _latest_rows_for_services(
        self,
        service_keys: list[str],
        *,
        cutoff: datetime,
    ) -> dict[str, list[dict[str, Any]]]:
        """Latest rows for services.
        
        Args:
            service_keys: The service keys value.
            cutoff: The cutoff value.
        
        Returns:
            The resulting value.
        """
        if not service_keys:
            return {}

        rows = await self._query(
            f"""
            SELECT
              service_key,
              check_key,
              status,
              observed_at,
              latency_ms
            FROM (
              SELECT
                service_key,
                check_key,
                status,
                observed_at,
                latency_ms,
                ROW_NUMBER() OVER (
                  PARTITION BY service_key, check_key
                  ORDER BY observed_at DESC
                ) AS row_num
              FROM `{self._table_id}`
              WHERE service_key IN UNNEST(@service_keys)
                AND observed_at >= @cutoff
            )
            WHERE row_num = 1
            ORDER BY service_key ASC, check_key ASC
            """,
            [
                bigquery.ArrayQueryParameter("service_keys", "STRING", service_keys),
                bigquery.ScalarQueryParameter("cutoff", "TIMESTAMP", cutoff),
            ],
        )

        rows_by_service: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            rows_by_service[str(row["service_key"])].append(row)
        return rows_by_service

    async def service_detail_view_counts_since(self, *, cutoff: datetime) -> dict[str, int]:
        """Service detail view counts since.
        
        Args:
            cutoff: The cutoff value.
        
        Returns:
            The resulting value.
        """
        try:
            rows = await self._query(
                f"""
                SELECT
                  service_key,
                  COUNT(1) AS view_count
                FROM `{self._tracking_table_id}`
                WHERE viewed_at >= @cutoff
                GROUP BY service_key
                """,
                [bigquery.ScalarQueryParameter("cutoff", "TIMESTAMP", cutoff)],
            )
        except Exception:
            logger.warning(
                "api.service_detail_views_query_failed",
                tracking_table=self._tracking_table_id,
                cutoff=cutoff.isoformat(),
                exc_info=True,
            )
            return {}

        view_counts_by_slug: dict[str, int] = {}
        for row in rows:
            view_counts_by_slug[str(row["service_key"])] = int(row.get("view_count") or 0)
        return view_counts_by_slug

    def track_service_detail_view(
        self,
        *,
        service_key: str,
        request_path: str,
        request_method: str,
        user_agent: str | None,
        referer: str | None,
        client_ip: str | None,
    ) -> None:
        """Track service detail view.
        
        Args:
            service_key: The service key value.
            request_path: The request path value.
            request_method: The request method value.
            user_agent: The user agent value.
            referer: The referer value.
            client_ip: The client ip value.
        """
        now = datetime.now(UTC)
        now_iso = now.isoformat()
        rows = [
            {
                "event_id": uuid4().hex,
                "service_key": service_key,
                "request_path": request_path,
                "request_method": request_method,
                "user_agent": user_agent,
                "referer": referer,
                "client_ip": client_ip,
                "viewed_at": now_iso,
                "ingested_at": now_iso,
            }
        ]
        errors = self._client.insert_rows_json(self._tracking_table_id, rows)
        if errors:
            logger.warning(
                "api.service_detail_view_insert_failed",
                tracking_table=self._tracking_table_id,
                service_key=service_key,
                errors=errors,
            )

    async def list_services(self) -> list[ServiceSummary]:
        """List services.
        
        Returns:
            The resulting value.
        """
        cutoff = datetime.now(UTC) - timedelta(days=_SERVICE_LOOKBACK_DAYS)
        rows = await self._query(
            f"""
            WITH filtered AS (
              SELECT
                service_key,
                check_key,
                status,
                observed_at,
                latency_ms
              FROM `{self._table_id}`
              WHERE observed_at >= @cutoff
            )
            SELECT
              service_key,
              check_key,
              status,
              observed_at,
              latency_ms
            FROM (
              SELECT
                service_key,
                check_key,
                status,
                observed_at,
                latency_ms,
                ROW_NUMBER() OVER (
                  PARTITION BY service_key, check_key
                  ORDER BY observed_at DESC
                ) AS row_num
              FROM filtered
            )
            WHERE row_num = 1
            ORDER BY service_key ASC, check_key ASC
            """,
            [bigquery.ScalarQueryParameter("cutoff", "TIMESTAMP", cutoff)],
        )

        rows_by_service: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            rows_by_service[str(row["service_key"])].append(row)

        service_keys = set(discovered_service_definitions().keys()) | set(rows_by_service.keys())
        now = datetime.now(UTC)
        summaries: list[ServiceSummary] = []
        for service_key in sorted(service_keys):
            definition = _service_definition_for_key(service_key)
            check_rows = rows_by_service.get(service_key, [])

            observed_at = now
            if check_rows:
                observed_at = max(
                    (_ensure_utc(row.get("observed_at")) or now for row in check_rows),
                    default=now,
                )

            raw_score, status = _compute_raw_score(definition, check_rows)
            summaries.append(
                ServiceSummary(
                    service_id=definition.service_id,
                    slug=definition.slug,
                    name=definition.name,
                    logo_url=definition.logo_url,
                    status=status,
                    raw_score=raw_score,
                    effective_score=raw_score,
                    observed_at=observed_at,
                    dependency_impacted=False,
                    attribution_confidence=0.0,
                    probable_root_service_id=None,
                )
            )

        view_counts_by_slug = await self.service_detail_view_counts_since(
            cutoff=datetime.now(UTC) - _SERVICE_VIEW_ORDER_WINDOW,
        )
        attributed_summaries = _apply_dependency_attribution(summaries)
        return _sort_service_summaries_by_views(attributed_summaries, view_counts_by_slug)

    async def get_services_uptime(self, *, cutoff: datetime) -> list[ServiceUptimeSummary]:
        """Get services uptime.
        
        Args:
            cutoff: The cutoff value.
        
        Returns:
            The resulting value.
        """
        rows = await self._query(
            f"""
            SELECT
              service_key,
              check_key,
              COUNT(1) AS total_runs,
              SUM(CASE WHEN status = 'up' THEN 1 ELSE 0 END) AS up_runs,
              AVG(
                CASE
                  WHEN status = 'up' THEN 100.0
                  WHEN status = 'degraded' THEN 60.0
                  WHEN status = 'down' THEN 0.0
                  ELSE 100.0
                END
              ) AS health_score
            FROM `{self._table_id}`
            WHERE observed_at >= @cutoff
            GROUP BY service_key, check_key
            ORDER BY service_key ASC, check_key ASC
            """,
            [bigquery.ScalarQueryParameter("cutoff", "TIMESTAMP", cutoff)],
        )

        check_metrics_by_service: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
        for row in rows:
            service_key = str(row["service_key"])
            check_key = str(row["check_key"])
            total_runs = int(row.get("total_runs") or 0)
            up_runs = int(row.get("up_runs") or 0)
            health_score = float(row.get("health_score") or 0.0) if total_runs > 0 else 0.0
            uptime_percent = (up_runs / total_runs * 100.0) if total_runs > 0 else 0.0

            check_metrics_by_service[service_key][check_key] = {
                "total_runs": total_runs,
                "up_runs": up_runs,
                "health_score": round(health_score, 2),
                "uptime_percent": round(uptime_percent, 2),
            }

        service_keys = set(discovered_service_definitions().keys()) | set(check_metrics_by_service.keys())
        service_uptimes: list[ServiceUptimeSummary] = []

        for service_key in sorted(service_keys):
            definition = _service_definition_for_key(service_key)
            check_metrics = check_metrics_by_service.get(service_key, {})
            discovered_check_keys = set(definition.check_weights.keys())
            all_check_keys = sorted(discovered_check_keys | set(check_metrics.keys()))

            checks: list[BaseCheckUptimeSummary] = []
            weighted_health_sum = 0.0
            weighted_uptime_sum = 0.0
            total_weight = 0.0

            for check_key in all_check_keys:
                metrics = check_metrics.get(check_key)
                if metrics is None:
                    metrics = {
                        "total_runs": 0,
                        "up_runs": 0,
                        "health_score": 0.0,
                        "uptime_percent": 0.0,
                    }

                checks.append(
                    BaseCheckUptimeSummary(
                        check_key=check_key,
                        uptime_percent=float(metrics["uptime_percent"]),
                        health_score=float(metrics["health_score"]),
                        total_runs=int(metrics["total_runs"]),
                        up_runs=int(metrics["up_runs"]),
                    )
                )

                weight = float(definition.check_weights.get(check_key, 1.0))
                weighted_health_sum += float(metrics["health_score"]) * weight
                weighted_uptime_sum += float(metrics["uptime_percent"]) * weight
                total_weight += weight

            if total_weight > 0:
                health_score = round(weighted_health_sum / total_weight, 2)
                uptime_percent = round(weighted_uptime_sum / total_weight, 2)
            else:
                health_score = 0.0
                uptime_percent = 0.0

            service_uptimes.append(
                ServiceUptimeSummary(
                    service_id=definition.service_id,
                    slug=definition.slug,
                    name=definition.name,
                    logo_url=definition.logo_url,
                    uptime_percent=uptime_percent,
                    health_score=health_score,
                    checks=checks,
                )
            )

        return service_uptimes

    async def get_service_checker_trends(self, *, cutoff: datetime) -> list[ServiceCheckerTrendSummary]:
        """Get service checker trends.
        
        Args:
            cutoff: The cutoff value.
        
        Returns:
            The resulting value.
        """
        rows = await self._query(
            f"""
            SELECT
              service_key,
              check_key,
              TIMESTAMP_TRUNC(observed_at, HOUR) AS bucket_start,
              COUNT(1) AS total_runs,
              SUM(CASE WHEN status = 'up' THEN 1 ELSE 0 END) AS up_runs,
              AVG(
                CASE
                  WHEN status = 'up' THEN 100.0
                  WHEN status = 'degraded' THEN 60.0
                  WHEN status = 'down' THEN 0.0
                  ELSE 100.0
                END
              ) AS health_score
            FROM `{self._table_id}`
            WHERE observed_at >= @cutoff
            GROUP BY service_key, check_key, bucket_start
            ORDER BY service_key ASC, bucket_start ASC, check_key ASC
            """,
            [bigquery.ScalarQueryParameter("cutoff", "TIMESTAMP", cutoff)],
        )

        points_by_service: dict[str, list[CheckerTrendPoint]] = defaultdict(list)
        for row in rows:
            service_key = str(row["service_key"])
            total_runs = int(row.get("total_runs") or 0)
            up_runs = int(row.get("up_runs") or 0)
            health_score = float(row.get("health_score") or 0.0) if total_runs > 0 else 0.0
            uptime_percent = (up_runs / total_runs * 100.0) if total_runs > 0 else 0.0
            bucket_start = _ensure_utc(row.get("bucket_start")) or datetime.now(UTC)

            points_by_service[service_key].append(
                CheckerTrendPoint(
                    bucket_start=bucket_start,
                    check_key=str(row["check_key"]),
                    uptime_percent=round(uptime_percent, 2),
                    health_score=round(health_score, 2),
                    total_runs=total_runs,
                    up_runs=up_runs,
                )
            )

        service_keys = set(discovered_service_definitions().keys()) | set(points_by_service.keys())
        trends: list[ServiceCheckerTrendSummary] = []
        for service_key in sorted(service_keys):
            definition = _service_definition_for_key(service_key)
            trends.append(
                ServiceCheckerTrendSummary(
                    service_id=definition.service_id,
                    slug=definition.slug,
                    name=definition.name,
                    logo_url=definition.logo_url,
                    points=points_by_service.get(service_key, []),
                )
            )

        return trends

    async def get_service_checker_trend(
        self,
        slug: str,
        *,
        cutoff: datetime,
    ) -> ServiceCheckerTrendSummary | None:
        """Get service checker trend.
        
        Args:
            slug: The slug value.
            cutoff: The cutoff value.
        
        Returns:
            The resulting value.
        """
        rows = await self._query(
            f"""
            SELECT
              check_key,
              TIMESTAMP_TRUNC(observed_at, HOUR) AS bucket_start,
              COUNT(1) AS total_runs,
              SUM(CASE WHEN status = 'up' THEN 1 ELSE 0 END) AS up_runs,
              AVG(
                CASE
                  WHEN status = 'up' THEN 100.0
                  WHEN status = 'degraded' THEN 60.0
                  WHEN status = 'down' THEN 0.0
                  ELSE 100.0
                END
              ) AS health_score
            FROM `{self._table_id}`
            WHERE service_key = @service_key
              AND observed_at >= @cutoff
            GROUP BY check_key, bucket_start
            ORDER BY bucket_start ASC, check_key ASC
            """,
            [
                bigquery.ScalarQueryParameter("service_key", "STRING", slug),
                bigquery.ScalarQueryParameter("cutoff", "TIMESTAMP", cutoff),
            ],
        )

        definition = discovered_service_definitions().get(slug)
        if definition is None and not rows:
            return None
        if definition is None:
            definition = _fallback_service_definition(slug)

        points: list[CheckerTrendPoint] = []
        for row in rows:
            total_runs = int(row.get("total_runs") or 0)
            up_runs = int(row.get("up_runs") or 0)
            health_score = float(row.get("health_score") or 0.0) if total_runs > 0 else 0.0
            uptime_percent = (up_runs / total_runs * 100.0) if total_runs > 0 else 0.0
            bucket_start = _ensure_utc(row.get("bucket_start")) or datetime.now(UTC)

            points.append(
                CheckerTrendPoint(
                    bucket_start=bucket_start,
                    check_key=str(row["check_key"]),
                    uptime_percent=round(uptime_percent, 2),
                    health_score=round(health_score, 2),
                    total_runs=total_runs,
                    up_runs=up_runs,
                )
            )

        return ServiceCheckerTrendSummary(
            service_id=definition.service_id,
            slug=definition.slug,
            name=definition.name,
            logo_url=definition.logo_url,
            points=points,
        )

    async def get_service_detail(self, slug: str) -> ServiceDetail | None:
        """Get service detail.
        
        Args:
            slug: The slug value.
        
        Returns:
            The resulting value.
        """
        rows = await self._query(
            f"""
            SELECT
              check_key,
              status,
              observed_at,
              latency_ms,
              http_status,
              error_code,
              error_message,
              metadata_json
            FROM (
              SELECT
                check_key,
                status,
                observed_at,
                latency_ms,
                http_status,
                error_code,
                error_message,
                metadata_json,
                ROW_NUMBER() OVER (
                  PARTITION BY check_key
                  ORDER BY observed_at DESC
                ) AS row_num
              FROM `{self._table_id}`
              WHERE service_key = @service_key
            )
            WHERE row_num = 1
            ORDER BY check_key ASC
            """,
            [bigquery.ScalarQueryParameter("service_key", "STRING", slug)],
        )

        definition = discovered_service_definitions().get(slug)
        if definition is None and not rows:
            return None
        if definition is None:
            definition = _fallback_service_definition(slug)

        now = datetime.now(UTC)
        observed_at = max((_ensure_utc(row.get("observed_at")) or now for row in rows), default=now)
        raw_score, status = _compute_raw_score(definition, rows)

        snapshot = ServiceSummary(
            service_id=definition.service_id,
            slug=definition.slug,
            name=definition.name,
            logo_url=definition.logo_url,
            status=status,
            raw_score=raw_score,
            effective_score=raw_score,
            observed_at=observed_at,
            dependency_impacted=False,
            attribution_confidence=0.0,
            probable_root_service_id=None,
        )

        dependency_summaries: dict[str, ServiceSummary] = {slug: snapshot}
        if definition.dependencies:
            dep_cutoff = datetime.now(UTC) - timedelta(days=_SERVICE_LOOKBACK_DAYS)
            dep_rows_by_service = await self._latest_rows_for_services(list(definition.dependencies), cutoff=dep_cutoff)

            for dependency_key in definition.dependencies:
                dependency_definition = _service_definition_for_key(dependency_key)
                dependency_rows = dep_rows_by_service.get(dependency_key, [])
                dependency_observed_at = now
                if dependency_rows:
                    dependency_observed_at = max(
                        (_ensure_utc(row.get("observed_at")) or now for row in dependency_rows),
                        default=now,
                    )
                dependency_raw_score, dependency_status = _compute_raw_score(dependency_definition, dependency_rows)
                dependency_summaries[dependency_key] = ServiceSummary(
                    service_id=dependency_definition.service_id,
                    slug=dependency_definition.slug,
                    name=dependency_definition.name,
                    logo_url=dependency_definition.logo_url,
                    status=dependency_status,
                    raw_score=dependency_raw_score,
                    effective_score=dependency_raw_score,
                    observed_at=dependency_observed_at,
                    dependency_impacted=False,
                    attribution_confidence=0.0,
                    probable_root_service_id=None,
                )

        dependency_impacted, attribution_confidence, probable_root_service_id = _infer_dependency_attribution(
            service_summary=snapshot,
            summaries_by_key=dependency_summaries,
        )
        snapshot = snapshot.model_copy(
            update={
                "dependency_impacted": dependency_impacted,
                "attribution_confidence": attribution_confidence,
                "probable_root_service_id": probable_root_service_id,
            }
        )
        likely_related_services = [
            RelatedServiceSummary(
                service_id=summary.service_id,
                slug=summary.slug,
                name=summary.name,
                logo_url=summary.logo_url,
                status=summary.status,
            )
            for summary in _likely_related_dependencies(
                service_summary=snapshot,
                summaries_by_key=dependency_summaries,
            )
        ]

        latest_checks: list[CheckRunSummary] = []
        for row in rows:
            latest_checks.append(
                CheckRunSummary(
                    check_key=str(row["check_key"]),
                    status=_normalize_status(row.get("status")),
                    observed_at=_ensure_utc(row.get("observed_at")) or now,
                    latency_ms=int(row["latency_ms"]) if row.get("latency_ms") is not None else None,
                    http_status=int(row["http_status"]) if row.get("http_status") is not None else None,
                    error_code=row.get("error_code"),
                    error_message=row.get("error_message"),
                    metadata=_metadata_from_json(row.get("metadata_json")),
                )
            )

        return ServiceDetail(
            service_id=definition.service_id,
            slug=definition.slug,
            name=definition.name,
            logo_url=definition.logo_url,
            official_status_url=definition.official_status_url,
            description=definition.description,
            snapshot=snapshot,
            likely_related_services=likely_related_services,
            latest_checks=latest_checks,
        )

    async def get_service_history(self, slug: str, *, cutoff: datetime) -> list[SnapshotPoint] | None:
        """Get service history.
        
        Args:
            slug: The slug value.
            cutoff: The cutoff value.
        
        Returns:
            The resulting value.
        """
        rows = await self._query(
            f"""
            WITH filtered AS (
              SELECT
                run_id,
                check_key,
                status,
                observed_at,
                latency_ms
              FROM `{self._table_id}`
              WHERE service_key = @service_key
                AND observed_at >= @cutoff
            ),
            deduped AS (
              SELECT
                run_id,
                check_key,
                status,
                observed_at,
                latency_ms
              FROM (
                SELECT
                  run_id,
                  check_key,
                  status,
                  observed_at,
                  latency_ms,
                  ROW_NUMBER() OVER (
                    PARTITION BY run_id, check_key
                    ORDER BY observed_at DESC
                  ) AS row_num
                FROM filtered
              )
              WHERE row_num = 1
            ),
            run_observed AS (
              SELECT run_id, MAX(observed_at) AS run_observed_at
              FROM deduped
              GROUP BY run_id
            )
            SELECT
              deduped.run_id,
              run_observed.run_observed_at,
              deduped.check_key,
              deduped.status,
              deduped.observed_at,
              deduped.latency_ms
            FROM deduped
            JOIN run_observed
              ON run_observed.run_id = deduped.run_id
            ORDER BY run_observed.run_observed_at ASC, deduped.check_key ASC
            """,
            [
                bigquery.ScalarQueryParameter("service_key", "STRING", slug),
                bigquery.ScalarQueryParameter("cutoff", "TIMESTAMP", cutoff),
            ],
        )

        definition = discovered_service_definitions().get(slug)
        if definition is None and not rows:
            return None
        if definition is None:
            definition = _fallback_service_definition(slug)

        rows_by_run: dict[str, list[dict[str, Any]]] = defaultdict(list)
        run_observed_at: dict[str, datetime] = {}
        for row in rows:
            run_id = str(row["run_id"])
            rows_by_run[run_id].append(row)
            run_observed = _ensure_utc(row.get("run_observed_at"))
            if run_observed is not None:
                run_observed_at[run_id] = run_observed

        points: list[SnapshotPoint] = []
        for run_id, check_rows in sorted(
            rows_by_run.items(),
            key=lambda item: run_observed_at.get(item[0], datetime.now(UTC)),
        ):
            observed_at = run_observed_at.get(run_id, datetime.now(UTC))
            raw_score, status = _compute_raw_score(definition, check_rows)
            points.append(
                SnapshotPoint(
                    observed_at=observed_at,
                    status=status,
                    raw_score=raw_score,
                    effective_score=raw_score,
                    dependency_impacted=False,
                )
            )

        return points

    async def list_incidents(self, *, status: str) -> list[IncidentSummary]:
        """List incidents.
        
        Args:
            status: The status value.
        
        Returns:
            The resulting value.
        """
        cutoff = datetime.now(UTC) - timedelta(days=_INCIDENT_LOOKBACK_DAYS)
        rows = await self._query(
            f"""
            WITH filtered AS (
              SELECT
                service_key,
                run_id,
                check_key,
                status,
                observed_at,
                latency_ms
              FROM `{self._table_id}`
              WHERE observed_at >= @cutoff
            ),
            deduped AS (
              SELECT
                service_key,
                run_id,
                check_key,
                status,
                observed_at,
                latency_ms
              FROM (
                SELECT
                  service_key,
                  run_id,
                  check_key,
                  status,
                  observed_at,
                  latency_ms,
                  ROW_NUMBER() OVER (
                    PARTITION BY service_key, run_id, check_key
                    ORDER BY observed_at DESC
                  ) AS row_num
                FROM filtered
              )
              WHERE row_num = 1
            ),
            run_observed AS (
              SELECT service_key, run_id, MAX(observed_at) AS run_observed_at
              FROM deduped
              GROUP BY service_key, run_id
            )
            SELECT
              deduped.service_key,
              deduped.run_id,
              run_observed.run_observed_at,
              deduped.check_key,
              deduped.status,
              deduped.observed_at,
              deduped.latency_ms
            FROM deduped
            JOIN run_observed
              ON run_observed.service_key = deduped.service_key
             AND run_observed.run_id = deduped.run_id
            ORDER BY deduped.service_key ASC, run_observed.run_observed_at ASC, deduped.check_key ASC
            """,
            [bigquery.ScalarQueryParameter("cutoff", "TIMESTAMP", cutoff)],
        )

        checks_by_run: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        run_observed_at: dict[tuple[str, str], datetime] = {}
        for row in rows:
            service_key = str(row["service_key"])
            run_id = str(row["run_id"])
            key = (service_key, run_id)
            checks_by_run[key].append(row)
            observed = _ensure_utc(row.get("run_observed_at"))
            if observed is not None:
                run_observed_at[key] = observed

        status_points_by_service: dict[str, list[tuple[datetime, ServiceStatus]]] = defaultdict(list)
        for key, check_rows in checks_by_run.items():
            service_key, _ = key
            definition = _service_definition_for_key(service_key)
            observed_at = run_observed_at.get(key, datetime.now(UTC))
            _, snapshot_status = _compute_raw_score(definition, check_rows)
            status_points_by_service[service_key].append((observed_at, snapshot_status))

        all_incidents: list[IncidentSummary] = []
        for service_key, points in status_points_by_service.items():
            points.sort(key=lambda item: item[0])
            definition = _service_definition_for_key(service_key)

            current_started: datetime | None = None
            peak_severity: ServiceStatus = "degraded"

            for observed_at, snapshot_status in points:
                if snapshot_status == "up":
                    if current_started is None:
                        continue

                    all_incidents.append(
                        IncidentSummary(
                            incident_id=_incident_id(service_key, current_started),
                            service_id=definition.service_id,
                            status="resolved",
                            started_at=current_started,
                            resolved_at=observed_at,
                            peak_severity=peak_severity,
                            probable_root_service_id=None,
                            confidence=0.0,
                            summary=f"{definition.name} recovered",
                        )
                    )
                    current_started = None
                    peak_severity = "degraded"
                    continue

                if current_started is None:
                    current_started = observed_at
                    peak_severity = snapshot_status
                    continue

                if _status_severity(snapshot_status) > _status_severity(peak_severity):
                    peak_severity = snapshot_status

            if current_started is not None:
                all_incidents.append(
                    IncidentSummary(
                        incident_id=_incident_id(service_key, current_started),
                        service_id=definition.service_id,
                        status="open",
                        started_at=current_started,
                        resolved_at=None,
                        peak_severity=peak_severity,
                        probable_root_service_id=None,
                        confidence=0.0,
                        summary=f"{definition.name} is {peak_severity}",
                    )
                )

        if status != "all":
            all_incidents = [incident for incident in all_incidents if incident.status == status]

        all_incidents.sort(key=lambda incident: incident.started_at, reverse=True)
        return all_incidents[:_MAX_INCIDENTS]

    async def latest_observed_at(self) -> datetime | None:
        """Latest observed at.
        
        Returns:
            The resulting value.
        """
        rows = await self._query(
            f"""
            SELECT MAX(observed_at) AS observed_at
            FROM `{self._table_id}`
            """
        )
        if not rows:
            return None
        return _ensure_utc(rows[0].get("observed_at"))

    async def snapshot_events_since(self, observed_after: datetime, limit: int = 200) -> list[SnapshotEvent]:
        """Snapshot events since.
        
        Args:
            observed_after: The observed after value.
            limit: The limit value.
        
        Returns:
            The resulting value.
        """
        rows = await self._query(
            f"""
            WITH filtered AS (
              SELECT
                service_key,
                run_id,
                check_key,
                status,
                observed_at,
                latency_ms
              FROM `{self._table_id}`
              WHERE observed_at > @observed_after
            ),
            deduped AS (
              SELECT
                service_key,
                run_id,
                check_key,
                status,
                observed_at,
                latency_ms
              FROM (
                SELECT
                  service_key,
                  run_id,
                  check_key,
                  status,
                  observed_at,
                  latency_ms,
                  ROW_NUMBER() OVER (
                    PARTITION BY service_key, run_id, check_key
                    ORDER BY observed_at DESC
                  ) AS row_num
                FROM filtered
              )
              WHERE row_num = 1
            ),
            run_observed AS (
              SELECT service_key, run_id, MAX(observed_at) AS run_observed_at
              FROM deduped
              GROUP BY service_key, run_id
            )
            SELECT
              deduped.service_key,
              deduped.run_id,
              run_observed.run_observed_at,
              deduped.check_key,
              deduped.status,
              deduped.observed_at,
              deduped.latency_ms
            FROM deduped
            JOIN run_observed
              ON run_observed.service_key = deduped.service_key
             AND run_observed.run_id = deduped.run_id
            ORDER BY run_observed.run_observed_at ASC, deduped.service_key ASC, deduped.check_key ASC
            """,
            [bigquery.ScalarQueryParameter("observed_after", "TIMESTAMP", observed_after)],
        )

        checks_by_run: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        run_observed_at: dict[tuple[str, str], datetime] = {}
        for row in rows:
            service_key = str(row["service_key"])
            run_id = str(row["run_id"])
            key = (service_key, run_id)
            checks_by_run[key].append(row)

            observed = _ensure_utc(row.get("run_observed_at"))
            if observed is not None:
                run_observed_at[key] = observed

        events: list[SnapshotEvent] = []
        for key, check_rows in checks_by_run.items():
            service_key, run_id = key
            definition = _service_definition_for_key(service_key)
            observed_at = run_observed_at.get(key, datetime.now(UTC))
            raw_score, snapshot_status = _compute_raw_score(definition, check_rows)
            events.append(
                SnapshotEvent(
                    snapshot_id=_stable_int(f"{service_key}:{run_id}"),
                    service_id=definition.service_id,
                    observed_at=observed_at,
                    status=snapshot_status,
                    raw_score=raw_score,
                    effective_score=raw_score,
                    dependency_impacted=False,
                    attribution_confidence=0.0,
                    probable_root_service_id=None,
                )
            )

        events.sort(key=lambda event: event.observed_at)
        return events[:limit]


@lru_cache
def get_bigquery_api_store() -> BigQueryApiStore:
    """Get bigquery api store.
    
    Returns:
        The resulting value.
    """
    settings = get_settings()
    client = bigquery.Client(project=settings.bigquery_project_id or None)
    return BigQueryApiStore(client)

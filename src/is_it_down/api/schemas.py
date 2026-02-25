"""Provide functionality for `is_it_down.api.schemas`."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ServiceSummary(BaseModel):
    """Represent `ServiceSummary`."""

    service_id: int
    slug: str
    name: str
    logo_url: str
    status: Literal["up", "degraded", "down"]
    raw_score: float
    effective_score: float
    observed_at: datetime
    dependency_impacted: bool
    attribution_confidence: float
    probable_root_service_id: int | None = None


class CheckRunSummary(BaseModel):
    """Represent `CheckRunSummary`."""

    check_key: str
    status: Literal["up", "degraded", "down"]
    observed_at: datetime
    latency_ms: int | None = None
    http_status: int | None = None
    error_code: str | None = None
    error_message: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RelatedServiceSummary(BaseModel):
    """Represent `RelatedServiceSummary`."""

    service_id: int
    slug: str
    name: str
    logo_url: str
    status: Literal["up", "degraded", "down"]


class ServiceDetail(BaseModel):
    """Represent `ServiceDetail`."""

    service_id: int
    slug: str
    name: str
    logo_url: str
    official_status_url: str | None = None
    description: str | None = None
    snapshot: ServiceSummary
    likely_related_services: list[RelatedServiceSummary] = Field(default_factory=list)
    latest_checks: list[CheckRunSummary]


class SnapshotPoint(BaseModel):
    """Represent `SnapshotPoint`."""

    observed_at: datetime
    status: Literal["up", "degraded", "down"]
    raw_score: float
    effective_score: float
    dependency_impacted: bool


class IncidentSummary(BaseModel):
    """Represent `IncidentSummary`."""

    incident_id: int
    service_id: int
    status: str
    started_at: datetime
    resolved_at: datetime | None = None
    peak_severity: str
    probable_root_service_id: int | None = None
    confidence: float
    summary: str | None = None


class BaseCheckUptimeSummary(BaseModel):
    """Represent `BaseCheckUptimeSummary`."""

    check_key: str
    uptime_percent: float
    health_score: float
    total_runs: int
    up_runs: int


class ServiceUptimeSummary(BaseModel):
    """Represent `ServiceUptimeSummary`."""

    service_id: int
    slug: str
    name: str
    logo_url: str
    uptime_percent: float
    health_score: float
    checks: list[BaseCheckUptimeSummary]


class CheckerTrendPoint(BaseModel):
    """Represent `CheckerTrendPoint`."""

    bucket_start: datetime
    check_key: str
    uptime_percent: float
    health_score: float
    total_runs: int
    up_runs: int


class ServiceCheckerTrendSummary(BaseModel):
    """Represent `ServiceCheckerTrendSummary`."""

    service_id: int
    slug: str
    name: str
    logo_url: str
    points: list[CheckerTrendPoint]

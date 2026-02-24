from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel


class ServiceSummary(BaseModel):
    service_id: int
    slug: str
    name: str
    status: Literal["up", "degraded", "down"]
    raw_score: float
    effective_score: float
    observed_at: datetime
    dependency_impacted: bool
    attribution_confidence: float
    probable_root_service_id: int | None = None


class CheckRunSummary(BaseModel):
    check_key: str
    status: Literal["up", "degraded", "down"]
    observed_at: datetime
    latency_ms: int | None = None
    http_status: int | None = None
    error_code: str | None = None
    error_message: str | None = None
    metadata: dict[str, Any] = {}


class ServiceDetail(BaseModel):
    service_id: int
    slug: str
    name: str
    description: str | None = None
    snapshot: ServiceSummary
    latest_checks: list[CheckRunSummary]


class SnapshotPoint(BaseModel):
    observed_at: datetime
    status: Literal["up", "degraded", "down"]
    raw_score: float
    effective_score: float
    dependency_impacted: bool


class IncidentSummary(BaseModel):
    incident_id: int
    service_id: int
    status: str
    started_at: datetime
    resolved_at: datetime | None = None
    peak_severity: str
    probable_root_service_id: int | None = None
    confidence: float
    summary: str | None = None

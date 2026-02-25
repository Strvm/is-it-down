from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

ServiceStatus = Literal["up", "degraded", "down"]
DependencyType = Literal["hard", "soft"]


class CheckResult(BaseModel):
    check_key: str
    status: ServiceStatus
    observed_at: datetime
    latency_ms: int | None = None
    http_status: int | None = None
    error_code: str | None = None
    error_message: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ServiceScoreResult(BaseModel):
    raw_score: float
    effective_score: float
    status: ServiceStatus
    dependency_impacted: bool
    attribution_confidence: float
    probable_root_service_id: int | None


class DependencySignal(BaseModel):
    dependency_service_id: int
    dependency_status: ServiceStatus
    dependency_type: DependencyType
    weight: float


class AttributionResult(BaseModel):
    dependency_impacted: bool
    probable_root_service_id: int | None
    attribution_confidence: float

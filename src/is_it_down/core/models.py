from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

ServiceStatus = Literal["up", "degraded", "down"]
DependencyType = Literal["hard", "soft"]


@dataclass(slots=True)
class CheckResult:
    check_key: str
    status: ServiceStatus
    observed_at: datetime
    latency_ms: int | None = None
    http_status: int | None = None
    error_code: str | None = None
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ServiceScoreResult:
    raw_score: float
    effective_score: float
    status: ServiceStatus
    dependency_impacted: bool
    attribution_confidence: float
    probable_root_service_id: int | None


@dataclass(slots=True)
class DependencySignal:
    dependency_service_id: int
    dependency_status: ServiceStatus
    dependency_type: DependencyType
    weight: float


@dataclass(slots=True)
class AttributionResult:
    dependency_impacted: bool
    probable_root_service_id: int | None
    attribution_confidence: float

"""Derived granularity helpers for service/check status reporting."""

from collections.abc import Mapping, Sequence
from typing import Any

from is_it_down.core.models import ServiceStatus

_DEGRADED_INDICATORS = {
    "degraded_performance",
    "minor",
    "major",
    "partial_outage",
}
_DOWN_INDICATORS = {
    "critical",
    "major_outage",
    "maintenance",
    "under_maintenance",
}
_MAJOR_SIGNAL_KEYS = (
    "major_open_incident_count",
    "major_impact_incident_count",
    "major_outage_component_count",
)
_DEGRADED_SIGNAL_KEYS = (
    "open_incident_count",
    "minor_impact_incident_count",
    "non_operational_component_count",
    "degraded_component_count",
    "unknown_component_count",
)


def score_band_from_score(score: float) -> str:
    """Return a stable score band for analytics and UI summaries.

    Args:
        score: Numeric health score in the 0-100 range.

    Returns:
        The resulting value.
    """
    if score >= 99:
        return "excellent"
    if score >= 95:
        return "healthy"
    if score >= 80:
        return "minor_issues"
    if score >= 60:
        return "degraded"
    if score >= 40:
        return "major_issues"
    return "critical"


def check_score_from_status(status: ServiceStatus, latency_ms: int | None) -> float:
    """Mirror checker score mapping from status and latency.

    Args:
        status: Canonical check status.
        latency_ms: Optional latency in milliseconds.

    Returns:
        The resulting value.
    """
    if status == "up":
        return 100.0

    if status == "down":
        return 0.0

    if latency_ms is None:
        return 60.0

    if latency_ms <= 500:
        return 80.0
    if latency_ms <= 1000:
        return 65.0
    return 45.0


def severity_level_from_score(score: float) -> int:
    """Return an integer severity (0 best, 5 worst) from a score.

    Args:
        score: Numeric health score in the 0-100 range.

    Returns:
        The resulting value.
    """
    if score >= 99:
        return 0
    if score >= 95:
        return 1
    if score >= 80:
        return 2
    if score >= 60:
        return 3
    if score >= 40:
        return 4
    return 5


def derive_check_status_detail(
    *,
    status: ServiceStatus,
    http_status: int | None,
    latency_ms: int | None,
    error_code: str | None,
    metadata: Mapping[str, Any] | None,
) -> str:
    """Derive a granular check status label from available run context.

    Args:
        status: Canonical check status.
        http_status: Optional HTTP status observed for the check.
        latency_ms: Optional latency in milliseconds.
        error_code: Optional execution error code.
        metadata: Optional check metadata payload.

    Returns:
        The resulting value.
    """
    normalized_error = (error_code or "").strip().upper()
    if normalized_error == "TIMEOUT":
        return "timeout"
    if normalized_error == "PROXY_CONFIGURATION_ERROR":
        return "proxy_error"
    if normalized_error:
        return "check_error"

    if http_status is not None:
        if http_status == 429:
            return "rate_limited"
        if http_status >= 500:
            return "server_error"
        if http_status in {401, 403}:
            return "auth_challenge"
        if http_status >= 400:
            return "client_error"

    metadata_dict = metadata or {}
    indicator = _normalized_indicator(metadata_dict)
    if indicator in _DOWN_INDICATORS:
        if indicator in {"maintenance", "under_maintenance"}:
            return "maintenance"
        return "major_outage"
    if indicator in _DEGRADED_INDICATORS:
        return "partial_outage"

    if _any_positive_signal(metadata_dict, _MAJOR_SIGNAL_KEYS):
        return "major_outage"
    if _any_positive_signal(metadata_dict, _DEGRADED_SIGNAL_KEYS):
        return "partial_outage"

    if status == "up":
        if latency_ms is not None and latency_ms >= 1_200:
            return "slow"
        return "operational"

    if status == "degraded":
        if latency_ms is not None and latency_ms >= 1_200:
            return "high_latency"
        return "degraded"

    return "outage"


def severity_level_from_check(status: ServiceStatus, status_detail: str) -> int:
    """Return check severity (0 best, 5 worst) from status and granular label.

    Args:
        status: Canonical check status.
        status_detail: Derived granular detail.

    Returns:
        The resulting value.
    """
    if status == "up":
        return 1 if status_detail == "slow" else 0

    if status == "degraded":
        if status_detail in {"partial_outage", "major_outage", "high_latency", "server_error"}:
            return 3
        return 2

    if status_detail in {"timeout", "major_outage", "outage"}:
        return 5
    return 4


def derive_service_status_detail(
    *,
    status: ServiceStatus,
    raw_score: float,
    check_details: Sequence[str] = (),
    dependency_impacted: bool = False,
) -> str:
    """Derive a service-level granular status label from score/check hints.

    Args:
        status: Canonical service status.
        raw_score: Service health score.
        check_details: Optional derived check detail labels.
        dependency_impacted: Whether attribution indicates dependency impact.

    Returns:
        The resulting value.
    """
    detail_set = {detail for detail in check_details if detail}

    if status == "up":
        detail = "fully_operational" if raw_score >= 99 else "operational"
    elif status == "degraded":
        if detail_set & {"major_outage", "outage", "timeout", "server_error"}:
            detail = "partial_outage"
        elif raw_score >= 85:
            detail = "minor_issues"
        else:
            detail = "degraded"
    else:
        if raw_score < 20 or detail_set & {"major_outage", "outage"}:
            detail = "major_outage"
        elif "timeout" in detail_set:
            detail = "timeouts"
        else:
            detail = "outage"

    if dependency_impacted and status != "up":
        return f"dependency_{detail}"
    return detail


def _normalized_indicator(metadata: Mapping[str, Any]) -> str | None:
    """Return normalized indicator from check metadata when available.

    Args:
        metadata: Check metadata payload.

    Returns:
        The resulting value.
    """
    for key in ("indicator", "largestatus", "large_status"):
        raw_value = metadata.get(key)
        if isinstance(raw_value, str):
            normalized = raw_value.strip().lower()
            if normalized:
                return normalized
    return None


def _any_positive_signal(metadata: Mapping[str, Any], keys: Sequence[str]) -> bool:
    """Return whether any metadata key has a positive numeric value.

    Args:
        metadata: Check metadata payload.
        keys: Candidate count keys.

    Returns:
        The resulting value.
    """
    for key in keys:
        raw_value = metadata.get(key)
        if isinstance(raw_value, bool):
            if raw_value:
                return True
            continue
        if isinstance(raw_value, (int, float)) and raw_value > 0:
            return True
    return False

from collections.abc import Mapping, Sequence

from is_it_down.core.models import CheckResult, ServiceStatus


def status_from_score(score: float) -> ServiceStatus:
    if score >= 95:
        return "up"
    if score >= 70:
        return "degraded"
    return "down"


def check_result_score(result: CheckResult) -> float:
    if result.status == "up":
        return 100.0

    if result.status == "down":
        return 0.0

    if result.latency_ms is None:
        return 60.0

    if result.latency_ms <= 500:
        return 80.0
    if result.latency_ms <= 1000:
        return 65.0
    return 45.0


def weighted_service_score(
    check_results: Sequence[CheckResult],
    weights_by_check: Mapping[str, float] | None = None,
) -> float:
    if not check_results:
        return 100.0

    numerator = 0.0
    denominator = 0.0
    for result in check_results:
        weight = 1.0
        if weights_by_check:
            weight = max(0.0, weights_by_check.get(result.check_key, 1.0))

        numerator += check_result_score(result) * weight
        denominator += weight

    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 2)

from datetime import UTC, datetime

from is_it_down.core.models import CheckResult
from is_it_down.core.scoring import check_result_score, status_from_score, weighted_service_score


def _result(check_key: str, status: str, latency_ms: int | None = None) -> CheckResult:
    return CheckResult(
        check_key=check_key,
        status=status,
        observed_at=datetime.now(UTC),
        latency_ms=latency_ms,
    )


def test_check_result_score_mapping() -> None:
    assert check_result_score(_result("a", "up")) == 100.0
    assert check_result_score(_result("a", "down")) == 0.0
    assert check_result_score(_result("a", "degraded", 400)) == 80.0
    assert check_result_score(_result("a", "degraded", 900)) == 65.0
    assert check_result_score(_result("a", "degraded", 1900)) == 45.0


def test_weighted_service_score_uses_weights() -> None:
    results = [
        _result("primary", "up"),
        _result("secondary", "down"),
    ]
    weights = {"primary": 3.0, "secondary": 1.0}
    assert weighted_service_score(results, weights) == 75.0


def test_status_thresholds() -> None:
    assert status_from_score(95) == "up"
    assert status_from_score(90) == "degraded"
    assert status_from_score(69.99) == "down"

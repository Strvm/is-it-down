from is_it_down.core.granularity import (
    check_score_from_status,
    derive_check_status_detail,
    derive_service_status_detail,
    score_band_from_score,
    severity_level_from_check,
    severity_level_from_score,
)


def test_score_band_and_severity_from_score() -> None:
    assert score_band_from_score(100.0) == "excellent"
    assert score_band_from_score(96.0) == "healthy"
    assert score_band_from_score(83.0) == "minor_issues"
    assert score_band_from_score(65.0) == "degraded"
    assert score_band_from_score(45.0) == "major_issues"
    assert score_band_from_score(10.0) == "critical"

    assert severity_level_from_score(100.0) == 0
    assert severity_level_from_score(95.0) == 1
    assert severity_level_from_score(80.0) == 2
    assert severity_level_from_score(60.0) == 3
    assert severity_level_from_score(40.0) == 4
    assert severity_level_from_score(0.0) == 5


def test_derive_check_status_detail_uses_errors_and_signals() -> None:
    assert (
        derive_check_status_detail(
            status="down",
            http_status=None,
            latency_ms=None,
            error_code="TIMEOUT",
            metadata={},
        )
        == "timeout"
    )

    assert (
        derive_check_status_detail(
            status="degraded",
            http_status=200,
            latency_ms=350,
            error_code=None,
            metadata={"indicator": "minor"},
        )
        == "partial_outage"
    )

    assert (
        derive_check_status_detail(
            status="down",
            http_status=200,
            latency_ms=210,
            error_code=None,
            metadata={"major_outage_component_count": 2},
        )
        == "major_outage"
    )

    assert (
        derive_check_status_detail(
            status="up",
            http_status=200,
            latency_ms=1500,
            error_code=None,
            metadata={},
        )
        == "slow"
    )


def test_check_score_and_check_severity_helpers() -> None:
    assert check_score_from_status("up", latency_ms=42) == 100.0
    assert check_score_from_status("down", latency_ms=42) == 0.0
    assert check_score_from_status("degraded", latency_ms=120) == 80.0
    assert check_score_from_status("degraded", latency_ms=900) == 65.0
    assert check_score_from_status("degraded", latency_ms=2_000) == 45.0

    assert severity_level_from_check("up", "operational") == 0
    assert severity_level_from_check("up", "slow") == 1
    assert severity_level_from_check("degraded", "degraded") == 2
    assert severity_level_from_check("degraded", "partial_outage") == 3
    assert severity_level_from_check("down", "major_outage") == 5


def test_derive_service_status_detail() -> None:
    assert derive_service_status_detail(status="up", raw_score=100.0) == "fully_operational"
    assert derive_service_status_detail(status="degraded", raw_score=88.0) == "minor_issues"
    assert derive_service_status_detail(status="down", raw_score=15.0) == "major_outage"

    assert (
        derive_service_status_detail(
            status="degraded",
            raw_score=82.0,
            check_details=("partial_outage",),
            dependency_impacted=True,
        )
        == "dependency_degraded"
    )

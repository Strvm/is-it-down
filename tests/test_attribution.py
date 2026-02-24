from is_it_down.core.attribution import attribute_dependency
from is_it_down.core.models import DependencySignal


def test_no_dependency_impact_when_service_up() -> None:
    output = attribute_dependency(
        "up",
        [
            DependencySignal(
                dependency_service_id=2,
                dependency_status="down",
                dependency_type="hard",
                weight=1.0,
            )
        ],
    )
    assert output.dependency_impacted is False
    assert output.probable_root_service_id is None
    assert output.attribution_confidence == 0.0


def test_dependency_impact_selects_highest_weighted_root() -> None:
    output = attribute_dependency(
        "down",
        [
            DependencySignal(
                dependency_service_id=10,
                dependency_status="degraded",
                dependency_type="soft",
                weight=0.6,
            ),
            DependencySignal(
                dependency_service_id=11,
                dependency_status="down",
                dependency_type="hard",
                weight=0.8,
            ),
        ],
    )

    assert output.dependency_impacted is True
    assert output.probable_root_service_id == 11
    assert 0.35 <= output.attribution_confidence <= 0.95

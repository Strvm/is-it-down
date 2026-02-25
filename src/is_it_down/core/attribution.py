"""Provide functionality for `is_it_down.core.attribution`."""

from collections.abc import Sequence

from is_it_down.core.models import AttributionResult, DependencySignal, ServiceStatus


def attribute_dependency(
    service_status: ServiceStatus,
    dependency_signals: Sequence[DependencySignal],
) -> AttributionResult:
    """Attribute dependency.
    
    Args:
        service_status: The service status value.
        dependency_signals: The dependency signals value.
    
    Returns:
        The resulting value.
    """
    if service_status == "up":
        return AttributionResult(
            dependency_impacted=False,
            probable_root_service_id=None,
            attribution_confidence=0.0,
        )

    impacted_dependencies = [
        signal
        for signal in dependency_signals
        if signal.dependency_status in {"degraded", "down"} and signal.weight > 0
    ]

    if not impacted_dependencies:
        return AttributionResult(
            dependency_impacted=False,
            probable_root_service_id=None,
            attribution_confidence=0.0,
        )

    def impact_score(signal: DependencySignal) -> float:
        """Impact score.
        
        Args:
            signal: The signal value.
        
        Returns:
            The resulting value.
        """
        severity_factor = 1.0 if signal.dependency_status == "down" else 0.6
        type_factor = 1.3 if signal.dependency_type == "hard" else 1.0
        return signal.weight * severity_factor * type_factor

    probable_root = max(impacted_dependencies, key=impact_score)
    best_score = impact_score(probable_root)

    confidence = min(0.95, 0.35 + best_score * 0.4)

    return AttributionResult(
        dependency_impacted=True,
        probable_root_service_id=probable_root.dependency_service_id,
        attribution_confidence=round(confidence, 3),
    )

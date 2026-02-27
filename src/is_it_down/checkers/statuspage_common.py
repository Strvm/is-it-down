"""Provide functionality for `is_it_down.checkers.statuspage_common`."""

from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

import httpx

from is_it_down.checkers.base import BaseCheck
from is_it_down.checkers.utils import (
    add_non_up_debug_metadata,
    apply_statuspage_indicator,
    json_dict_or_none,
    response_latency_ms,
    status_from_http,
)
from is_it_down.core.models import CheckResult, ServiceStatus

_NON_OPERATIONAL_COMPONENT_STATUSES = {
    "degraded_performance",
    "partial_outage",
    "major_outage",
    "under_maintenance",
    "maintenance",
}

_RESOLVED_INCIDENT_STATUSES = {
    "closed",
    "completed",
    "completed_verification",
    "cancelled",
    "postmortem_published",
    "resolved",
    "postmortem",
}

_NON_DISRUPTIVE_INCIDENT_STATUSES = {
    "scheduled",
}

_ERROR_SIGNAL_KEYS = (
    "error",
    "errors",
    "error_description",
    "error_message",
    "error_summary",
    "error_code",
    "errorCode",
    "message",
    "msg",
    "detail",
    "title",
    "status_code",
    "statusCode",
)

_ACCESS_CHALLENGE_MARKERS = (
    "just a moment",
    "verifying your connection",
    "attention required",
    "request blocked",
    "access denied",
    "why do i have to complete a captcha",
    "__cf_chl_",
    "cf-challenge",
    "cloudflare",
    "ray id",
    "security checkpoint",
    "security check",
    "bot detection",
)


def _status_rank(status: ServiceStatus) -> int:
    """Status rank.

    Args:
        status: The status value.

    Returns:
        The resulting value.
    """
    return {"up": 0, "degraded": 1, "down": 2}[status]


def _elevate_status(current: ServiceStatus, candidate: ServiceStatus) -> ServiceStatus:
    """Elevate status.

    Args:
        current: The current value.
        candidate: The candidate value.

    Returns:
        The resulting value.
    """
    if _status_rank(candidate) > _status_rank(current):
        return candidate
    return current


def _response_indicator_and_description(response_payload: Mapping[str, Any]) -> tuple[str | None, str | None, bool]:
    """Response indicator and description.

    Args:
        response_payload: The response payload value.

    Returns:
        The resulting value.
    """
    status_block = response_payload.get("status")
    if not isinstance(status_block, Mapping):
        return None, None, False

    indicator = status_block.get("indicator")
    description = status_block.get("description")

    normalized_indicator: str | None = None
    normalized_description: str | None = None

    if isinstance(indicator, str):
        normalized_indicator = indicator
    if isinstance(description, str):
        normalized_description = description

    return normalized_indicator, normalized_description, True


def _payload_contains_error_signal(payload: Mapping[str, Any]) -> bool:
    """Payload contains error signal.

    Args:
        payload: The payload value.

    Returns:
        The resulting value.
    """
    for key in _ERROR_SIGNAL_KEYS:
        raw_value = payload.get(key)
        if isinstance(raw_value, str) and raw_value.strip():
            return True
        if isinstance(raw_value, Mapping):
            return True
        if isinstance(raw_value, list):
            return True
        if isinstance(raw_value, (int, float)) and raw_value != 0:
            return True
    return False


def _normalized_status_value(raw_status: Any) -> str | None:
    """Normalize status value.

    Args:
        raw_status: The raw status value.

    Returns:
        The resulting value.
    """
    if not isinstance(raw_status, str):
        return None
    normalized = raw_status.strip().lower()
    if not normalized:
        return None
    return normalized


def _check_result(
    *,
    check_key: str,
    status: ServiceStatus,
    response: httpx.Response,
    metadata: dict[str, Any],
) -> CheckResult:
    """Check result.

    Args:
        check_key: The check key value.
        status: The status value.
        response: The response value.
        metadata: The metadata value.

    Returns:
        The resulting value.
    """
    return CheckResult(
        check_key=check_key,
        status=status,
        observed_at=datetime.now(UTC),
        latency_ms=response_latency_ms(response),
        http_status=response.status_code,
        metadata=metadata,
    )


class StatuspageStatusCheck(BaseCheck):
    """Represent `StatuspageStatusCheck`."""

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        """Run the entrypoint.

        Args:
            client: The client value.

        Returns:
            The resulting value.
        """
        response = await client.get(self.endpoint_key)
        status: ServiceStatus = status_from_http(response)
        metadata: dict[str, Any] = {}

        if response.is_success:
            payload = json_dict_or_none(response)
            if payload is None:
                status = "degraded"
                metadata["status_payload_present"] = False
            else:
                indicator, description, has_status_block = _response_indicator_and_description(payload)
                metadata["indicator"] = indicator
                metadata["status_block_present"] = has_status_block
                if description is not None:
                    metadata["description"] = description

                status = apply_statuspage_indicator(status, indicator)
                if indicator is None:
                    status = _elevate_status(status, "degraded")

        add_non_up_debug_metadata(metadata=metadata, status=status, response=response)
        return _check_result(check_key=self.check_key, status=status, response=response, metadata=metadata)


class StatuspageSummaryCheck(BaseCheck):
    """Represent `StatuspageSummaryCheck`."""

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        """Run the entrypoint.

        Args:
            client: The client value.

        Returns:
            The resulting value.
        """
        response = await client.get(self.endpoint_key)
        status: ServiceStatus = status_from_http(response)
        metadata: dict[str, Any] = {}

        if response.is_success:
            payload = json_dict_or_none(response)
            if payload is None:
                status = "degraded"
                metadata["summary_payload_present"] = False
            else:
                indicator, description, has_status_block = _response_indicator_and_description(payload)
                metadata["indicator"] = indicator
                metadata["status_block_present"] = has_status_block
                if description is not None:
                    metadata["description"] = description

                status = apply_statuspage_indicator(status, indicator)
                if indicator is None:
                    status = _elevate_status(status, "degraded")

                incidents = payload.get("incidents")
                if isinstance(incidents, list):
                    open_incidents = [
                        incident
                        for incident in incidents
                        if isinstance(incident, Mapping)
                        and _normalized_status_value(incident.get("status")) not in _RESOLVED_INCIDENT_STATUSES
                        and _normalized_status_value(incident.get("status")) not in _NON_DISRUPTIVE_INCIDENT_STATUSES
                    ]
                    major_open_incidents = [
                        incident
                        for incident in open_incidents
                        if incident.get("impact") in {"major", "critical"}
                    ]
                    critical_open_incidents = [
                        incident
                        for incident in open_incidents
                        if incident.get("impact") == "critical"
                    ]

                    metadata["open_incident_count"] = len(open_incidents)
                    metadata["major_open_incident_count"] = len(major_open_incidents)
                    metadata["critical_open_incident_count"] = len(critical_open_incidents)
                    metadata["open_incident_names"] = [
                        incident.get("name")
                        for incident in open_incidents[:5]
                        if isinstance(incident.get("name"), str)
                    ]

                    if critical_open_incidents:
                        status = _elevate_status(status, "down")
                    elif open_incidents:
                        status = _elevate_status(status, "degraded")
                else:
                    metadata["incidents_present"] = False

                components = payload.get("components")
                if isinstance(components, list):
                    non_operational_components = [
                        component
                        for component in components
                        if isinstance(component, Mapping)
                        and component.get("group") is not True
                        and component.get("status") in _NON_OPERATIONAL_COMPONENT_STATUSES
                    ]
                    major_outage_components = [
                        component
                        for component in non_operational_components
                        if component.get("status") == "major_outage"
                    ]

                    metadata["non_operational_component_count"] = len(non_operational_components)
                    metadata["major_outage_component_count"] = len(major_outage_components)

                    if major_outage_components:
                        status = _elevate_status(status, "down")
                    elif non_operational_components:
                        status = _elevate_status(status, "degraded")
                else:
                    metadata["components_present"] = False

        add_non_up_debug_metadata(metadata=metadata, status=status, response=response)
        return _check_result(check_key=self.check_key, status=status, response=response, metadata=metadata)


class HtmlMarkerCheck(BaseCheck):
    """Represent `HtmlMarkerCheck`."""

    expected_markers: tuple[str, ...] = ()
    required_content_type_fragment: str | None = "text/html"
    allow_access_challenge: bool = True

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        """Run the entrypoint.

        Args:
            client: The client value.

        Returns:
            The resulting value.
        """
        response = await client.get(self.endpoint_key)
        status: ServiceStatus = status_from_http(response)

        content_type = response.headers.get("content-type", "")
        body = response.text
        metadata: dict[str, Any] = {
            "content_type": content_type,
            "body_chars": len(body),
        }

        if self.allow_access_challenge and response.status_code in {401, 403, 429}:
            page_text = body.lower()
            challenge_markers = [
                marker
                for marker in _ACCESS_CHALLENGE_MARKERS
                if marker in page_text
            ]
            if challenge_markers:
                status = "up"
                metadata["access_challenge_detected"] = True
                metadata["access_challenge_markers"] = challenge_markers[:5]

        if response.is_success:
            if self.required_content_type_fragment and self.required_content_type_fragment not in content_type.lower():
                status = "degraded"

            if not body.strip():
                status = "degraded"

            if self.expected_markers:
                page_text = body.lower()
                marker_hits = {
                    marker: marker.lower() in page_text
                    for marker in self.expected_markers
                }
                metadata["marker_hits"] = marker_hits
                if not all(marker_hits.values()):
                    status = "degraded"

        add_non_up_debug_metadata(metadata=metadata, status=status, response=response)
        return _check_result(check_key=self.check_key, status=status, response=response, metadata=metadata)


class ApiAuthResponseCheck(BaseCheck):
    """Represent `ApiAuthResponseCheck`."""

    request_method = "GET"
    request_headers: dict[str, str] | None = None
    request_json: dict[str, Any] | None = None
    request_data: dict[str, Any] | None = None
    expected_http_statuses: tuple[int, ...] = (401, 403)
    require_error_signal = True

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        """Run the entrypoint.

        Args:
            client: The client value.

        Returns:
            The resulting value.
        """
        request_kwargs: dict[str, Any] = {}
        if self.request_headers is not None:
            request_kwargs["headers"] = self.request_headers
        if self.request_json is not None:
            request_kwargs["json"] = self.request_json
        if self.request_data is not None:
            request_kwargs["data"] = self.request_data

        response = await client.request(self.request_method, self.endpoint_key, **request_kwargs)
        status: ServiceStatus = status_from_http(response)
        metadata: dict[str, Any] = {
            "request_method": self.request_method,
            "expected_http_statuses": list(self.expected_http_statuses),
        }

        if response.status_code in self.expected_http_statuses:
            status = "up"
            payload = json_dict_or_none(response)
            if payload is None:
                metadata["json_payload_present"] = False
                text_payload_present = bool(response.text.strip())
                metadata["text_payload_present"] = text_payload_present
                metadata["error_signal_present"] = text_payload_present
                if self.require_error_signal and not text_payload_present:
                    status = "degraded"
            else:
                metadata["json_payload_present"] = True
                metadata["payload_keys"] = sorted(str(key) for key in payload)[:10]
                error_signal_present = _payload_contains_error_signal(payload)
                metadata["error_signal_present"] = error_signal_present
                if self.require_error_signal and not error_signal_present:
                    status = "degraded"
        elif response.is_success:
            status = "degraded"
            metadata["unexpected_success"] = True

        add_non_up_debug_metadata(metadata=metadata, status=status, response=response)
        return _check_result(check_key=self.check_key, status=status, response=response, metadata=metadata)

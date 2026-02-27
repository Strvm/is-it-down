"""Provide functionality for `is_it_down.checkers.services.paypal`."""

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

import httpx

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import (
    ApiAuthResponseCheck,
    HtmlMarkerCheck,
)
from is_it_down.checkers.utils import (
    add_non_up_debug_metadata,
    json_dict_or_none,
    response_latency_ms,
    status_from_http,
)
from is_it_down.core.models import CheckResult

_PAYPAL_CLOSED_EVENT_STATES = {"closed", "resolved", "completed", "cancelled"}
_PAYPAL_DOWN_STATUS_MARKERS = ("critical", "major outage", "outage", "unavailable", "down")
_PAYPAL_DEGRADED_STATUS_MARKERS = ("degraded", "partial outage", "maintenance", "issue")
_PAYPAL_DOWN_SEVERITY_MARKERS = ("critical", "major", "severe", "disruption")


def _normalized_text(value: Any) -> str | None:
    """Normalize text.

    Args:
        value: The value value.

    Returns:
        The resulting value.
    """
    if not isinstance(value, str):
        return None
    normalized = " ".join(value.split()).strip().lower()
    if not normalized:
        return None
    return normalized


class PayPalStatusPageCheck(BaseCheck):
    """Represent `PayPalStatusPageCheck`."""

    check_key = "paypal_status_page"
    endpoint_key = "https://www.paypal-status.com/api/v1/components"
    interval_seconds = 60
    timeout_seconds = 8.0
    weight = 0.3

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        """Run the entrypoint.

        Args:
            client: The client value.

        Returns:
            The resulting value.
        """
        response = await client.get(self.endpoint_key)
        status = status_from_http(response)
        metadata: dict[str, Any] = {}

        if response.is_success:
            payload = json_dict_or_none(response)
            if payload is None:
                status = "degraded"
                metadata["components_payload_present"] = False
            else:
                metadata["components_payload_present"] = True
                result = payload.get("result")
                if not isinstance(result, list):
                    status = "degraded"
                    metadata["components_present"] = False
                else:
                    metadata["components_present"] = True
                    metadata["component_count"] = len(result)

                    degraded_components = 0
                    down_components = 0
                    unknown_components = 0
                    for component in result:
                        if not isinstance(component, dict):
                            continue
                        component_status_block = component.get("status")
                        if not isinstance(component_status_block, dict):
                            unknown_components += 1
                            continue

                        component_status = component_status_block.get("production")
                        normalized_component_status = _normalized_text(component_status)
                        if normalized_component_status is None:
                            unknown_components += 1
                            continue
                        if "operational" in normalized_component_status:
                            continue
                        if any(marker in normalized_component_status for marker in _PAYPAL_DOWN_STATUS_MARKERS):
                            down_components += 1
                        elif any(marker in normalized_component_status for marker in _PAYPAL_DEGRADED_STATUS_MARKERS):
                            degraded_components += 1
                        else:
                            degraded_components += 1

                    metadata["unknown_component_status_count"] = unknown_components
                    metadata["degraded_component_count"] = degraded_components
                    metadata["down_component_count"] = down_components

                    if down_components > 0:
                        status = "down"
                    elif degraded_components > 0:
                        status = "degraded"

        add_non_up_debug_metadata(metadata=metadata, status=status, response=response)
        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=response_latency_ms(response),
            http_status=response.status_code,
            metadata=metadata,
        )


class PayPalSummaryCheck(BaseCheck):
    """Represent `PayPalSummaryCheck`."""

    check_key = "paypal_summary"
    endpoint_key = "https://www.paypal-status.com/api/v1/events?s=true"
    interval_seconds = 60
    timeout_seconds = 8.0
    weight = 0.25

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        """Run the entrypoint.

        Args:
            client: The client value.

        Returns:
            The resulting value.
        """
        response = await client.get(self.endpoint_key)
        status = status_from_http(response)
        metadata: dict[str, Any] = {}

        if response.is_success:
            payload = json_dict_or_none(response)
            if payload is None:
                status = "degraded"
                metadata["events_payload_present"] = False
            else:
                metadata["events_payload_present"] = True
                result = payload.get("result")
                if not isinstance(result, list):
                    status = "degraded"
                    metadata["events_present"] = False
                else:
                    metadata["events_present"] = True
                    open_events: list[dict[str, Any]] = []
                    major_open_incidents = 0

                    for event in result:
                        if not isinstance(event, dict):
                            continue
                        if _normalized_text(event.get("environment")) not in {None, "production"}:
                            continue

                        event_state = _normalized_text(event.get("state"))
                        if event_state in _PAYPAL_CLOSED_EVENT_STATES:
                            continue

                        open_events.append(event)
                        event_type = _normalized_text(event.get("type")) or ""
                        event_severity = _normalized_text(event.get("severity")) or ""
                        if event_type == "incident" and any(
                            marker in event_severity for marker in _PAYPAL_DOWN_SEVERITY_MARKERS
                        ):
                            major_open_incidents += 1

                    metadata["open_event_count"] = len(open_events)
                    metadata["major_open_incident_count"] = major_open_incidents
                    metadata["open_event_names"] = [
                        event.get("summary")
                        for event in open_events[:5]
                        if isinstance(event.get("summary"), str)
                    ]

                    if major_open_incidents > 0:
                        status = "down"
                    elif open_events:
                        status = "degraded"

        add_non_up_debug_metadata(metadata=metadata, status=status, response=response)
        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=response_latency_ms(response),
            http_status=response.status_code,
            metadata=metadata,
        )


class PayPalHomepageCheck(HtmlMarkerCheck):
    """Represent `PayPalHomepageCheck`."""

    check_key = "paypal_homepage"
    endpoint_key = "https://www.paypal.com/us/home"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("paypal",)


class PayPalDocsCheck(HtmlMarkerCheck):
    """Represent `PayPalDocsCheck`."""

    check_key = "paypal_docs"
    endpoint_key = "https://developer.paypal.com/api/rest/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("paypal",)


class PayPalApiAuthCheck(ApiAuthResponseCheck):
    """Represent `PayPalApiAuthCheck`."""

    check_key = "paypal_api_auth"
    endpoint_key = "https://api-m.paypal.com/v1/reporting/balances"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    request_method = "GET"
    request_headers = {"Accept": "application/json"}
    request_json = None
    request_data = None
    expected_http_statuses = (401, 403)


class PayPalServiceChecker(BaseServiceChecker):
    """Represent `PayPalServiceChecker`."""

    service_key = "paypal"
    logo_url = "https://cdn.simpleicons.org/paypal"
    official_uptime = "https://www.paypal-status.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            PayPalStatusPageCheck(),
            PayPalSummaryCheck(),
            PayPalHomepageCheck(),
            PayPalDocsCheck(),
            PayPalApiAuthCheck(),
        ]

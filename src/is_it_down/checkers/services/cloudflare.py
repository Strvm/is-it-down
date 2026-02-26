"""Provide functionality for `is_it_down.checkers.services.cloudflare`."""

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

import httpx

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.utils import (
    add_non_up_debug_metadata,
    apply_statuspage_indicator,
    json_dict_or_none,
    response_latency_ms,
    status_from_http,
)
from is_it_down.core.models import CheckResult

_NON_OPERATIONAL_COMPONENT_STATUSES = {
    "degraded_performance",
    "partial_outage",
    "major_outage",
    "under_maintenance",
}


def _status_rank(status: str) -> int:
    """Status rank.
    
    Args:
        status: The status value.
    
    Returns:
        The resulting value.
    """
    return {"up": 0, "degraded": 1, "down": 2}.get(status, 0)


def _elevate_status(current: str, candidate: str) -> str:
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


def _score_cloudflare_api_auth_response(response: httpx.Response) -> tuple[str, dict[str, Any]]:
    """Score cloudflare api auth response.

    Args:
        response: The response value.

    Returns:
        The resulting value.
    """
    status = status_from_http(response)
    metadata: dict[str, Any] = {"expected_http_statuses": [400, 401, 403]}

    if response.status_code in {400, 401, 403}:
        status = "up"
        payload = json_dict_or_none(response)
        if payload is None:
            metadata["error_payload_present"] = False
        else:
            metadata["error_payload_present"] = True
            success = payload.get("success")
            metadata["success"] = success
            if success is True:
                status = "degraded"

            errors = payload.get("errors")
            if isinstance(errors, list):
                metadata["error_count"] = len(errors)
                if errors:
                    first_error = errors[0]
                    if isinstance(first_error, dict):
                        metadata["error_code"] = first_error.get("code")
                        metadata["error_message"] = first_error.get("message")
            else:
                metadata["error_count"] = 0
    elif response.is_success:
        status = "degraded"
        metadata["unexpected_success"] = True

    return status, metadata


class CloudflareStatusAPICheck(BaseCheck):
    """Represent `CloudflareStatusAPICheck`."""

    check_key = "cloudflare_status_api"
    endpoint_key = "https://www.cloudflarestatus.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 4.0
    weight = 0.2

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
                metadata["summary_payload_present"] = False
            else:
                summary_status = payload.get("status")
                indicator: str | None = None
                description: str | None = None
                if isinstance(summary_status, dict):
                    raw_indicator = summary_status.get("indicator")
                    raw_description = summary_status.get("description")
                    if isinstance(raw_indicator, str):
                        indicator = raw_indicator
                    if isinstance(raw_description, str):
                        description = raw_description
                else:
                    status = "degraded"

                status = apply_statuspage_indicator(status, indicator)
                metadata["indicator"] = indicator
                if description is not None:
                    metadata["description"] = description
                if indicator is None:
                    status = _elevate_status(status, "degraded")

                incidents = payload.get("incidents")
                open_incidents: list[dict[str, Any]] = []
                major_impact_count = 0
                minor_impact_count = 0
                if isinstance(incidents, list):
                    for incident in incidents:
                        if not isinstance(incident, dict):
                            continue
                        incident_status = incident.get("status")
                        if incident_status in {"resolved", "postmortem"}:
                            continue
                        open_incidents.append(incident)

                        impact = incident.get("impact")
                        if impact in {"major", "critical"}:
                            major_impact_count += 1
                        elif impact in {"minor"}:
                            minor_impact_count += 1

                metadata["open_incident_count"] = len(open_incidents)
                metadata["major_impact_incident_count"] = major_impact_count
                metadata["minor_impact_incident_count"] = minor_impact_count
                metadata["open_incident_names"] = [
                    incident.get("name")
                    for incident in open_incidents[:5]
                    if isinstance(incident.get("name"), str)
                ]

                if major_impact_count > 0:
                    status = _elevate_status(status, "down")
                elif len(open_incidents) > 0:
                    status = _elevate_status(status, "degraded")

                components = payload.get("components")
                non_operational_components = 0
                major_outage_components = 0
                if isinstance(components, list):
                    for component in components:
                        if not isinstance(component, dict):
                            continue
                        if component.get("group") is True:
                            continue

                        component_status = component.get("status")
                        if component_status not in _NON_OPERATIONAL_COMPONENT_STATUSES:
                            continue

                        non_operational_components += 1
                        if component_status == "major_outage":
                            major_outage_components += 1

                metadata["non_operational_component_count"] = non_operational_components
                metadata["major_outage_component_count"] = major_outage_components
                if major_outage_components > 0:
                    status = _elevate_status(status, "down")
                elif non_operational_components > 0:
                    status = _elevate_status(status, "degraded")

        add_non_up_debug_metadata(metadata=metadata, status=status, response=response)

        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=response_latency_ms(response),
            http_status=response.status_code,
            metadata=metadata,
        )


class CloudflareApiAuthCheck(BaseCheck):
    """Represent `CloudflareApiAuthCheck`."""

    check_key = "cloudflare_api_auth"
    endpoint_key = "https://api.cloudflare.com/client/v4/user/tokens/verify"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.4

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        """Run the entrypoint.

        Args:
            client: The client value.

        Returns:
            The resulting value.
        """
        response = await client.get(self.endpoint_key, headers={"Accept": "application/json"})
        status, metadata = _score_cloudflare_api_auth_response(response)
        add_non_up_debug_metadata(metadata=metadata, status=status, response=response)

        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=response_latency_ms(response),
            http_status=response.status_code,
            metadata=metadata,
        )


class CloudflareTraceCheck(BaseCheck):
    """Represent `CloudflareTraceCheck`."""

    check_key = "cloudflare_trace"
    endpoint_key = "https://www.cloudflare.com/cdn-cgi/trace"
    interval_seconds = 60
    timeout_seconds = 5.0

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        """Run the entrypoint.

        Args:
            client: The client value.

        Returns:
            The resulting value.
        """
        response = await client.get(self.endpoint_key)
        status = status_from_http(response)

        content_type = response.headers.get("content-type", "")
        metadata: dict[str, Any] = {"content_type": content_type}

        if response.is_success:
            trace_fields: dict[str, str] = {}
            for line in response.text.splitlines():
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                normalized_key = key.strip()
                if not normalized_key:
                    continue
                trace_fields[normalized_key] = value.strip()

            required_keys = {"fl", "h", "ip", "ts", "visit_scheme", "colo"}
            missing_required_keys = sorted(key for key in required_keys if key not in trace_fields)

            metadata["trace_key_count"] = len(trace_fields)
            metadata["trace_keys_sample"] = sorted(trace_fields.keys())[:10]
            metadata["colo"] = trace_fields.get("colo")
            metadata["visit_scheme"] = trace_fields.get("visit_scheme")
            metadata["missing_required_keys"] = missing_required_keys

            if "text/plain" not in content_type.lower():
                status = "degraded"
            if not trace_fields:
                status = "degraded"
            if missing_required_keys:
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


class CloudflareServiceChecker(BaseServiceChecker):
    """Represent `CloudflareServiceChecker`."""

    service_key = "cloudflare"
    logo_url = "https://cdn.simpleicons.org/cloudflare"
    official_uptime = "https://www.cloudflarestatus.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.
        
        Returns:
            The resulting value.
        """
        return [
            CloudflareStatusAPICheck(),
            CloudflareApiAuthCheck(),
            CloudflareTraceCheck(),
        ]

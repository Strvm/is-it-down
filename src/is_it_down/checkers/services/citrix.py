"""Provide functionality for `is_it_down.checkers.services.citrix`."""

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

import httpx

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.utils import (
    add_non_up_debug_metadata,
    json_dict_or_none,
    response_latency_ms,
    safe_get,
    status_from_http,
)
from is_it_down.core.models import CheckResult


class CitrixStatusCheck(BaseCheck):
    """Represent `CitrixStatusCheck`."""

    check_key = "citrix_status"
    endpoint_key = "https://status.cloud.com/api/statuses"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.35

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        """Run the entrypoint.

        Args:
            client: The client value.

        Returns:
            The resulting value.
        """
        response = await safe_get(client, self.endpoint_key)
        status = status_from_http(response)
        metadata: dict[str, Any] = {}

        if response.is_success:
            payload = json_dict_or_none(response)
            if payload is None:
                status = "degraded"
            else:
                groups = payload.get("groups")
                if not isinstance(groups, list):
                    status = "degraded"
                else:
                    service_status_codes: list[int] = []
                    for group in groups:
                        if not isinstance(group, dict):
                            continue
                        services = group.get("services")
                        if not isinstance(services, list):
                            continue
                        for service in services:
                            if not isinstance(service, dict):
                                continue
                            raw_status = service.get("status")
                            if isinstance(raw_status, int):
                                service_status_codes.append(raw_status)

                    metadata["service_count"] = len(service_status_codes)
                    degraded_count = sum(1 for code in service_status_codes if code == 2)
                    down_count = sum(1 for code in service_status_codes if code >= 3)
                    metadata["degraded_service_count"] = degraded_count
                    metadata["down_service_count"] = down_count

                    if down_count > 0:
                        status = "down"
                    elif degraded_count > 0:
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


class CitrixSummaryCheck(BaseCheck):
    """Represent `CitrixSummaryCheck`."""

    check_key = "citrix_summary"
    endpoint_key = "https://status.cloud.com/api/incidents"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        """Run the entrypoint.

        Args:
            client: The client value.

        Returns:
            The resulting value.
        """
        response = await safe_get(client, self.endpoint_key)
        status = status_from_http(response)
        metadata: dict[str, Any] = {}

        if response.is_success:
            incidents: list[Any] = []
            try:
                parsed = response.json()
                if isinstance(parsed, list):
                    incidents = parsed
            except ValueError:
                status = "degraded"

            metadata["incident_count"] = len(incidents)
            if incidents:
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


class CitrixComponentsCheck(BaseCheck):
    """Represent `CitrixComponentsCheck`."""

    check_key = "citrix_components"
    endpoint_key = "https://status.cloud.com/api/history"
    interval_seconds = 60
    timeout_seconds = 5.0

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        """Run the entrypoint.

        Args:
            client: The client value.

        Returns:
            The resulting value.
        """
        response = await safe_get(client, self.endpoint_key)
        status = status_from_http(response)
        metadata: dict[str, Any] = {}

        if response.is_success:
            groups: list[Any] = []
            try:
                parsed = response.json()
                if isinstance(parsed, list):
                    groups = parsed
            except ValueError:
                status = "degraded"

            service_count = 0
            for group in groups:
                if not isinstance(group, dict):
                    continue
                services = group.get("services")
                if isinstance(services, list):
                    service_count += len([service for service in services if isinstance(service, dict)])
            metadata["history_group_count"] = len(groups)
            metadata["history_service_count"] = service_count

        add_non_up_debug_metadata(metadata=metadata, status=status, response=response)
        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=response_latency_ms(response),
            http_status=response.status_code,
            metadata=metadata,
        )


class CitrixHomepageCheck(BaseCheck):
    """Represent `CitrixHomepageCheck`."""

    check_key = "citrix_homepage"
    endpoint_key = "https://www.citrix.com/"
    interval_seconds = 60
    timeout_seconds = 5.0

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        """Run the entrypoint.

        Args:
            client: The client value.

        Returns:
            The resulting value.
        """
        response = await safe_get(client, self.endpoint_key)
        status = status_from_http(response)
        content_type = response.headers.get("content-type", "")
        metadata: dict[str, Any] = {"content_type": content_type, "body_chars": len(response.text)}

        if response.is_success and "text/html" not in content_type.lower():
            status = "degraded"
        if response.is_success and not response.text.strip():
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


class CitrixRobotsCheck(BaseCheck):
    """Represent `CitrixRobotsCheck`."""

    check_key = "citrix_robots"
    endpoint_key = "https://www.citrix.com/robots.txt"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.1

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        """Run the entrypoint.

        Args:
            client: The client value.

        Returns:
            The resulting value.
        """
        response = await safe_get(client, self.endpoint_key)
        status = status_from_http(response)
        content_type = response.headers.get("content-type", "")
        metadata: dict[str, Any] = {"content_type": content_type, "body_chars": len(response.text)}

        if response.is_success and len(response.text.strip()) == 0:
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


class CitrixServiceChecker(BaseServiceChecker):
    """Represent `CitrixServiceChecker`."""

    service_key = "citrix"
    logo_url = "https://cdn.simpleicons.org/citrix"
    official_uptime = "https://status.cloud.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            CitrixStatusCheck(),
            CitrixSummaryCheck(),
            CitrixComponentsCheck(),
            CitrixHomepageCheck(),
            CitrixRobotsCheck(),
        ]

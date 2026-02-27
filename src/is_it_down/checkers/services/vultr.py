"""Provide functionality for `is_it_down.checkers.services.vultr`."""

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

import httpx

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.utils import (
    add_non_up_debug_metadata,
    json_dict_or_none,
    response_latency_ms,
    status_from_http,
)
from is_it_down.core.models import CheckResult


class VultrStatusPageCheck(BaseCheck):
    """Represent `VultrStatusPageCheck`."""

    check_key = "vultr_status_page"
    endpoint_key = "https://status.vultr.com/status.json"
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
        response = await client.get(self.endpoint_key)
        status = status_from_http(response)
        metadata: dict[str, Any] = {}

        if response.is_success:
            payload = json_dict_or_none(response)
            if payload is None:
                status = "degraded"
            else:
                service_alerts = payload.get("service_alerts")
                unresolved_alerts = 0
                if isinstance(service_alerts, list):
                    unresolved_alerts += sum(
                        1
                        for alert in service_alerts
                        if isinstance(alert, dict) and str(alert.get("status", "")).strip().lower() != "resolved"
                    )

                regions = payload.get("regions")
                unresolved_region_alerts = 0
                if isinstance(regions, dict):
                    for region in regions.values():
                        if not isinstance(region, dict):
                            continue
                        alerts = region.get("alerts")
                        if not isinstance(alerts, list):
                            continue
                        unresolved_region_alerts += sum(
                            1
                            for alert in alerts
                            if isinstance(alert, dict) and str(alert.get("status", "")).strip().lower() != "resolved"
                        )

                metadata["unresolved_service_alert_count"] = unresolved_alerts
                metadata["unresolved_region_alert_count"] = unresolved_region_alerts

                total_unresolved = unresolved_alerts + unresolved_region_alerts
                if total_unresolved > 0:
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


class VultrHomepageCheck(BaseCheck):
    """Represent `VultrHomepageCheck`."""

    check_key = "vultr_homepage"
    endpoint_key = "https://www.vultr.com/"
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


class VultrDocsCheck(BaseCheck):
    """Represent `VultrDocsCheck`."""

    check_key = "vultr_docs"
    endpoint_key = "https://docs.vultr.com/"
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


class VultrBlogCheck(BaseCheck):
    """Represent `VultrBlogCheck`."""

    check_key = "vultr_blog"
    endpoint_key = "https://www.vultr.com/news/"
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


class VultrRobotsCheck(BaseCheck):
    """Represent `VultrRobotsCheck`."""

    check_key = "vultr_robots"
    endpoint_key = "https://www.vultr.com/robots.txt"
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
        response = await client.get(self.endpoint_key)
        status = status_from_http(response)
        content_type = response.headers.get("content-type", "")
        metadata: dict[str, Any] = {
            "content_type": content_type,
            "body_chars": len(response.text),
        }

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


class VultrServiceChecker(BaseServiceChecker):
    """Represent `VultrServiceChecker`."""

    service_key = "vultr"
    logo_url = "https://cdn.simpleicons.org/vultr"
    official_uptime = "https://status.vultr.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            VultrStatusPageCheck(),
            VultrHomepageCheck(),
            VultrDocsCheck(),
            VultrBlogCheck(),
            VultrRobotsCheck(),
        ]

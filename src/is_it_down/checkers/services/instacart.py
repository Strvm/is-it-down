"""Provide functionality for `is_it_down.checkers.services.instacart`."""

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
    safe_get,
    status_from_http,
)
from is_it_down.core.models import CheckResult


class InstacartStatusCheck(BaseCheck):
    """Represent `InstacartStatusCheck`."""

    check_key = "instacart_status"
    endpoint_key = "https://status.instacart.com/api/v2/status.json"
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
                status_block = payload.get("status")
                indicator: str | None = None
                if isinstance(status_block, dict):
                    raw_indicator = status_block.get("indicator")
                    raw_description = status_block.get("description")
                    if isinstance(raw_indicator, str):
                        indicator = raw_indicator
                    if isinstance(raw_description, str):
                        metadata["description"] = raw_description
                else:
                    status = "degraded"

                metadata["indicator"] = indicator
                status = apply_statuspage_indicator(status, indicator)
                if indicator is None:
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


class InstacartSummaryCheck(BaseCheck):
    """Represent `InstacartSummaryCheck`."""

    check_key = "instacart_summary"
    endpoint_key = "https://status.instacart.com/api/v2/summary.json"
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
            payload = json_dict_or_none(response)
            if payload is None:
                status = "degraded"
            else:
                components = payload.get("components")
                incidents = payload.get("incidents")
                metadata["components_count"] = len(components) if isinstance(components, list) else None
                metadata["incidents_count"] = len(incidents) if isinstance(incidents, list) else None

        add_non_up_debug_metadata(metadata=metadata, status=status, response=response)
        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=response_latency_ms(response),
            http_status=response.status_code,
            metadata=metadata,
        )


class InstacartComponentsCheck(BaseCheck):
    """Represent `InstacartComponentsCheck`."""

    check_key = "instacart_components"
    endpoint_key = "https://status.instacart.com/api/v2/components.json"
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
            payload = json_dict_or_none(response)
            if payload is None:
                status = "degraded"
            else:
                components = payload.get("components")
                metadata["components_count"] = len(components) if isinstance(components, list) else None

        add_non_up_debug_metadata(metadata=metadata, status=status, response=response)
        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=response_latency_ms(response),
            http_status=response.status_code,
            metadata=metadata,
        )


class InstacartHomepageCheck(BaseCheck):
    """Represent `InstacartHomepageCheck`."""

    check_key = "instacart_homepage"
    endpoint_key = "https://www.instacart.com/"
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


class InstacartRobotsCheck(BaseCheck):
    """Represent `InstacartRobotsCheck`."""

    check_key = "instacart_robots"
    endpoint_key = "https://www.instacart.com/robots.txt"
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


class InstacartServiceChecker(BaseServiceChecker):
    """Represent `InstacartServiceChecker`."""

    service_key = "instacart"
    logo_url = "https://cdn.simpleicons.org/instacart"
    official_uptime = "https://status.instacart.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            InstacartStatusCheck(),
            InstacartSummaryCheck(),
            InstacartComponentsCheck(),
            InstacartHomepageCheck(),
            InstacartRobotsCheck(),
        ]

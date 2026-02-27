"""Provide functionality for `is_it_down.checkers.services.quickbooks`."""

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


class QuickbooksStatusPageCheck(BaseCheck):
    """Represent `QuickbooksStatusPageCheck`."""

    check_key = "quickbooks_status_page"
    endpoint_key = "https://status.developer.intuit.com/api/v2/status.json"
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


class QuickbooksHomepageCheck(BaseCheck):
    """Represent `QuickbooksHomepageCheck`."""

    check_key = "quickbooks_homepage"
    endpoint_key = "https://quickbooks.intuit.com/"
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


class QuickbooksDocsCheck(BaseCheck):
    """Represent `QuickbooksDocsCheck`."""

    check_key = "quickbooks_docs"
    endpoint_key = "https://developer.intuit.com/app/developer/qbo/docs/learn/rest-api-features"
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


class QuickbooksBlogCheck(BaseCheck):
    """Represent `QuickbooksBlogCheck`."""

    check_key = "quickbooks_blog"
    endpoint_key = "https://quickbooks.intuit.com/r/"
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


class QuickbooksRobotsCheck(BaseCheck):
    """Represent `QuickbooksRobotsCheck`."""

    check_key = "quickbooks_robots"
    endpoint_key = "https://quickbooks.intuit.com/robots.txt"
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


class QuickbooksServiceChecker(BaseServiceChecker):
    """Represent `QuickbooksServiceChecker`."""

    service_key = "quickbooks"
    logo_url = "https://cdn.simpleicons.org/quickbooks"
    official_uptime = "https://status.developer.intuit.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            QuickbooksStatusPageCheck(),
            QuickbooksHomepageCheck(),
            QuickbooksDocsCheck(),
            QuickbooksBlogCheck(),
            QuickbooksRobotsCheck(),
        ]

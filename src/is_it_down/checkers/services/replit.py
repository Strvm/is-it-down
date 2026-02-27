"""Provide functionality for `is_it_down.checkers.services.replit`."""

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


class ReplitStatusPageCheck(BaseCheck):
    """Represent `ReplitStatusPageCheck`."""

    check_key = "replit_status_page"
    endpoint_key = "https://status.replit.com/api/v1/status"
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
                page = payload.get("page")
                page_state: str | None = None
                if isinstance(page, dict):
                    raw_state = page.get("state")
                    if isinstance(raw_state, str):
                        page_state = raw_state
                    state_text = page.get("state_text")
                    if isinstance(state_text, str):
                        metadata["state_text"] = state_text
                if page_state is None:
                    status = "degraded"
                else:
                    normalized = page_state.strip().lower()
                    metadata["page_state"] = normalized
                    if normalized in {"operational", "up"}:
                        status = "up"
                    elif normalized in {"major_outage", "down"}:
                        status = "down"
                    else:
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


class ReplitHomepageCheck(BaseCheck):
    """Represent `ReplitHomepageCheck`."""

    check_key = "replit_homepage"
    endpoint_key = "https://replit.com/"
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


class ReplitDocsCheck(BaseCheck):
    """Represent `ReplitDocsCheck`."""

    check_key = "replit_docs"
    endpoint_key = "https://docs.replit.com/"
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


class ReplitBlogCheck(BaseCheck):
    """Represent `ReplitBlogCheck`."""

    check_key = "replit_blog"
    endpoint_key = "https://blog.replit.com/"
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


class ReplitRobotsCheck(BaseCheck):
    """Represent `ReplitRobotsCheck`."""

    check_key = "replit_robots"
    endpoint_key = "https://replit.com/robots.txt"
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


class ReplitServiceChecker(BaseServiceChecker):
    """Represent `ReplitServiceChecker`."""

    service_key = "replit"
    logo_url = "https://cdn.simpleicons.org/replit"
    official_uptime = "https://status.replit.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            ReplitStatusPageCheck(),
            ReplitHomepageCheck(),
            ReplitDocsCheck(),
            ReplitBlogCheck(),
            ReplitRobotsCheck(),
        ]

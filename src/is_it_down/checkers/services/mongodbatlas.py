"""Provide functionality for `is_it_down.checkers.services.mongodbatlas`."""

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


class MongodbAtlasStatusPageCheck(BaseCheck):
    """Represent `MongodbAtlasStatusPageCheck`."""

    check_key = "mongodbatlas_status_page"
    endpoint_key = "https://status.mongodb.com/api/v2/status.json"
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


class MongodbAtlasHomepageCheck(BaseCheck):
    """Represent `MongodbAtlasHomepageCheck`."""

    check_key = "mongodbatlas_homepage"
    endpoint_key = "https://www.mongodb.com/atlas"
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


class MongodbAtlasDocsCheck(BaseCheck):
    """Represent `MongodbAtlasDocsCheck`."""

    check_key = "mongodbatlas_docs"
    endpoint_key = "https://www.mongodb.com/docs/atlas/"
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


class MongodbAtlasBlogCheck(BaseCheck):
    """Represent `MongodbAtlasBlogCheck`."""

    check_key = "mongodbatlas_blog"
    endpoint_key = "https://www.mongodb.com/company/blog"
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


class MongodbAtlasRobotsCheck(BaseCheck):
    """Represent `MongodbAtlasRobotsCheck`."""

    check_key = "mongodbatlas_robots"
    endpoint_key = "https://www.mongodb.com/atlas/robots.txt"
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


class MongodbAtlasServiceChecker(BaseServiceChecker):
    """Represent `MongodbAtlasServiceChecker`."""

    service_key = "mongodbatlas"
    logo_url = "https://cdn.simpleicons.org/mongodb"
    official_uptime = "https://status.mongodb.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            MongodbAtlasStatusPageCheck(),
            MongodbAtlasHomepageCheck(),
            MongodbAtlasDocsCheck(),
            MongodbAtlasBlogCheck(),
            MongodbAtlasRobotsCheck(),
        ]

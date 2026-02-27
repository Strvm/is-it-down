"""Provide functionality for `is_it_down.checkers.services.dockerhub`."""

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


class DockerHubStatusPageCheck(BaseCheck):
    """Represent `DockerHubStatusPageCheck`."""

    check_key = "dockerhub_status_page"
    endpoint_key = "https://www.dockerstatus.com/1.0/status/533c6539221ae15e3f000031"
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
                result = payload.get("result")
                overall_status_code: int | None = None
                if isinstance(result, dict):
                    status_overall = result.get("status_overall")
                    if isinstance(status_overall, dict):
                        raw_status_code = status_overall.get("status_code")
                        if isinstance(raw_status_code, int):
                            overall_status_code = raw_status_code
                        overall_status_label = status_overall.get("status")
                        if isinstance(overall_status_label, str):
                            metadata["overall_status"] = overall_status_label
                if overall_status_code is None:
                    status = "degraded"
                else:
                    metadata["overall_status_code"] = overall_status_code
                    if overall_status_code == 100:
                        status = "up"
                    elif overall_status_code >= 300:
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


class DockerHubHomepageCheck(BaseCheck):
    """Represent `DockerHubHomepageCheck`."""

    check_key = "dockerhub_homepage"
    endpoint_key = "https://www.docker.com/"
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


class DockerHubDocsCheck(BaseCheck):
    """Represent `DockerHubDocsCheck`."""

    check_key = "dockerhub_docs"
    endpoint_key = "https://docs.docker.com/"
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


class DockerHubBlogCheck(BaseCheck):
    """Represent `DockerHubBlogCheck`."""

    check_key = "dockerhub_blog"
    endpoint_key = "https://www.docker.com/blog/"
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


class DockerHubRobotsCheck(BaseCheck):
    """Represent `DockerHubRobotsCheck`."""

    check_key = "dockerhub_robots"
    endpoint_key = "https://www.docker.com/robots.txt"
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


class DockerHubServiceChecker(BaseServiceChecker):
    """Represent `DockerHubServiceChecker`."""

    service_key = "dockerhub"
    logo_url = "https://img.logo.dev/docker.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://www.dockerstatus.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            DockerHubStatusPageCheck(),
            DockerHubHomepageCheck(),
            DockerHubDocsCheck(),
            DockerHubBlogCheck(),
            DockerHubRobotsCheck(),
        ]

"""Provide functionality for `is_it_down.checkers.services.discourse`."""

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


class DiscourseStatusCheck(BaseCheck):
    """Represent `DiscourseStatusCheck`."""

    check_key = "discourse_status"
    endpoint_key = "https://status.discourse.org/1.0/status/5e2141ce30dc5c04b3ac32fc"
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


class DiscourseSummaryCheck(BaseCheck):
    """Represent `DiscourseSummaryCheck`."""

    check_key = "discourse_summary"
    endpoint_key = "https://status.discourse.org/1.0/status/5e2141ce30dc5c04b3ac32fc"
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
                result = payload.get("result")
                services: list[dict[str, Any]] = []
                if isinstance(result, dict):
                    raw_services = result.get("status")
                    if isinstance(raw_services, list):
                        services = [item for item in raw_services if isinstance(item, dict)]

                metadata["service_count"] = len(services)
                degraded_services = [
                    service
                    for service in services
                    if isinstance(service.get("status_code"), int) and service.get("status_code") != 100
                ]
                metadata["degraded_service_count"] = len(degraded_services)

                if any(
                    isinstance(service.get("status_code"), int) and service.get("status_code") >= 300
                    for service in degraded_services
                ):
                    status = "down"
                elif degraded_services:
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


class DiscourseComponentsCheck(BaseCheck):
    """Represent `DiscourseComponentsCheck`."""

    check_key = "discourse_components"
    endpoint_key = "https://status.discourse.org/1.0/status/5e2141ce30dc5c04b3ac32fc"
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
                result = payload.get("result")
                services: list[dict[str, Any]] = []
                if isinstance(result, dict):
                    raw_services = result.get("status")
                    if isinstance(raw_services, list):
                        services = [item for item in raw_services if isinstance(item, dict)]

                container_count = 0
                degraded_container_count = 0
                for service in services:
                    containers = service.get("containers")
                    if not isinstance(containers, list):
                        continue
                    for container in containers:
                        if not isinstance(container, dict):
                            continue
                        container_count += 1
                        container_status_code = container.get("status_code")
                        if isinstance(container_status_code, int) and container_status_code != 100:
                            degraded_container_count += 1

                metadata["container_count"] = container_count
                metadata["degraded_container_count"] = degraded_container_count

                if degraded_container_count > 0:
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


class DiscourseHomepageCheck(BaseCheck):
    """Represent `DiscourseHomepageCheck`."""

    check_key = "discourse_homepage"
    endpoint_key = "https://www.discourse.org/"
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


class DiscourseRobotsCheck(BaseCheck):
    """Represent `DiscourseRobotsCheck`."""

    check_key = "discourse_robots"
    endpoint_key = "https://www.discourse.org/robots.txt"
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


class DiscourseServiceChecker(BaseServiceChecker):
    """Represent `DiscourseServiceChecker`."""

    service_key = "discourse"
    logo_url = "https://cdn.simpleicons.org/discourse"
    official_uptime = "https://status.discourse.org/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            DiscourseStatusCheck(),
            DiscourseSummaryCheck(),
            DiscourseComponentsCheck(),
            DiscourseHomepageCheck(),
            DiscourseRobotsCheck(),
        ]

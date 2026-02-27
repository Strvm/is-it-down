"""Provide functionality for `is_it_down.checkers.services.docker`."""

import re
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any
from xml.etree import ElementTree

import httpx

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import (
    ApiAuthResponseCheck,
    HtmlMarkerCheck,
)
from is_it_down.checkers.utils import (
    add_non_up_debug_metadata,
    response_latency_ms,
    status_from_http,
)
from is_it_down.core.models import CheckResult

_DOCKER_STATUS_PAGE_ID = "533c6539221ae15e3f000031"
_DOCKER_STATUS_TEXT_PATTERN = re.compile(r'id="statusbar_text"[^>]*>\s*([^<]+?)\s*<', re.IGNORECASE)
_DOCKER_DEGRADED_STATUS_MARKERS = ("degraded", "partial outage", "maintenance")
_DOCKER_DOWN_STATUS_MARKERS = ("major outage", "critical outage")


class DockerStatusPageCheck(BaseCheck):
    """Represent `DockerStatusPageCheck`."""

    check_key = "docker_status_page"
    endpoint_key = f"https://www.dockerstatus.com/pages/{_DOCKER_STATUS_PAGE_ID}/rss"
    interval_seconds = 60
    timeout_seconds = 5.0
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
        metadata: dict[str, Any] = {
            "content_type": response.headers.get("content-type", ""),
        }

        if response.is_success:
            try:
                root = ElementTree.fromstring(response.text)
            except ElementTree.ParseError:
                status = "degraded"
                metadata["rss_parse_error"] = True
            else:
                channel = root.find("channel")
                if channel is None:
                    status = "degraded"
                    metadata["channel_present"] = False
                else:
                    metadata["channel_present"] = True
                    title = channel.findtext("title")
                    items = channel.findall("item")
                    metadata["title"] = title
                    metadata["item_count"] = len(items)
                    if items:
                        latest_item_title = items[0].findtext("title")
                        if isinstance(latest_item_title, str):
                            metadata["latest_item_title"] = latest_item_title
                    if not isinstance(title, str) or not title.strip():
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


class DockerSummaryCheck(BaseCheck):
    """Represent `DockerSummaryCheck`."""

    check_key = "docker_summary"
    endpoint_key = f"https://www.dockerstatus.com/pages/{_DOCKER_STATUS_PAGE_ID}"
    interval_seconds = 60
    timeout_seconds = 5.0
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
        metadata: dict[str, Any] = {
            "content_type": response.headers.get("content-type", ""),
        }

        if response.is_success:
            body = response.text
            content_type = metadata["content_type"]
            if "text/html" not in content_type.lower():
                status = "degraded"

            status_match = _DOCKER_STATUS_TEXT_PATTERN.search(body)
            if status_match is None:
                status = "degraded"
                metadata["status_text_present"] = False
            else:
                raw_status_text = status_match.group(1)
                normalized_status_text = " ".join(raw_status_text.split()).lower()
                metadata["status_text_present"] = True
                metadata["status_text"] = raw_status_text

                if "all systems operational" in normalized_status_text:
                    status = "up"
                elif any(marker in normalized_status_text for marker in _DOCKER_DOWN_STATUS_MARKERS):
                    status = "down"
                elif any(marker in normalized_status_text for marker in _DOCKER_DEGRADED_STATUS_MARKERS):
                    status = "degraded"
                else:
                    status = "degraded"
                    metadata["status_text_unrecognized"] = True

        add_non_up_debug_metadata(metadata=metadata, status=status, response=response)
        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=response_latency_ms(response),
            http_status=response.status_code,
            metadata=metadata,
        )


class DockerHomepageCheck(HtmlMarkerCheck):
    """Represent `DockerHomepageCheck`."""

    check_key = "docker_homepage"
    endpoint_key = "https://hub.docker.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("docker",)


class DockerDocsCheck(HtmlMarkerCheck):
    """Represent `DockerDocsCheck`."""

    check_key = "docker_docs"
    endpoint_key = "https://docs.docker.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("docker",)


class DockerApiAuthCheck(ApiAuthResponseCheck):
    """Represent `DockerApiAuthCheck`."""

    check_key = "docker_api_auth"
    endpoint_key = "https://hub.docker.com/v2/user/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    request_method = "GET"
    request_headers = {"Accept": "application/json"}
    request_json = None
    request_data = None
    expected_http_statuses = (401, 403)


class DockerServiceChecker(BaseServiceChecker):
    """Represent `DockerServiceChecker`."""

    service_key = "docker"
    logo_url = "https://cdn.simpleicons.org/docker"
    official_uptime = "https://www.dockerstatus.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            DockerStatusPageCheck(),
            DockerSummaryCheck(),
            DockerHomepageCheck(),
            DockerDocsCheck(),
            DockerApiAuthCheck(),
        ]

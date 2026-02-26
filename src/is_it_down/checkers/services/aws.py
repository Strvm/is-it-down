"""Provide functionality for `is_it_down.checkers.services.aws`."""

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any
from xml.etree import ElementTree

import httpx

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.utils import (
    add_non_up_debug_metadata,
    json_dict_or_none,
    response_latency_ms,
    status_from_http,
)
from is_it_down.core.models import CheckResult


class AwsStatusRssCheck(BaseCheck):
    """Represent `AwsStatusRssCheck`."""

    check_key = "aws_status_rss"
    endpoint_key = "https://status.aws.amazon.com/rss/all.rss"
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
                    metadata["title"] = title
                    items = channel.findall("item")
                    metadata["item_count"] = len(items)
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


class AwsStsAuthCheck(BaseCheck):
    """Represent `AwsStsAuthCheck`."""

    check_key = "aws_sts_auth"
    endpoint_key = "https://sts.amazonaws.com/?Action=GetCallerIdentity&Version=2011-06-15"
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
        response = await client.get(self.endpoint_key, headers={"Accept": "application/json"})
        status = status_from_http(response)
        metadata: dict[str, Any] = {
            "expected_http_statuses": [403],
            "content_type": response.headers.get("content-type", ""),
        }

        if response.status_code == 403:
            status = "up"
            payload = json_dict_or_none(response)
            if payload is None:
                metadata["error_payload_present"] = False
            else:
                metadata["error_payload_present"] = True
                error = payload.get("Error")
                metadata["error_block_present"] = isinstance(error, dict)
                if isinstance(error, dict):
                    metadata["error_code"] = error.get("Code")
                    metadata["error_message"] = error.get("Message")
        elif response.is_success:
            status = "degraded"
            metadata["unexpected_success"] = True

        add_non_up_debug_metadata(metadata=metadata, status=status, response=response)

        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=response_latency_ms(response),
            http_status=response.status_code,
            metadata=metadata,
        )


class AwsHomepageCheck(BaseCheck):
    """Represent `AwsHomepageCheck`."""

    check_key = "aws_homepage"
    endpoint_key = "https://aws.amazon.com/"
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
        metadata: dict[str, Any] = {
            "content_type": content_type,
            "cache_control": response.headers.get("cache-control", ""),
        }

        if response.is_success and "text/html" not in content_type.lower():
            status = "degraded"
        if response.is_success:
            metadata["body_chars"] = len(response.text)
            if not response.text.strip():
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


class AwsServiceChecker(BaseServiceChecker):
    """Represent `AwsServiceChecker`."""

    service_key = "aws"
    logo_url = "https://cdn.simpleicons.org/amazonwebservices"
    official_uptime = "https://status.aws.amazon.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            AwsStatusRssCheck(),
            AwsStsAuthCheck(),
            AwsHomepageCheck(),
        ]

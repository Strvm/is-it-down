"""Provide functionality for `is_it_down.checkers.services.stripe`."""

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


class StripeStatusPageCheck(BaseCheck):
    """Represent `StripeStatusPageCheck`."""

    check_key = "stripe_status_page"
    endpoint_key = "https://status.stripe.com/current"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.4

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        """Run."""
        response = await client.get(self.endpoint_key)
        status = status_from_http(response)

        metadata: dict[str, Any] = {}
        if response.is_success:
            payload = json_dict_or_none(response)
            if payload is None:
                status = "degraded"
            else:
                large_status = payload.get("largestatus")
                component_statuses = payload.get("statuses")
                message = payload.get("message")

                metadata["largestatus"] = large_status
                if isinstance(component_statuses, dict):
                    metadata["component_statuses"] = component_statuses
                    metadata["non_up_components"] = [key for key, value in component_statuses.items() if value != "up"]
                else:
                    status = "degraded"

                if isinstance(message, str):
                    metadata["message"] = message

                if large_status == "up":
                    status = "up"
                elif large_status in {"down", "critical", "maintenance"}:
                    status = "down"
                elif large_status in {"degraded", "minor", "major"}:
                    status = "degraded"
                elif isinstance(large_status, str):
                    status = apply_statuspage_indicator(status, large_status)
                    if status == "up":
                        status = "degraded"
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


class StripeApiUnauthenticatedCheck(BaseCheck):
    """Represent `StripeApiUnauthenticatedCheck`."""

    check_key = "stripe_api_unauthenticated"
    endpoint_key = "https://api.stripe.com/v1/charges?limit=1"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.35

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        """Run."""
        response = await client.get(self.endpoint_key)
        status = status_from_http(response)

        metadata: dict[str, Any] = {"expected_http_status": 401}
        if response.status_code == 401:
            status = "up"
            payload = json_dict_or_none(response)
            if payload is None:
                metadata["error_payload_present"] = False
            else:
                error = payload.get("error")
                metadata["error_payload_present"] = isinstance(error, dict)
                if isinstance(error, dict):
                    error_type = error.get("type")
                    error_code = error.get("code")
                    metadata["error_type"] = error_type
                    metadata["error_code"] = error_code
                    if not isinstance(error_type, str) or not error_type:
                        status = "degraded"
                else:
                    status = "degraded"
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


class StripeJsV3Check(BaseCheck):
    """Represent `StripeJsV3Check`."""

    check_key = "stripe_js_v3"
    endpoint_key = "https://js.stripe.com/v3/"
    interval_seconds = 60
    timeout_seconds = 5.0

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        """Run."""
        response = await client.get(self.endpoint_key)
        status = status_from_http(response)

        content_type = response.headers.get("content-type", "")
        metadata: dict[str, Any] = {
            "content_type": content_type,
            "cache_control": response.headers.get("cache-control", ""),
        }

        if response.is_success and "javascript" not in content_type.lower():
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


class StripeServiceChecker(BaseServiceChecker):
    """Represent `StripeServiceChecker`."""

    service_key = "stripe"
    logo_url = "https://cdn.simpleicons.org/stripe"
    official_uptime = "https://status.stripe.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks."""
        return [
            StripeStatusPageCheck(),
            StripeApiUnauthenticatedCheck(),
            StripeJsV3Check(),
        ]

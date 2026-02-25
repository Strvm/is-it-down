from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

import httpx

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.utils import (
    add_non_up_debug_metadata,
    apply_statuspage_indicator,
    response_latency_ms,
    status_from_http,
)
from is_it_down.core.models import CheckResult


def _json_dict(response: httpx.Response) -> dict[str, Any] | None:
    try:
        payload = response.json()
    except ValueError:
        return None
    if not isinstance(payload, dict):
        return None
    return payload


class NetlifyStatusPageCheck(BaseCheck):
    check_key = "netlify_status_page"
    endpoint_key = "https://www.netlifystatus.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.4

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        response = await client.get(self.endpoint_key)
        status = status_from_http(response)
        metadata: dict[str, Any] = {}

        if response.is_success:
            payload = _json_dict(response)
            if payload is None:
                status = "degraded"
            else:
                status_block = payload.get("status")
                indicator: str | None = None
                description: str | None = None

                if isinstance(status_block, dict):
                    raw_indicator = status_block.get("indicator")
                    raw_description = status_block.get("description")
                    if isinstance(raw_indicator, str):
                        indicator = raw_indicator
                    if isinstance(raw_description, str):
                        description = raw_description
                else:
                    status = "degraded"

                metadata["indicator"] = indicator
                if description is not None:
                    metadata["description"] = description

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


class NetlifyApiAuthCheck(BaseCheck):
    check_key = "netlify_api_auth"
    endpoint_key = "https://api.netlify.com/api/v1/sites"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.35

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        response = await client.get(self.endpoint_key, headers={"Accept": "application/json"})
        status = status_from_http(response)
        metadata: dict[str, Any] = {"expected_http_statuses": [401, 403]}

        if response.status_code in {401, 403}:
            status = "up"
            payload = _json_dict(response)
            if payload is None:
                metadata["error_payload_present"] = False
            else:
                message = payload.get("message")
                code = payload.get("code")
                metadata["error_message"] = message
                metadata["error_code"] = code
                if message is not None and not isinstance(message, str):
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


class NetlifyHomepageCheck(BaseCheck):
    check_key = "netlify_homepage"
    endpoint_key = "https://www.netlify.com/"
    interval_seconds = 60
    timeout_seconds = 5.0

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
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


class NetlifyServiceChecker(BaseServiceChecker):
    service_key = "netlify"
    logo_url = "https://cdn.simpleicons.org/netlify"
    official_uptime = "https://www.netlifystatus.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        return [
            NetlifyStatusPageCheck(),
            NetlifyApiAuthCheck(),
            NetlifyHomepageCheck(),
        ]

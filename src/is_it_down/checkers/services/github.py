from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any, Literal

import httpx

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.core.models import CheckResult

ServiceStatus = Literal["up", "degraded", "down"]


def _latency_ms(response: httpx.Response) -> int:
    return int(response.elapsed.total_seconds() * 1000)


def _status_from_http(response: httpx.Response) -> ServiceStatus:
    if response.status_code >= 500:
        return "down"
    if response.status_code >= 400:
        return "degraded"
    return "up"


class GitHubApiRateLimitCheck(BaseCheck):
    check_key = "github_api_rate_limit"
    endpoint_key = "https://api.github.com/rate_limit"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 1.2

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        response = await client.get(
            self.endpoint_key,
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )

        status = _status_from_http(response)
        metadata: dict[str, Any] = {}

        if response.is_success:
            payload = response.json()
            core_rate = payload.get("resources", {}).get("core", {})
            remaining = core_rate.get("remaining")
            limit = core_rate.get("limit")
            metadata["core_remaining"] = remaining
            metadata["core_limit"] = limit

            if not isinstance(limit, int):
                status = "degraded"

        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=_latency_ms(response),
            http_status=response.status_code,
            metadata=metadata,
        )


class GitHubStatusPageCheck(BaseCheck):
    check_key = "github_status_page"
    endpoint_key = "https://www.githubstatus.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 1.0

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        response = await client.get(self.endpoint_key)
        status = _status_from_http(response)

        metadata: dict[str, Any] = {}
        if response.is_success:
            payload = response.json()
            indicator = payload.get("status", {}).get("indicator", "unknown")
            metadata["indicator"] = indicator

            if indicator in {"minor", "major"}:
                status = "degraded"
            elif indicator in {"critical", "maintenance"}:
                status = "down"

        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=_latency_ms(response),
            http_status=response.status_code,
            metadata=metadata,
        )


class GitHubHomepageCheck(BaseCheck):
    check_key = "github_homepage"
    endpoint_key = "https://github.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.8

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        response = await client.get(self.endpoint_key)
        status = _status_from_http(response)

        content_type = response.headers.get("content-type", "")
        metadata: dict[str, Any] = {"content_type": content_type}

        if response.is_success and "text/html" not in content_type:
            status = "degraded"

        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=_latency_ms(response),
            http_status=response.status_code,
            metadata=metadata,
        )


class GitHubServiceChecker(BaseServiceChecker):
    service_key = "github"
    official_uptime = "https://www.githubstatus.com/"
    dependencies: Sequence[str] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        return [
            GitHubApiRateLimitCheck(),
            GitHubStatusPageCheck(),
            GitHubHomepageCheck(),
        ]

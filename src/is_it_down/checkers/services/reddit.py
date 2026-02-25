from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

import httpx

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.services.cloudflare import CloudflareServiceChecker
from is_it_down.checkers.utils import (
    add_non_up_debug_metadata,
    apply_statuspage_indicator,
    response_latency_ms,
    status_from_http,
)
from is_it_down.core.models import CheckResult


class RedditStatusPageCheck(BaseCheck):
    check_key = "reddit_status_page"
    endpoint_key = "https://www.redditstatus.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.4

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        response = await client.get(self.endpoint_key)
        status = status_from_http(response)

        metadata: dict[str, Any] = {}
        if response.is_success:
            payload = response.json()
            indicator = payload.get("status", {}).get("indicator", "unknown")
            metadata["indicator"] = indicator
            status = apply_statuspage_indicator(status, indicator)
        add_non_up_debug_metadata(metadata=metadata, status=status, response=response)

        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=response_latency_ms(response),
            http_status=response.status_code,
            metadata=metadata,
        )


class RedditAllHotCheck(BaseCheck):
    check_key = "reddit_all_hot"
    endpoint_key = "https://www.reddit.com/r/all/hot.json?limit=1"
    interval_seconds = 60
    timeout_seconds = 5.0

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        response = await client.get(self.endpoint_key)
        status = status_from_http(response)

        metadata: dict[str, Any] = {}
        if response.is_success:
            payload = response.json()
            children = payload.get("data", {}).get("children", [])
            metadata["post_count"] = len(children)
            if not isinstance(children, list):
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


class RedditSubredditAboutCheck(BaseCheck):
    check_key = "reddit_subreddit_about"
    endpoint_key = "https://www.reddit.com/r/reddit/about.json"
    interval_seconds = 60
    timeout_seconds = 5.0

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        response = await client.get(self.endpoint_key)
        status = status_from_http(response)

        metadata: dict[str, Any] = {}
        if response.is_success:
            payload = response.json()
            subreddit = payload.get("data", {}).get("display_name")
            metadata["display_name"] = subreddit
            if not isinstance(subreddit, str) or not subreddit:
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


class RedditServiceChecker(BaseServiceChecker):
    service_key = "reddit"
    logo_url = "https://cdn.simpleicons.org/reddit"
    official_uptime = "https://www.redditstatus.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = (CloudflareServiceChecker,)

    def build_checks(self) -> Sequence[BaseCheck]:
        return [
            RedditStatusPageCheck(),
            RedditAllHotCheck(),
            RedditSubredditAboutCheck(),
        ]

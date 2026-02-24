from collections.abc import Sequence
from datetime import UTC, datetime

import httpx

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.services.cloudflare import CloudflareServiceChecker
from is_it_down.checkers.utils import apply_statuspage_indicator, response_latency_ms, status_from_http
from is_it_down.core.models import CheckResult


class DiscordGatewayCheck(BaseCheck):
    check_key = "discord_gateway"
    endpoint_key = "https://discord.com/api/v9/gateway"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.5

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        response = await client.get(self.endpoint_key)
        status = status_from_http(response)

        gateway_url: str | None = None
        if response.is_success:
            payload = response.json()
            gateway_url = payload.get("url")
            if not gateway_url:
                status = "degraded"

        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=response_latency_ms(response),
            http_status=response.status_code,
            metadata={"gateway_url_present": bool(gateway_url)},
        )


class DiscordCDNAvatarCheck(BaseCheck):
    check_key = "discord_cdn_avatar"
    endpoint_key = "https://cdn.discordapp.com/embed/avatars/0.png"
    interval_seconds = 60
    timeout_seconds = 5.0

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        response = await client.get(self.endpoint_key)
        status = status_from_http(response)

        content_type = response.headers.get("content-type", "")
        if response.is_success and not content_type.startswith("image/"):
            status = "degraded"

        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=response_latency_ms(response),
            http_status=response.status_code,
            metadata={"content_type": content_type},
        )


class DiscordStatusPageCheck(BaseCheck):
    check_key = "discord_status_page"
    endpoint_key = "https://discordstatus.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        response = await client.get(self.endpoint_key)
        status = status_from_http(response)

        indicator = "unknown"
        if response.is_success:
            payload = response.json()
            indicator = payload.get("status", {}).get("indicator", "unknown")
            status = apply_statuspage_indicator(status, indicator)

        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=response_latency_ms(response),
            http_status=response.status_code,
            metadata={"indicator": indicator},
        )


class DiscordServiceChecker(BaseServiceChecker):
    service_key = "discord"
    official_uptime = "https://discordstatus.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = (CloudflareServiceChecker,)

    def build_checks(self) -> Sequence[BaseCheck]:
        return [DiscordGatewayCheck(), DiscordCDNAvatarCheck(), DiscordStatusPageCheck()]

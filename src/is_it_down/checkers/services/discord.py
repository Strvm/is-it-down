from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Literal

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


class DiscordGatewayCheck(BaseCheck):
    check_key = "discord_gateway"
    endpoint_key = "https://discord.com/api/v9/gateway"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 1.2

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        response = await client.get(self.endpoint_key)
        status = _status_from_http(response)

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
            latency_ms=_latency_ms(response),
            http_status=response.status_code,
            metadata={"gateway_url_present": bool(gateway_url)},
        )


class DiscordCDNAvatarCheck(BaseCheck):
    check_key = "discord_cdn_avatar"
    endpoint_key = "https://cdn.discordapp.com/embed/avatars/0.png"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 1.0

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        response = await client.get(self.endpoint_key)
        status = _status_from_http(response)

        content_type = response.headers.get("content-type", "")
        if response.is_success and not content_type.startswith("image/"):
            status = "degraded"

        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=_latency_ms(response),
            http_status=response.status_code,
            metadata={"content_type": content_type},
        )


class DiscordStatusPageCheck(BaseCheck):
    check_key = "discord_status_page"
    endpoint_key = "https://discordstatus.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.8

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        response = await client.get(self.endpoint_key)
        status = _status_from_http(response)

        indicator = "unknown"
        if response.is_success:
            payload = response.json()
            indicator = payload.get("status", {}).get("indicator", "unknown")
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
            metadata={"indicator": indicator},
        )


class DiscordServiceChecker(BaseServiceChecker):
    service_key = "discord"
    official_uptime = "https://discordstatus.com/"
    dependencies: Sequence[str] = ("cloudflare",)

    def build_checks(self) -> Sequence[BaseCheck]:
        return [DiscordGatewayCheck(), DiscordCDNAvatarCheck(), DiscordStatusPageCheck()]

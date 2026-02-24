from collections.abc import Sequence
from datetime import UTC, datetime

import httpx

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.core.models import CheckResult


class CloudflareStatusAPICheck(BaseCheck):
    check_key = "cloudflare_status_api"
    endpoint_key = "https://www.cloudflarestatus.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 4.0
    weight = 1.0

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        response = await client.get(self.endpoint_key)
        response.raise_for_status()

        payload = response.json()
        indicator = payload.get("status", {}).get("indicator", "unknown")

        status = "up"
        if indicator in {"minor", "major"}:
            status = "degraded"
        elif indicator in {"critical", "maintenance", "none"}:
            status = "down" if indicator in {"critical", "maintenance"} else "up"

        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=int(response.elapsed.total_seconds() * 1000),
            http_status=response.status_code,
            metadata={"indicator": indicator},
        )


class CloudflareServiceChecker(BaseServiceChecker):
    service_key = "cloudflare"
    official_uptime = "https://www.cloudflarestatus.com/"
    dependencies: Sequence[str] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        return [CloudflareStatusAPICheck()]

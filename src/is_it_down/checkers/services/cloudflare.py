from collections.abc import Sequence
from datetime import UTC, datetime

import httpx

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.utils import (
    add_non_up_debug_metadata,
    apply_statuspage_indicator,
    response_latency_ms,
)
from is_it_down.core.models import CheckResult


class CloudflareStatusAPICheck(BaseCheck):
    check_key = "cloudflare_status_api"
    endpoint_key = "https://www.cloudflarestatus.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 4.0

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        response = await client.get(self.endpoint_key)
        response.raise_for_status()

        payload = response.json()
        indicator = payload.get("status", {}).get("indicator", "unknown")

        status = apply_statuspage_indicator("up", indicator)
        metadata = {"indicator": indicator}
        add_non_up_debug_metadata(metadata=metadata, status=status, response=response)

        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=response_latency_ms(response),
            http_status=response.status_code,
            metadata=metadata,
        )


class CloudflareServiceChecker(BaseServiceChecker):
    service_key = "cloudflare"
    logo_url = "https://cdn.simpleicons.org/cloudflare"
    official_uptime = "https://www.cloudflarestatus.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        return [CloudflareStatusAPICheck()]

# Service Checker Patterns

Use this as a copy/paste starting point when adding a new service checker.

## Minimal Skeleton

```python
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

import httpx

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.services.cloudflare import CloudflareServiceChecker
from is_it_down.checkers.utils import (
    add_non_up_debug_metadata,
    response_latency_ms,
    status_from_http,
)
from is_it_down.core.models import CheckResult


class ExampleHealthCheck(BaseCheck):
    check_key = "example_health"
    endpoint_key = "https://api.example.com/health"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.5

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        response = await client.get(self.endpoint_key)
        status = status_from_http(response)
        metadata: dict[str, Any] = {}

        if response.is_success:
            payload = response.json()
            metadata["version"] = payload.get("version")

        add_non_up_debug_metadata(metadata=metadata, status=status, response=response)
        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=response_latency_ms(response),
            http_status=response.status_code,
            metadata=metadata,
        )


class ExampleSecondaryCheck(BaseCheck):
    check_key = "example_secondary"
    endpoint_key = "https://api.example.com/ping"
    interval_seconds = 60
    timeout_seconds = 5.0
    # weight intentionally omitted -> auto-distributed

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        response = await client.get(self.endpoint_key)
        status = status_from_http(response)
        metadata: dict[str, Any] = {}
        add_non_up_debug_metadata(metadata=metadata, status=status, response=response)
        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=response_latency_ms(response),
            http_status=response.status_code,
            metadata=metadata,
        )


class ExampleServiceChecker(BaseServiceChecker):
    service_key = "example"
    official_uptime = "https://status.example.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = (CloudflareServiceChecker,)

    def build_checks(self) -> Sequence[BaseCheck]:
        return [ExampleHealthCheck(), ExampleSecondaryCheck()]
```

## Implementation Checklist

1. Ensure at least one `BaseServiceChecker` subclass exists in the module.
2. Ensure `service_key` is unique and stable.
3. Ensure dependency classes are imported and valid.
4. Ensure every check has unique `check_key`.
5. Ensure no duplicated helper code; use `checkers/utils.py`.
6. Ensure non-up responses include debug metadata.
7. Ensure explicit weights do not exceed 1 in total.
8. Run lint/tests and local runner commands from SKILL.md.

## Common Pitfalls

1. Using string dependencies instead of checker classes.
2. Duplicating status/latency helper functions in service modules.
3. Setting explicit check weights that exceed 1.
4. Forgetting to include debug metadata for degraded/down checks.
5. Using fragile payload parsing without guard checks.

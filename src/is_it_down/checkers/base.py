import asyncio
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime

import httpx

from is_it_down.core.models import CheckResult


@dataclass(slots=True)
class ServiceRunResult:
    service_key: str
    check_results: list[CheckResult]


class BaseCheck(ABC):
    check_key: str
    endpoint_key: str
    interval_seconds: int = 60
    timeout_seconds: float = 5.0
    weight: float = 1.0

    @abstractmethod
    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        """Execute the check and return a typed result."""

    async def execute(self, client: httpx.AsyncClient) -> CheckResult:
        observed_at = datetime.now(UTC)
        try:
            result = await asyncio.wait_for(self.run(client), timeout=self.timeout_seconds)
            if not result.check_key:
                result.check_key = self.check_key
            if not result.observed_at:
                result.observed_at = observed_at
            return result
        except TimeoutError:
            return CheckResult(
                check_key=self.check_key,
                status="down",
                observed_at=observed_at,
                error_code="TIMEOUT",
                error_message=f"Check timed out after {self.timeout_seconds}s",
            )
        except Exception as exc:
            return CheckResult(
                check_key=self.check_key,
                status="down",
                observed_at=observed_at,
                error_code="CHECK_EXECUTION_ERROR",
                error_message=str(exc),
            )


class BaseServiceChecker(ABC):
    service_key: str
    official_uptime: str | None = None
    dependencies: Sequence[str] = ()

    @abstractmethod
    def build_checks(self) -> Sequence[BaseCheck]:
        """Return concrete endpoint checks for this service."""

    async def run_all(self, client: httpx.AsyncClient) -> ServiceRunResult:
        checks = list(self.build_checks())
        if not checks:
            return ServiceRunResult(service_key=self.service_key, check_results=[])

        results = await asyncio.gather(*(check.execute(client) for check in checks))
        return ServiceRunResult(service_key=self.service_key, check_results=list(results))

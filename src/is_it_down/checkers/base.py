from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from math import isclose

import httpx
from pydantic import BaseModel

from is_it_down.checkers.proxy import ProxyConfigurationError, resolve_proxy_url_for_setting
from is_it_down.core.models import CheckResult


class ServiceRunResult(BaseModel):
    service_key: str
    check_results: list[CheckResult]


class BaseCheck(ABC):
    check_key: str
    endpoint_key: str
    interval_seconds: int = 60
    timeout_seconds: float = 5.0
    weight: float | None = None
    proxy_setting: str | None = None

    @abstractmethod
    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        """Execute the check and return a typed result."""

    @asynccontextmanager
    async def _execute_client(self, client: httpx.AsyncClient) -> AsyncIterator[httpx.AsyncClient]:
        if not self.proxy_setting:
            yield client
            return

        proxy_url = await resolve_proxy_url_for_setting(self.proxy_setting)
        async with _proxy_client_for_check(base_client=client, proxy_url=proxy_url) as proxy_client:
            yield proxy_client

    async def execute(self, client: httpx.AsyncClient) -> CheckResult:
        observed_at = datetime.now(UTC)
        try:
            async with self._execute_client(client) as check_client:
                result = await asyncio.wait_for(self.run(check_client), timeout=self.timeout_seconds)
            if not result.check_key:
                result.check_key = self.check_key
            if not result.observed_at:
                result.observed_at = observed_at
            return result
        except ProxyConfigurationError as exc:
            return CheckResult(
                check_key=self.check_key,
                status="down",
                observed_at=observed_at,
                error_code="PROXY_CONFIGURATION_ERROR",
                error_message=str(exc),
            )
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


@asynccontextmanager
async def _proxy_client_for_check(
    *,
    base_client: httpx.AsyncClient,
    proxy_url: str,
) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        timeout=base_client.timeout,
        headers=dict(base_client.headers),
        follow_redirects=base_client.follow_redirects,
        proxy=proxy_url,
        trust_env=False,
    ) as proxy_client:
        yield proxy_client


class BaseServiceChecker(ABC):
    service_key: str
    logo_url: str
    official_uptime: str | None = None
    dependencies: Sequence[type["BaseServiceChecker"]] = ()

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if cls is BaseServiceChecker:
            return

        logo_url = getattr(cls, "logo_url", None)
        if not isinstance(logo_url, str) or not logo_url.strip():
            raise TypeError(f"{cls.__name__} must define a non-empty logo_url.")

    def dependency_service_keys(self) -> list[str]:
        dependency_keys: list[str] = []
        for dependency in self.dependencies:
            if not isinstance(dependency, type) or not issubclass(dependency, BaseServiceChecker):
                raise TypeError(f"{self.service_key} dependency {dependency!r} is not a BaseServiceChecker subclass.")

            dependency_key = getattr(dependency, "service_key", None)
            if not isinstance(dependency_key, str) or not dependency_key:
                raise ValueError(f"{self.service_key} dependency {dependency.__name__} has no valid service_key.")

            if dependency_key == self.service_key:
                raise ValueError(f"{self.service_key} cannot depend on itself.")

            dependency_keys.append(dependency_key)
        return dependency_keys

    def resolve_check_weights(self, checks: Sequence[BaseCheck]) -> list[BaseCheck]:
        if not checks:
            return []

        explicit_sum = 0.0
        unspecified: list[BaseCheck] = []

        for check in checks:
            if check.weight is None:
                unspecified.append(check)
                continue

            weight = float(check.weight)
            if weight <= 0:
                raise ValueError(f"{self.service_key}.{check.check_key} weight must be greater than 0.")
            if weight > 1:
                raise ValueError(f"{self.service_key}.{check.check_key} weight must be <= 1.0.")

            explicit_sum += weight
            if explicit_sum > 1 + 1e-9:
                raise ValueError(f"{self.service_key} explicit check weights exceed 1.0 (sum={explicit_sum:.6f}).")
            check.weight = weight

        remaining = 1.0 - explicit_sum
        if unspecified:
            if remaining <= 1e-9:
                raise ValueError(
                    f"{self.service_key} has no remaining weight for {len(unspecified)} "
                    "checks without explicit weights."
                )

            shared_weight = remaining / len(unspecified)
            for check in unspecified:
                check.weight = shared_weight
        elif not isclose(explicit_sum, 1.0, rel_tol=1e-9, abs_tol=1e-9):
            raise ValueError(
                f"{self.service_key} explicit check weights must sum to 1.0 "
                f"when all checks set weight (sum={explicit_sum:.6f})."
            )

        total = sum((check.weight or 0.0) for check in checks)
        if not isclose(total, 1.0, rel_tol=1e-9, abs_tol=1e-9):
            raise ValueError(f"{self.service_key} resolved check weights must sum to 1.0 (sum={total:.6f}).")

        return list(checks)

    @abstractmethod
    def build_checks(self) -> Sequence[BaseCheck]:
        """Return concrete endpoint checks for this service."""

    async def run_all(self, client: httpx.AsyncClient) -> ServiceRunResult:
        self.dependency_service_keys()
        checks = self.resolve_check_weights(list(self.build_checks()))
        if not checks:
            return ServiceRunResult(service_key=self.service_key, check_results=[])

        results = await asyncio.gather(*(check.execute(client) for check in checks))
        return ServiceRunResult(service_key=self.service_key, check_results=list(results))

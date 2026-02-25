import asyncio
from datetime import UTC, datetime
from math import isclose

import httpx
import pytest

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.core.models import CheckResult


class SuccessCheck(BaseCheck):
    check_key = "success"
    endpoint_key = "example"

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        return CheckResult(check_key=self.check_key, status="up", observed_at=datetime.now(UTC))


class TimeoutCheck(BaseCheck):
    check_key = "timeout"
    endpoint_key = "example"
    timeout_seconds = 0.01

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        await asyncio.sleep(0.05)
        return CheckResult(check_key=self.check_key, status="up", observed_at=datetime.now(UTC))


class ErrorCheck(BaseCheck):
    check_key = "error"
    endpoint_key = "example"

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        raise RuntimeError("boom")


class WeightedHalfCheck(BaseCheck):
    check_key = "weighted_half"
    endpoint_key = "example"
    weight = 0.5

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        return CheckResult(check_key=self.check_key, status="up", observed_at=datetime.now(UTC))


class UnweightedCheckA(BaseCheck):
    check_key = "unweighted_a"
    endpoint_key = "example"

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        return CheckResult(check_key=self.check_key, status="up", observed_at=datetime.now(UTC))


class UnweightedCheckB(BaseCheck):
    check_key = "unweighted_b"
    endpoint_key = "example"

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        return CheckResult(check_key=self.check_key, status="up", observed_at=datetime.now(UTC))


class WeightedDistributionServiceChecker(BaseServiceChecker):
    service_key = "weight-distribution"
    logo_url = "https://example.com/logo.svg"

    def build_checks(self) -> list[BaseCheck]:
        return [WeightedHalfCheck(), UnweightedCheckA(), UnweightedCheckB()]


class TooHeavySingleCheck(BaseCheck):
    check_key = "too_heavy_single"
    endpoint_key = "example"
    weight = 1.1

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        return CheckResult(check_key=self.check_key, status="up", observed_at=datetime.now(UTC))


class TooHeavySingleServiceChecker(BaseServiceChecker):
    service_key = "too-heavy-single"
    logo_url = "https://example.com/logo.svg"

    def build_checks(self) -> list[BaseCheck]:
        return [TooHeavySingleCheck()]


class WeightOverLimitCheckA(BaseCheck):
    check_key = "over_limit_a"
    endpoint_key = "example"
    weight = 0.8

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        return CheckResult(check_key=self.check_key, status="up", observed_at=datetime.now(UTC))


class WeightOverLimitCheckB(BaseCheck):
    check_key = "over_limit_b"
    endpoint_key = "example"
    weight = 0.4

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        return CheckResult(check_key=self.check_key, status="up", observed_at=datetime.now(UTC))


class WeightOverLimitServiceChecker(BaseServiceChecker):
    service_key = "too-heavy-total"
    logo_url = "https://example.com/logo.svg"

    def build_checks(self) -> list[BaseCheck]:
        return [WeightOverLimitCheckA(), WeightOverLimitCheckB()]


class ExplicitButNotOneCheckA(BaseCheck):
    check_key = "not_one_a"
    endpoint_key = "example"
    weight = 0.6

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        return CheckResult(check_key=self.check_key, status="up", observed_at=datetime.now(UTC))


class ExplicitButNotOneCheckB(BaseCheck):
    check_key = "not_one_b"
    endpoint_key = "example"
    weight = 0.3

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        return CheckResult(check_key=self.check_key, status="up", observed_at=datetime.now(UTC))


class ExplicitButNotOneServiceChecker(BaseServiceChecker):
    service_key = "explicit-not-one"
    logo_url = "https://example.com/logo.svg"

    def build_checks(self) -> list[BaseCheck]:
        return [ExplicitButNotOneCheckA(), ExplicitButNotOneCheckB()]


@pytest.mark.asyncio
async def test_success_check_execute() -> None:
    check = SuccessCheck()
    async with httpx.AsyncClient() as client:
        result = await check.execute(client)
    assert result.status == "up"


@pytest.mark.asyncio
async def test_error_check_execute_returns_down() -> None:
    check = ErrorCheck()
    async with httpx.AsyncClient() as client:
        result = await check.execute(client)

    assert result.status == "down"
    assert result.error_code == "CHECK_EXECUTION_ERROR"


@pytest.mark.asyncio
async def test_timeout_check_execute_returns_timeout() -> None:
    check = TimeoutCheck()
    async with httpx.AsyncClient() as client:
        result = await check.execute(client)

    assert result.status == "down"
    assert result.error_code == "TIMEOUT"


def test_resolve_check_weights_distributes_unspecified_weights() -> None:
    checker = WeightedDistributionServiceChecker()
    checks = checker.resolve_check_weights(list(checker.build_checks()))

    assert len(checks) == 3
    assert checks[0].weight == 0.5
    assert checks[1].weight == 0.25
    assert checks[2].weight == 0.25
    assert isclose(sum(check.weight or 0.0 for check in checks), 1.0, rel_tol=1e-9, abs_tol=1e-9)


def test_resolve_check_weights_raises_if_single_weight_exceeds_one() -> None:
    checker = TooHeavySingleServiceChecker()
    with pytest.raises(ValueError):
        checker.resolve_check_weights(list(checker.build_checks()))


def test_resolve_check_weights_raises_if_total_explicit_weight_exceeds_one() -> None:
    checker = WeightOverLimitServiceChecker()
    with pytest.raises(ValueError):
        checker.resolve_check_weights(list(checker.build_checks()))


def test_resolve_check_weights_raises_if_all_explicit_weights_do_not_sum_to_one() -> None:
    checker = ExplicitButNotOneServiceChecker()
    with pytest.raises(ValueError):
        checker.resolve_check_weights(list(checker.build_checks()))


def test_service_checker_requires_logo_url() -> None:
    with pytest.raises(TypeError):

        class MissingLogoServiceChecker(BaseServiceChecker):
            service_key = "missing-logo"

            def build_checks(self) -> list[BaseCheck]:
                return [SuccessCheck()]

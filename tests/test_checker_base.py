import asyncio
from datetime import UTC, datetime

import httpx
import pytest

from is_it_down.checkers.base import BaseCheck
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

from datetime import UTC, datetime

import httpx
import pytest

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.core.models import CheckResult
from is_it_down.scripts.run_service_checker import (
    discover_service_checkers,
    execute_service_checkers,
    resolve_service_checker_targets,
)


class DummyCheck(BaseCheck):
    check_key = "dummy_check"
    endpoint_key = "dummy://endpoint"

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        return CheckResult(
            check_key=self.check_key,
            status="up",
            observed_at=datetime.now(UTC),
            http_status=200,
            latency_ms=1,
        )


class DummyServiceChecker(BaseServiceChecker):
    service_key = "dummy"

    def build_checks(self) -> list[BaseCheck]:
        return [DummyCheck()]


def test_discover_service_checkers_includes_cloudflare() -> None:
    discovered = discover_service_checkers()
    assert discovered


def test_resolve_service_checker_by_key() -> None:
    discovered = discover_service_checkers()
    target_key = next(iter(sorted(discovered)))

    resolved = resolve_service_checker_targets([target_key])
    assert len(resolved) == 1
    assert resolved[0].service_key == target_key


def test_resolve_service_checker_by_class_path() -> None:
    discovered = discover_service_checkers()
    target_key = next(iter(sorted(discovered)))
    target_cls = discovered[target_key]
    target_path = f"{target_cls.__module__}.{target_cls.__name__}"

    resolved = resolve_service_checker_targets([target_path])
    assert len(resolved) == 1
    assert resolved[0] is target_cls


def test_resolve_service_checker_rejects_unknown_key() -> None:
    with pytest.raises(ValueError):
        resolve_service_checker_targets(["this-does-not-exist"])


@pytest.mark.asyncio
async def test_execute_service_checkers_runs_without_db() -> None:
    runs = await execute_service_checkers([DummyServiceChecker])
    assert len(runs) == 1

    _, run_result = runs[0]
    assert run_result.service_key == "dummy"
    assert len(run_result.check_results) == 1
    assert run_result.check_results[0].status == "up"

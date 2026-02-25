from __future__ import annotations

from datetime import UTC, datetime

import httpx
import pytest

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.core.models import CheckResult
from is_it_down.scripts.checker_runtime import (
    discover_service_checkers,
    execute_service_checkers,
    resolve_service_checker_targets,
    service_checker_path,
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
    logo_url = "https://example.com/logo.svg"

    def build_checks(self) -> list[BaseCheck]:
        return [DummyCheck()]


def _build_dummy_service_checker(index: int) -> type[BaseServiceChecker]:
    class IndexedDummyServiceChecker(BaseServiceChecker):
        service_key = f"dummy_{index}"
        logo_url = "https://example.com/logo.svg"

        def build_checks(self) -> list[BaseCheck]:
            return [DummyCheck()]

    IndexedDummyServiceChecker.__name__ = f"IndexedDummyServiceChecker{index}"
    return IndexedDummyServiceChecker


def test_service_checker_path_returns_fully_qualified_name() -> None:
    path = service_checker_path(DummyServiceChecker)
    assert path.endswith(".DummyServiceChecker")


def test_resolve_service_checker_targets_de_dupes_entries() -> None:
    discovered = discover_service_checkers()
    target_key = next(iter(sorted(discovered)))
    target_cls = discovered[target_key]
    target_path = service_checker_path(target_cls)

    resolved = resolve_service_checker_targets([target_key, target_path, target_key])
    assert len(resolved) == 1
    assert resolved[0] is target_cls


@pytest.mark.asyncio
async def test_execute_service_checkers_supports_concurrent_mode() -> None:
    runs = await execute_service_checkers([DummyServiceChecker], concurrent=True, concurrency_limit=1)
    assert len(runs) == 1
    assert runs[0][1].service_key == "dummy"


@pytest.mark.asyncio
async def test_execute_service_checkers_handles_many_service_classes() -> None:
    checker_classes = [_build_dummy_service_checker(index) for index in range(100)]
    runs = await execute_service_checkers(checker_classes, concurrent=True, concurrency_limit=20)

    assert len(runs) == 100
    assert all(run_result.service_key.startswith("dummy_") for _, run_result in runs)
    assert all(run_result.check_results[0].status == "up" for _, run_result in runs)

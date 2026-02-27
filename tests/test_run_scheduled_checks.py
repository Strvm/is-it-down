from datetime import UTC, datetime

import pytest

from is_it_down.checkers.base import BaseServiceChecker, ServiceRunResult
from is_it_down.core.models import CheckResult
from is_it_down.scripts import run_scheduled_checks
from is_it_down.settings import get_settings


class DummyServiceChecker(BaseServiceChecker):
    service_key = "dummy"
    logo_url = "https://example.com/logo.svg"

    def build_checks(self) -> list:
        return []


def _reset_settings_cache() -> None:
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_run_once_warms_cache_after_bigquery_insert(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_ENABLED", "true")
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_WARM_ON_CHECKER_JOB", "true")
    _reset_settings_cache()

    run_result = ServiceRunResult(
        service_key="dummy",
        check_results=[
            CheckResult(
                check_key="dummy_check",
                status="up",
                observed_at=datetime.now(UTC),
            )
        ],
    )

    async def fake_execute(*args, **kwargs):  # type: ignore[no-untyped-def]
        return [(DummyServiceChecker, run_result)]

    insert_calls: list[int] = []
    warm_calls: list[int] = []

    def fake_insert_rows(rows):  # type: ignore[no-untyped-def]
        insert_calls.append(len(rows))

    async def fake_warm_api_cache() -> int:
        warm_calls.append(1)
        return 4

    monkeypatch.setattr(run_scheduled_checks, "_resolve_service_checker_classes", lambda targets: [DummyServiceChecker])
    monkeypatch.setattr(run_scheduled_checks, "execute_service_checkers", fake_execute)
    monkeypatch.setattr(run_scheduled_checks, "_insert_rows", fake_insert_rows)
    monkeypatch.setattr(run_scheduled_checks, "warm_api_cache", fake_warm_api_cache)

    await run_scheduled_checks._run_once(targets=[], strict=False, dry_run=False)

    assert insert_calls == [1]
    assert warm_calls == [1]


@pytest.mark.asyncio
async def test_run_once_dry_run_skips_insert_and_cache_warm(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_ENABLED", "true")
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_WARM_ON_CHECKER_JOB", "true")
    _reset_settings_cache()

    run_result = ServiceRunResult(
        service_key="dummy",
        check_results=[
            CheckResult(
                check_key="dummy_check",
                status="up",
                observed_at=datetime.now(UTC),
            )
        ],
    )

    async def fake_execute(*args, **kwargs):  # type: ignore[no-untyped-def]
        return [(DummyServiceChecker, run_result)]

    insert_calls: list[int] = []
    warm_calls: list[int] = []

    def fake_insert_rows(rows):  # type: ignore[no-untyped-def]
        insert_calls.append(len(rows))

    async def fake_warm_api_cache() -> int:
        warm_calls.append(1)
        return 1

    monkeypatch.setattr(run_scheduled_checks, "_resolve_service_checker_classes", lambda targets: [DummyServiceChecker])
    monkeypatch.setattr(run_scheduled_checks, "execute_service_checkers", fake_execute)
    monkeypatch.setattr(run_scheduled_checks, "_insert_rows", fake_insert_rows)
    monkeypatch.setattr(run_scheduled_checks, "warm_api_cache", fake_warm_api_cache)

    await run_scheduled_checks._run_once(targets=[], strict=False, dry_run=True)

    assert insert_calls == []
    assert warm_calls == []

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


def _build_dummy_checker(service_key: str) -> type[BaseServiceChecker]:
    checker_service_key = service_key

    class _GeneratedDummyServiceChecker(BaseServiceChecker):
        logo_url = "https://example.com/logo.svg"
        service_key = checker_service_key

        def build_checks(self) -> list:
            return []

    return _GeneratedDummyServiceChecker


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

    async def fake_iter(*args, **kwargs):  # type: ignore[no-untyped-def]
        yield DummyServiceChecker, run_result

    insert_calls: list[int] = []
    warm_calls: list[int] = []

    def fake_insert_rows(rows):  # type: ignore[no-untyped-def]
        insert_calls.append(len(rows))

    async def fake_warm_api_cache() -> int:
        warm_calls.append(1)
        return 4

    monkeypatch.setattr(
        run_scheduled_checks,
        "_resolve_service_checker_classes",
        lambda targets, task_metadata=None: [DummyServiceChecker],
    )
    monkeypatch.setattr(run_scheduled_checks, "iter_service_checker_runs", fake_iter)
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

    async def fake_iter(*args, **kwargs):  # type: ignore[no-untyped-def]
        yield DummyServiceChecker, run_result

    insert_calls: list[int] = []
    warm_calls: list[int] = []

    def fake_insert_rows(rows):  # type: ignore[no-untyped-def]
        insert_calls.append(len(rows))

    async def fake_warm_api_cache() -> int:
        warm_calls.append(1)
        return 1

    monkeypatch.setattr(
        run_scheduled_checks,
        "_resolve_service_checker_classes",
        lambda targets, task_metadata=None: [DummyServiceChecker],
    )
    monkeypatch.setattr(run_scheduled_checks, "iter_service_checker_runs", fake_iter)
    monkeypatch.setattr(run_scheduled_checks, "_insert_rows", fake_insert_rows)
    monkeypatch.setattr(run_scheduled_checks, "warm_api_cache", fake_warm_api_cache)

    await run_scheduled_checks._run_once(targets=[], strict=False, dry_run=True)

    assert insert_calls == []
    assert warm_calls == []


def test_resolve_cloud_run_task_metadata_returns_none_without_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CLOUD_RUN_TASK_INDEX", raising=False)
    monkeypatch.delenv("CLOUD_RUN_TASK_COUNT", raising=False)

    assert run_scheduled_checks._resolve_cloud_run_task_metadata() is None


def test_resolve_service_checker_classes_shards_by_task(monkeypatch: pytest.MonkeyPatch) -> None:
    checkers = {
        key: _build_dummy_checker(key)
        for key in ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot"]
    }
    monkeypatch.setattr(run_scheduled_checks, "discover_service_checkers", lambda: checkers)

    task_zero = run_scheduled_checks._resolve_service_checker_classes([], task_metadata=(0, 3))
    task_one = run_scheduled_checks._resolve_service_checker_classes([], task_metadata=(1, 3))
    task_two = run_scheduled_checks._resolve_service_checker_classes([], task_metadata=(2, 3))

    assert [checker.service_key for checker in task_zero] == ["alpha", "bravo"]
    assert [checker.service_key for checker in task_one] == ["charlie", "delta"]
    assert [checker.service_key for checker in task_two] == ["echo", "foxtrot"]


def test_resolve_service_checker_classes_evenly_distributes_remainder(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    checkers = {
        key: _build_dummy_checker(key)
        for key in ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf"]
    }
    monkeypatch.setattr(run_scheduled_checks, "discover_service_checkers", lambda: checkers)

    task_zero = run_scheduled_checks._resolve_service_checker_classes([], task_metadata=(0, 3))
    task_one = run_scheduled_checks._resolve_service_checker_classes([], task_metadata=(1, 3))
    task_two = run_scheduled_checks._resolve_service_checker_classes([], task_metadata=(2, 3))

    assert [checker.service_key for checker in task_zero] == ["alpha", "bravo", "charlie"]
    assert [checker.service_key for checker in task_one] == ["delta", "echo"]
    assert [checker.service_key for checker in task_two] == ["foxtrot", "golf"]


@pytest.mark.asyncio
async def test_run_once_non_primary_task_skips_cache_warm(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_ENABLED", "true")
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_WARM_ON_CHECKER_JOB", "true")
    monkeypatch.setenv("CLOUD_RUN_TASK_INDEX", "1")
    monkeypatch.setenv("CLOUD_RUN_TASK_COUNT", "4")
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

    async def fake_iter(*args, **kwargs):  # type: ignore[no-untyped-def]
        yield DummyServiceChecker, run_result

    insert_calls: list[int] = []
    warm_calls: list[int] = []

    def fake_insert_rows(rows):  # type: ignore[no-untyped-def]
        insert_calls.append(len(rows))

    async def fake_warm_api_cache() -> int:
        warm_calls.append(1)
        return 1

    monkeypatch.setattr(
        run_scheduled_checks,
        "_resolve_service_checker_classes",
        lambda targets, task_metadata=None: [DummyServiceChecker],
    )
    monkeypatch.setattr(run_scheduled_checks, "iter_service_checker_runs", fake_iter)
    monkeypatch.setattr(run_scheduled_checks, "_insert_rows", fake_insert_rows)
    monkeypatch.setattr(run_scheduled_checks, "warm_api_cache", fake_warm_api_cache)

    await run_scheduled_checks._run_once(targets=[], strict=False, dry_run=False)

    assert insert_calls == [1]
    assert warm_calls == []


@pytest.mark.asyncio
async def test_run_once_task_with_no_assigned_checkers_exits_cleanly(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CLOUD_RUN_TASK_INDEX", "5")
    monkeypatch.setenv("CLOUD_RUN_TASK_COUNT", "6")
    _reset_settings_cache()

    def fail_iter(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("iter_service_checker_runs should not be called when no checkers are assigned.")

    monkeypatch.setattr(
        run_scheduled_checks,
        "_resolve_service_checker_classes",
        lambda targets, task_metadata=None: [],
    )
    monkeypatch.setattr(run_scheduled_checks, "iter_service_checker_runs", fail_iter)

    await run_scheduled_checks._run_once(targets=[], strict=False, dry_run=False)

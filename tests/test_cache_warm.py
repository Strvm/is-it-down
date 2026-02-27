from datetime import UTC, datetime

import pytest

from is_it_down.api.cache_warm import warm_api_cache
from is_it_down.api.schemas import (
    CheckerTrendPoint,
    IncidentSummary,
    ServiceCheckerTrendSummary,
    ServiceDetail,
    ServiceSummary,
    ServiceUptimeSummary,
    SnapshotPoint,
)
from is_it_down.settings import get_settings


def _reset_settings_cache() -> None:
    get_settings.cache_clear()


def _service_summary(*, slug: str, status: str, severity_level: int) -> ServiceSummary:
    return ServiceSummary(
        service_id=1,
        slug=slug,
        name=slug.title(),
        logo_url=f"https://example.com/{slug}.svg",
        status=status,
        status_detail=status,
        severity_level=severity_level,
        score_band="healthy" if status == "up" else "critical",
        raw_score=100.0,
        effective_score=100.0,
        observed_at=datetime.now(UTC),
        dependency_impacted=False,
        attribution_confidence=0.0,
        probable_root_service_id=None,
    )


class FakeCache:
    def __init__(self, *, fail_keys: set[str] | None = None) -> None:
        self.fail_keys = fail_keys or set()
        self.keys: list[str] = []
        self.enabled = True

    async def refresh(self, *, cache_key: str, adapter, loader, ttl_seconds=None):  # type: ignore[no-untyped-def]
        self.keys.append(cache_key)
        if cache_key in self.fail_keys:
            raise RuntimeError("warm failed")
        return await loader()


class FakeStore:
    def __init__(self) -> None:
        self.services = [
            _service_summary(slug="github", status="up", severity_level=0),
            _service_summary(slug="stripe", status="down", severity_level=5),
            _service_summary(slug="vercel", status="degraded", severity_level=3),
        ]
        self.view_counts_by_slug: dict[str, int] = {}

    async def list_services(self) -> list[ServiceSummary]:
        return self.services

    async def service_detail_view_counts_since(self, *, cutoff: datetime) -> dict[str, int]:
        return self.view_counts_by_slug

    async def list_incidents(self, *, status: str) -> list[IncidentSummary]:
        return [
            IncidentSummary(
                incident_id=1,
                service_id=1,
                status=status,
                started_at=datetime.now(UTC),
                resolved_at=None,
                peak_severity="down",
                probable_root_service_id=None,
                confidence=0.0,
                summary="Example incident",
            )
        ]

    async def get_services_uptime(self, *, cutoff: datetime) -> list[ServiceUptimeSummary]:
        return [
            ServiceUptimeSummary(
                service_id=1,
                slug="stripe",
                name="Stripe",
                logo_url="https://example.com/stripe.svg",
                uptime_percent=95.0,
                health_score=92.0,
                checks=[],
            )
        ]

    async def get_service_checker_trends(self, *, cutoff: datetime) -> list[ServiceCheckerTrendSummary]:
        return [
            ServiceCheckerTrendSummary(
                service_id=1,
                slug="stripe",
                name="Stripe",
                logo_url="https://example.com/stripe.svg",
                points=[],
            )
        ]

    async def get_service_detail(self, slug: str) -> ServiceDetail:
        snapshot = _service_summary(slug=slug, status="down", severity_level=5)
        return ServiceDetail(
            service_id=1,
            slug=slug,
            name=slug.title(),
            logo_url=f"https://example.com/{slug}.svg",
            official_status_url=None,
            description=None,
            snapshot=snapshot,
            likely_related_services=[],
            latest_checks=[],
        )

    async def get_service_history(self, slug: str, *, cutoff: datetime) -> list[SnapshotPoint]:
        return [
            SnapshotPoint(
                observed_at=datetime.now(UTC),
                status="down",
                status_detail="down",
                severity_level=5,
                score_band="critical",
                raw_score=0.0,
                effective_score=0.0,
                dependency_impacted=False,
            )
        ]

    async def get_service_checker_trend(self, slug: str, *, cutoff: datetime) -> ServiceCheckerTrendSummary:
        return ServiceCheckerTrendSummary(
            service_id=1,
            slug=slug,
            name=slug.title(),
            logo_url=f"https://example.com/{slug}.svg",
            points=[
                CheckerTrendPoint(
                    bucket_start=datetime.now(UTC),
                    check_key="api",
                    uptime_percent=0.0,
                    health_score=0.0,
                    total_runs=1,
                    up_runs=0,
                )
            ],
        )


@pytest.mark.asyncio
async def test_warm_api_cache_warms_global_and_impacted_service_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_ENABLED", "true")
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_WARM_IMPACTED_SERVICE_LIMIT", "1")
    _reset_settings_cache()

    store = FakeStore()
    cache = FakeCache()
    warmed = await warm_api_cache(store=store, cache=cache)

    assert warmed == 8
    assert "services:list" in cache.keys
    assert "incidents:open" in cache.keys
    assert "incidents:all" in cache.keys
    assert "services:uptime:24h" in cache.keys
    assert "services:checker-trends:24h" in cache.keys
    assert "services:stripe:detail" in cache.keys
    assert "services:stripe:history:24h" in cache.keys
    assert "services:stripe:checker-trend:24h" in cache.keys
    assert "services:vercel:detail" not in cache.keys


@pytest.mark.asyncio
async def test_warm_api_cache_continues_when_individual_key_warm_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_ENABLED", "true")
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_WARM_IMPACTED_SERVICE_LIMIT", "1")
    _reset_settings_cache()

    store = FakeStore()
    cache = FakeCache(fail_keys={"services:stripe:detail"})
    warmed = await warm_api_cache(store=store, cache=cache)

    assert warmed == 7
    assert "services:stripe:detail" in cache.keys
    assert "services:stripe:history:24h" in cache.keys
    assert "services:stripe:checker-trend:24h" in cache.keys


@pytest.mark.asyncio
async def test_warm_api_cache_can_include_top_viewed_services(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_ENABLED", "true")
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_WARM_IMPACTED_SERVICE_LIMIT", "0")
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_WARM_TOP_VIEWED_SERVICE_LIMIT", "1")
    _reset_settings_cache()

    store = FakeStore()
    store.view_counts_by_slug = {"github": 8, "stripe": 3}
    cache = FakeCache()
    warmed = await warm_api_cache(store=store, cache=cache)

    assert warmed == 8
    assert "services:github:detail" in cache.keys
    assert "services:github:history:24h" in cache.keys
    assert "services:github:checker-trend:24h" in cache.keys
    assert "services:stripe:detail" not in cache.keys


@pytest.mark.asyncio
async def test_warm_api_cache_skips_when_cache_is_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_ENABLED", "false")
    _reset_settings_cache()

    store = FakeStore()
    cache = FakeCache()
    warmed = await warm_api_cache(store=store, cache=cache)

    assert warmed == 0
    assert cache.keys == []

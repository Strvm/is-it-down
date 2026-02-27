"""Provide functionality for `is_it_down.api.cache_warm`."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from typing import Any

import structlog
from pydantic import TypeAdapter

from is_it_down.api.bigquery_store import BigQueryApiStore, get_bigquery_api_store
from is_it_down.api.cache import ApiResponseCache, get_api_response_cache
from is_it_down.api.schemas import (
    IncidentSummary,
    ServiceCheckerTrendSummary,
    ServiceDetail,
    ServiceSummary,
    ServiceUptimeSummary,
    SnapshotPoint,
)
from is_it_down.core.time import parse_history_window
from is_it_down.settings import get_settings

logger = structlog.get_logger(__name__)
_DEFAULT_WARM_WINDOW = "24h"
_TOP_VIEWED_LOOKBACK_WINDOW = timedelta(hours=1)
_WARM_CONCURRENCY = 6
_SERVICE_SUMMARY_LIST_ADAPTER = TypeAdapter(list[ServiceSummary])
_INCIDENT_LIST_ADAPTER = TypeAdapter(list[IncidentSummary])
_SERVICE_UPTIME_LIST_ADAPTER = TypeAdapter(list[ServiceUptimeSummary])
_SERVICE_TRENDS_LIST_ADAPTER = TypeAdapter(list[ServiceCheckerTrendSummary])
_SERVICE_DETAIL_ADAPTER = TypeAdapter(ServiceDetail)
_SERVICE_CHECKER_TREND_ADAPTER = TypeAdapter(ServiceCheckerTrendSummary)
_SERVICE_HISTORY_ADAPTER = TypeAdapter(list[SnapshotPoint])


def _warm_target_slugs(
    services: list[ServiceSummary],
    *,
    impacted_limit: int,
    top_viewed_slugs: list[str],
) -> list[str]:
    """Warm target slugs.

    Args:
        services: Service summaries from list endpoint.
        impacted_limit: Maximum number of impacted services to warm.
        top_viewed_slugs: Top viewed service slugs ordered by descending view volume.

    Returns:
        The resulting value.
    """
    impacted = [summary for summary in services if summary.status != "up"]
    impacted.sort(
        key=lambda summary: (summary.severity_level or 0, summary.observed_at),
        reverse=True,
    )
    slugs: list[str] = []
    slug_set: set[str] = set()

    for summary in impacted[: max(0, impacted_limit)]:
        if summary.slug not in slug_set:
            slugs.append(summary.slug)
            slug_set.add(summary.slug)

    for slug in top_viewed_slugs:
        if slug not in slug_set:
            slugs.append(slug)
            slug_set.add(slug)

    return slugs


async def _top_viewed_service_slugs(
    *,
    store: BigQueryApiStore,
    services: list[ServiceSummary],
    limit: int,
) -> list[str]:
    """Top viewed service slugs.

    Args:
        store: Store dependency.
        services: Service summaries from list endpoint.
        limit: Maximum number of top-viewed services to include.

    Returns:
        Ordered list of top-viewed service slugs.
    """
    if limit <= 0:
        return []

    resolver = getattr(store, "service_detail_view_counts_since", None)
    if not callable(resolver):
        return []

    try:
        view_counts_by_slug = await resolver(cutoff=datetime.now(UTC) - _TOP_VIEWED_LOOKBACK_WINDOW)
    except Exception:
        logger.warning("api.cache_warm_top_viewed_lookup_failed", exc_info=True)
        return []

    known_slugs = {summary.slug for summary in services}
    ranked: list[tuple[str, int]] = []
    for slug, view_count_raw in view_counts_by_slug.items():
        if slug not in known_slugs:
            continue
        try:
            view_count = int(view_count_raw)
        except (TypeError, ValueError):
            continue
        if view_count <= 0:
            continue
        ranked.append((slug, view_count))
    ranked.sort(key=lambda item: (-item[1], item[0]))
    return [slug for slug, _ in ranked[:limit]]


async def _warm_many_keys(
    *,
    cache: ApiResponseCache,
    warm_entries: list[tuple[str, TypeAdapter[Any], Callable[[], Awaitable[Any]]]],
) -> int:
    """Warm many keys concurrently.

    Args:
        cache: Cache dependency.
        warm_entries: Collection of warm requests.

    Returns:
        Number of keys that were refreshed successfully.
    """
    if not warm_entries:
        return 0

    semaphore = asyncio.Semaphore(_WARM_CONCURRENCY)

    async def _warm_entry(
        warm_entry: tuple[str, TypeAdapter[Any], Callable[[], Awaitable[Any]]],
    ) -> int:
        """Warm entry.

        Args:
            warm_entry: Tuple of cache key, adapter, and loader.

        Returns:
            `1` when the key was warmed successfully; otherwise, `0`.
        """
        cache_key, adapter, loader = warm_entry
        async with semaphore:
            value = await _warm_key(
                cache=cache,
                cache_key=cache_key,
                adapter=adapter,
                loader=loader,
            )
        return 1 if value is not None else 0

    warmed_results = await asyncio.gather(*(_warm_entry(entry) for entry in warm_entries))
    return sum(warmed_results)


async def _warm_key[T](
    *,
    cache: ApiResponseCache,
    cache_key: str,
    adapter: TypeAdapter[T],
    loader,
) -> T | None:
    """Warm key.

    Args:
        cache: Cache dependency.
        cache_key: Logical cache key.
        adapter: Type adapter for the payload.
        loader: Async loader callable.

    Returns:
        The loaded value when key refresh succeeds; otherwise, None.
    """
    try:
        return await cache.refresh(cache_key=cache_key, adapter=adapter, loader=loader)
    except Exception:
        logger.warning("api.cache_warm_key_failed", cache_key=cache_key, exc_info=True)
        return None


async def warm_api_cache(
    *,
    store: BigQueryApiStore | None = None,
    cache: ApiResponseCache | None = None,
) -> int:
    """Warm api cache.

    Args:
        store: Optional store override for tests.
        cache: Optional cache override for tests.

    Returns:
        Total number of keys warmed successfully.
    """
    settings = get_settings()
    if not settings.api_cache_enabled:
        logger.info("api.cache_warm_skipped_disabled")
        return 0

    store = store or get_bigquery_api_store()
    cache = cache or get_api_response_cache()
    if not cache.enabled:
        logger.info("api.cache_warm_skipped_cache_disabled")
        return 0
    if hasattr(cache, "backend_available") and not await cache.backend_available():
        logger.info("api.cache_warm_skipped_backend_unavailable")
        return 0

    cutoff = datetime.now(UTC) - parse_history_window(_DEFAULT_WARM_WINDOW)
    warmed_key_count = 0

    async def load_services() -> list[ServiceSummary]:
        """Load services.

        Returns:
            The resulting value.
        """
        return await store.list_services()

    services = await _warm_key(
        cache=cache,
        cache_key="services:list",
        adapter=_SERVICE_SUMMARY_LIST_ADAPTER,
        loader=load_services,
    )
    if services is not None:
        warmed_key_count += 1

    warmed_key_count += await _warm_many_keys(
        cache=cache,
        warm_entries=[
            (
                "incidents:open",
                _INCIDENT_LIST_ADAPTER,
                lambda: store.list_incidents(status="open"),
            ),
            (
                "incidents:all",
                _INCIDENT_LIST_ADAPTER,
                lambda: store.list_incidents(status="all"),
            ),
            (
                f"services:uptime:{_DEFAULT_WARM_WINDOW}",
                _SERVICE_UPTIME_LIST_ADAPTER,
                lambda: store.get_services_uptime(cutoff=cutoff),
            ),
            (
                f"services:checker-trends:{_DEFAULT_WARM_WINDOW}",
                _SERVICE_TRENDS_LIST_ADAPTER,
                lambda: store.get_service_checker_trends(cutoff=cutoff),
            ),
        ],
    )

    if services is None:
        services = []

    warm_service_limit = max(0, settings.api_cache_warm_impacted_service_limit)
    warm_top_viewed_service_limit = max(0, settings.api_cache_warm_top_viewed_service_limit)
    top_viewed_slugs = await _top_viewed_service_slugs(
        store=store,
        services=services,
        limit=warm_top_viewed_service_limit,
    )
    warm_service_slugs = _warm_target_slugs(
        services,
        impacted_limit=warm_service_limit,
        top_viewed_slugs=top_viewed_slugs,
    )

    service_warm_entries: list[tuple[str, TypeAdapter[Any], Callable[[], Awaitable[Any]]]] = []
    for slug in warm_service_slugs:
        async def load_detail(current_slug: str = slug) -> ServiceDetail:
            """Load detail.

            Args:
                current_slug: Service slug.

            Returns:
                The resulting value.

            Raises:
                RuntimeError: If service detail is missing.
            """
            detail = await store.get_service_detail(current_slug)
            if detail is None:
                raise RuntimeError(f"Service detail is missing for slug='{current_slug}'.")
            return detail

        service_warm_entries.append(
            (
                f"services:{slug}:detail",
                _SERVICE_DETAIL_ADAPTER,
                load_detail,
            )
        )

        async def load_history(current_slug: str = slug) -> list[SnapshotPoint]:
            """Load history.

            Args:
                current_slug: Service slug.

            Returns:
                The resulting value.

            Raises:
                RuntimeError: If service history is missing.
            """
            history = await store.get_service_history(current_slug, cutoff=cutoff)
            if history is None:
                raise RuntimeError(f"Service history is missing for slug='{current_slug}'.")
            return history

        service_warm_entries.append(
            (
                f"services:{slug}:history:{_DEFAULT_WARM_WINDOW}",
                _SERVICE_HISTORY_ADAPTER,
                load_history,
            )
        )

        async def load_checker_trend(current_slug: str = slug) -> ServiceCheckerTrendSummary:
            """Load checker trend.

            Args:
                current_slug: Service slug.

            Returns:
                The resulting value.

            Raises:
                RuntimeError: If service checker trend is missing.
            """
            checker_trend = await store.get_service_checker_trend(current_slug, cutoff=cutoff)
            if checker_trend is None:
                raise RuntimeError(f"Service checker trend is missing for slug='{current_slug}'.")
            return checker_trend

        service_warm_entries.append(
            (
                f"services:{slug}:checker-trend:{_DEFAULT_WARM_WINDOW}",
                _SERVICE_CHECKER_TREND_ADAPTER,
                load_checker_trend,
            )
        )

    warmed_key_count += await _warm_many_keys(
        cache=cache,
        warm_entries=service_warm_entries,
    )

    logger.info(
        "api.cache_warm_completed",
        warmed_key_count=warmed_key_count,
        warmed_service_count=len(warm_service_slugs),
    )
    return warmed_key_count

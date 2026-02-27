"""Provide functionality for `is_it_down.api.routes.services`."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import TypeAdapter

from is_it_down.api.bigquery_store import BigQueryApiStore
from is_it_down.api.cache import ApiResponseCache
from is_it_down.api.deps import api_response_cache_dep, bigquery_store_dep
from is_it_down.api.schemas import (
    ServiceCheckerTrendSummary,
    ServiceDetail,
    ServiceSummary,
    ServiceUptimeSummary,
    SnapshotPoint,
)
from is_it_down.core.time import parse_history_window

router = APIRouter(prefix="/v1/services", tags=["services"])
_SERVICE_SUMMARY_LIST_ADAPTER = TypeAdapter(list[ServiceSummary])
_SERVICE_UPTIME_LIST_ADAPTER = TypeAdapter(list[ServiceUptimeSummary])
_SERVICE_CHECKER_TRENDS_LIST_ADAPTER = TypeAdapter(list[ServiceCheckerTrendSummary])
_SERVICE_CHECKER_TREND_ADAPTER = TypeAdapter(ServiceCheckerTrendSummary)
_SERVICE_DETAIL_ADAPTER = TypeAdapter(ServiceDetail)
_SERVICE_HISTORY_LIST_ADAPTER = TypeAdapter(list[SnapshotPoint])


@router.get("", response_model=list[ServiceSummary])
async def list_services(
    store: BigQueryApiStore = Depends(bigquery_store_dep),
    cache: ApiResponseCache = Depends(api_response_cache_dep),
) -> list[ServiceSummary]:
    """List services.
    
    Args:
        store: The store value.
        cache: The cache value.
    
    Returns:
        The resulting value.
    """
    return await cache.get_or_set(
        cache_key="services:list",
        adapter=_SERVICE_SUMMARY_LIST_ADAPTER,
        loader=store.list_services,
    )


@router.get("/uptime", response_model=list[ServiceUptimeSummary])
async def list_services_uptime(
    window: str = Query(default="24h", pattern=r"^[1-9][0-9]*[hdm]$"),
    store: BigQueryApiStore = Depends(bigquery_store_dep),
    cache: ApiResponseCache = Depends(api_response_cache_dep),
) -> list[ServiceUptimeSummary]:
    """List services uptime.
    
    Args:
        window: The window value.
        store: The store value.
        cache: The cache value.
    
    Returns:
        The resulting value.
    """
    cutoff = datetime.now(UTC) - parse_history_window(window)
    return await cache.get_or_set(
        cache_key=f"services:uptime:{window}",
        adapter=_SERVICE_UPTIME_LIST_ADAPTER,
        loader=lambda: store.get_services_uptime(cutoff=cutoff),
    )


@router.get("/checker-trends", response_model=list[ServiceCheckerTrendSummary])
async def list_service_checker_trends(
    window: str = Query(default="24h", pattern=r"^[1-9][0-9]*[hdm]$"),
    store: BigQueryApiStore = Depends(bigquery_store_dep),
    cache: ApiResponseCache = Depends(api_response_cache_dep),
) -> list[ServiceCheckerTrendSummary]:
    """List service checker trends.
    
    Args:
        window: The window value.
        store: The store value.
        cache: The cache value.
    
    Returns:
        The resulting value.
    """
    cutoff = datetime.now(UTC) - parse_history_window(window)
    return await cache.get_or_set(
        cache_key=f"services:checker-trends:{window}",
        adapter=_SERVICE_CHECKER_TRENDS_LIST_ADAPTER,
        loader=lambda: store.get_service_checker_trends(cutoff=cutoff),
    )


@router.get("/{slug}/checker-trends", response_model=ServiceCheckerTrendSummary)
async def get_service_checker_trend(
    slug: str,
    window: str = Query(default="24h", pattern=r"^[1-9][0-9]*[hdm]$"),
    store: BigQueryApiStore = Depends(bigquery_store_dep),
    cache: ApiResponseCache = Depends(api_response_cache_dep),
) -> ServiceCheckerTrendSummary:
    """Get service checker trend.
    
    Args:
        slug: The slug value.
        window: The window value.
        store: The store value.
        cache: The cache value.
    
    Returns:
        The resulting value.
    
    Raises:
        HTTPException: If an error occurs while executing this function.
    """
    cutoff = datetime.now(UTC) - parse_history_window(window)

    async def load_trend() -> ServiceCheckerTrendSummary:
        """Load trend.

        Returns:
            The resulting value.

        Raises:
            HTTPException: If the service does not exist.
        """
        trend = await store.get_service_checker_trend(slug, cutoff=cutoff)
        if trend is None:
            raise HTTPException(status_code=404, detail="Service not found")
        return trend

    return await cache.get_or_set(
        cache_key=f"services:{slug}:checker-trend:{window}",
        adapter=_SERVICE_CHECKER_TREND_ADAPTER,
        loader=load_trend,
    )


@router.get("/{slug}", response_model=ServiceDetail)
async def get_service_detail(
    slug: str,
    store: BigQueryApiStore = Depends(bigquery_store_dep),
    cache: ApiResponseCache = Depends(api_response_cache_dep),
) -> ServiceDetail:
    """Get service detail.
    
    Args:
        slug: The slug value.
        store: The store value.
        cache: The cache value.
    
    Returns:
        The resulting value.
    
    Raises:
        HTTPException: If an error occurs while executing this function.
    """
    async def load_detail() -> ServiceDetail:
        """Load detail.

        Returns:
            The resulting value.

        Raises:
            HTTPException: If the service does not exist.
        """
        detail = await store.get_service_detail(slug)
        if detail is None:
            raise HTTPException(status_code=404, detail="Service not found")
        return detail

    return await cache.get_or_set(
        cache_key=f"services:{slug}:detail",
        adapter=_SERVICE_DETAIL_ADAPTER,
        loader=load_detail,
    )


@router.get("/{slug}/history", response_model=list[SnapshotPoint])
async def get_service_history(
    slug: str,
    window: str = Query(default="24h", pattern=r"^[1-9][0-9]*[hdm]$"),
    store: BigQueryApiStore = Depends(bigquery_store_dep),
    cache: ApiResponseCache = Depends(api_response_cache_dep),
) -> list[SnapshotPoint]:
    """Get service history.
    
    Args:
        slug: The slug value.
        window: The window value.
        store: The store value.
        cache: The cache value.
    
    Returns:
        The resulting value.
    
    Raises:
        HTTPException: If an error occurs while executing this function.
    """
    cutoff = datetime.now(UTC) - parse_history_window(window)

    async def load_history() -> list[SnapshotPoint]:
        """Load history.

        Returns:
            The resulting value.

        Raises:
            HTTPException: If the service does not exist.
        """
        points = await store.get_service_history(slug, cutoff=cutoff)
        if points is None:
            raise HTTPException(status_code=404, detail="Service not found")
        return points

    return await cache.get_or_set(
        cache_key=f"services:{slug}:history:{window}",
        adapter=_SERVICE_HISTORY_LIST_ADAPTER,
        loader=load_history,
    )

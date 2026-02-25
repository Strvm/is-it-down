"""Provide functionality for `is_it_down.api.routes.services`."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from is_it_down.api.bigquery_store import BigQueryApiStore
from is_it_down.api.deps import bigquery_store_dep
from is_it_down.api.schemas import (
    ServiceCheckerTrendSummary,
    ServiceDetail,
    ServiceSummary,
    ServiceUptimeSummary,
    SnapshotPoint,
)
from is_it_down.core.time import parse_history_window

router = APIRouter(prefix="/v1/services", tags=["services"])


@router.get("", response_model=list[ServiceSummary])
async def list_services(store: BigQueryApiStore = Depends(bigquery_store_dep)) -> list[ServiceSummary]:
    """List services."""
    return await store.list_services()


@router.get("/uptime", response_model=list[ServiceUptimeSummary])
async def list_services_uptime(
    window: str = Query(default="24h", pattern=r"^[1-9][0-9]*[hdm]$"),
    store: BigQueryApiStore = Depends(bigquery_store_dep),
) -> list[ServiceUptimeSummary]:
    """List services uptime."""
    cutoff = datetime.now(UTC) - parse_history_window(window)
    return await store.get_services_uptime(cutoff=cutoff)


@router.get("/checker-trends", response_model=list[ServiceCheckerTrendSummary])
async def list_service_checker_trends(
    window: str = Query(default="24h", pattern=r"^[1-9][0-9]*[hdm]$"),
    store: BigQueryApiStore = Depends(bigquery_store_dep),
) -> list[ServiceCheckerTrendSummary]:
    """List service checker trends."""
    cutoff = datetime.now(UTC) - parse_history_window(window)
    return await store.get_service_checker_trends(cutoff=cutoff)


@router.get("/{slug}/checker-trends", response_model=ServiceCheckerTrendSummary)
async def get_service_checker_trend(
    slug: str,
    window: str = Query(default="24h", pattern=r"^[1-9][0-9]*[hdm]$"),
    store: BigQueryApiStore = Depends(bigquery_store_dep),
) -> ServiceCheckerTrendSummary:
    """Get service checker trend."""
    cutoff = datetime.now(UTC) - parse_history_window(window)
    trend = await store.get_service_checker_trend(slug, cutoff=cutoff)
    if trend is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return trend


@router.get("/{slug}", response_model=ServiceDetail)
async def get_service_detail(slug: str, store: BigQueryApiStore = Depends(bigquery_store_dep)) -> ServiceDetail:
    """Get service detail."""
    detail = await store.get_service_detail(slug)
    if detail is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return detail


@router.get("/{slug}/history", response_model=list[SnapshotPoint])
async def get_service_history(
    slug: str,
    window: str = Query(default="24h", pattern=r"^[1-9][0-9]*[hdm]$"),
    store: BigQueryApiStore = Depends(bigquery_store_dep),
) -> list[SnapshotPoint]:
    """Get service history."""
    cutoff = datetime.now(UTC) - parse_history_window(window)
    points = await store.get_service_history(slug, cutoff=cutoff)
    if points is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return points

"""Provide functionality for `is_it_down.api.routes.incidents`."""

from fastapi import APIRouter, Depends, Query
from pydantic import TypeAdapter

from is_it_down.api.bigquery_store import BigQueryApiStore
from is_it_down.api.cache import ApiResponseCache
from is_it_down.api.deps import api_response_cache_dep, bigquery_store_dep
from is_it_down.api.schemas import IncidentSummary

router = APIRouter(prefix="/v1/incidents", tags=["incidents"])
_INCIDENT_LIST_ADAPTER = TypeAdapter(list[IncidentSummary])


@router.get("", response_model=list[IncidentSummary])
async def list_incidents(
    status: str = Query(default="open", pattern=r"^(open|resolved|all)$"),
    store: BigQueryApiStore = Depends(bigquery_store_dep),
    cache: ApiResponseCache = Depends(api_response_cache_dep),
) -> list[IncidentSummary]:
    """List incidents.
    
    Args:
        status: The status value.
        store: The store value.
        cache: The cache value.
    
    Returns:
        The resulting value.
    """
    return await cache.get_or_set(
        cache_key=f"incidents:{status}",
        adapter=_INCIDENT_LIST_ADAPTER,
        loader=lambda: store.list_incidents(status=status),
    )

"""Provide functionality for `is_it_down.api.routes.incidents`."""

from fastapi import APIRouter, Depends, Query

from is_it_down.api.bigquery_store import BigQueryApiStore
from is_it_down.api.deps import bigquery_store_dep
from is_it_down.api.schemas import IncidentSummary

router = APIRouter(prefix="/v1/incidents", tags=["incidents"])


@router.get("", response_model=list[IncidentSummary])
async def list_incidents(
    status: str = Query(default="open", pattern=r"^(open|resolved|all)$"),
    store: BigQueryApiStore = Depends(bigquery_store_dep),
) -> list[IncidentSummary]:
    """List incidents."""
    return await store.list_incidents(status=status)

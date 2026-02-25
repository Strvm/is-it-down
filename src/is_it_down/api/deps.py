"""Provide functionality for `is_it_down.api.deps`."""

from is_it_down.api.bigquery_store import BigQueryApiStore, get_bigquery_api_store


def bigquery_store_dep() -> BigQueryApiStore:
    """Bigquery store dep.
    
    Returns:
        The resulting value.
    """
    return get_bigquery_api_store()

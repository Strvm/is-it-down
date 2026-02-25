from is_it_down.api.bigquery_store import BigQueryApiStore, get_bigquery_api_store


def bigquery_store_dep() -> BigQueryApiStore:
    return get_bigquery_api_store()

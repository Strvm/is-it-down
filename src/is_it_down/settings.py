from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="IS_IT_DOWN_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: Literal["local", "development", "production"] = "local"
    database_url: str = Field(default="postgresql+asyncpg://postgres:postgres@localhost:5432/is_it_down")
    bigquery_project_id: str | None = None
    bigquery_dataset_id: str = "is_it_down"
    bigquery_table_id: str = "check_results"
    log_level: str = "INFO"

    scheduler_tick_seconds: float = 5.0
    scheduler_batch_size: int = 500

    worker_poll_seconds: float = 1.0
    worker_batch_size: int = 100
    worker_concurrency: int = 200
    per_service_concurrency: int = 10
    worker_lease_seconds: int = 30
    worker_max_attempts: int = 3
    checker_concurrency: int = 10

    default_http_timeout_seconds: float = 5.0
    user_agent: str = "is-it-down/0.1.0"

    api_host: str = "0.0.0.0"
    api_port: int = 8080


@lru_cache
def get_settings() -> Settings:
    return Settings()

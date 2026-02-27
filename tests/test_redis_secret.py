import pytest

from is_it_down.cache.redis_secret import (
    RedisSecretConfigurationError,
    _resolve_secret_name,
    clear_redis_secret_resolution_cache,
    resolve_api_cache_redis_url_sync,
)
from is_it_down.settings import get_settings


def _reset_settings_cache() -> None:
    get_settings.cache_clear()
    clear_redis_secret_resolution_cache()


def test_resolve_secret_name_keeps_fully_qualified_secret_version() -> None:
    _reset_settings_cache()
    try:
        name = _resolve_secret_name("projects/demo/secrets/redis-url/versions/5")
    finally:
        _reset_settings_cache()

    assert name == "projects/demo/secrets/redis-url/versions/5"


def test_resolve_secret_name_appends_latest_for_fully_qualified_secret() -> None:
    _reset_settings_cache()
    try:
        name = _resolve_secret_name("projects/demo/secrets/redis-url")
    finally:
        _reset_settings_cache()

    assert name == "projects/demo/secrets/redis-url/versions/latest"


def test_resolve_secret_name_uses_redis_secret_project(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IS_IT_DOWN_REDIS_SECRET_PROJECT_ID", "demo-project")
    _reset_settings_cache()
    try:
        name = _resolve_secret_name("redis-url")
    finally:
        _reset_settings_cache()

    assert name == "projects/demo-project/secrets/redis-url/versions/latest"


def test_resolve_secret_name_requires_project_for_short_secret_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("IS_IT_DOWN_REDIS_SECRET_PROJECT_ID", raising=False)
    monkeypatch.delenv("IS_IT_DOWN_BIGQUERY_PROJECT_ID", raising=False)
    _reset_settings_cache()
    try:
        with pytest.raises(RedisSecretConfigurationError):
            _resolve_secret_name("redis-url")
    finally:
        _reset_settings_cache()


def test_default_redis_url_from_settings_bypasses_secret_manager(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_REDIS_URL", "redis://127.0.0.1:6379")
    monkeypatch.delenv("IS_IT_DOWN_API_CACHE_REDIS_SECRET_ID", raising=False)
    monkeypatch.delenv("IS_IT_DOWN_REDIS_SECRET_PROJECT_ID", raising=False)
    _reset_settings_cache()
    try:
        redis_url = resolve_api_cache_redis_url_sync()
    finally:
        _reset_settings_cache()

    assert redis_url == "redis://127.0.0.1:6379"

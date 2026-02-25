import pytest

from is_it_down.checkers.proxy import (
    ProxyConfigurationError,
    _resolve_secret_name,
    clear_proxy_resolution_cache,
    resolve_proxy_url_for_setting_sync,
)
from is_it_down.settings import get_settings


def _reset_settings_cache() -> None:
    get_settings.cache_clear()
    clear_proxy_resolution_cache()


def test_resolve_secret_name_keeps_fully_qualified_secret_version() -> None:
    _reset_settings_cache()
    try:
        name = _resolve_secret_name("projects/demo/secrets/proxy-url/versions/5")
    finally:
        _reset_settings_cache()

    assert name == "projects/demo/secrets/proxy-url/versions/5"


def test_resolve_secret_name_appends_latest_for_fully_qualified_secret() -> None:
    _reset_settings_cache()
    try:
        name = _resolve_secret_name("projects/demo/secrets/proxy-url")
    finally:
        _reset_settings_cache()

    assert name == "projects/demo/secrets/proxy-url/versions/latest"


def test_resolve_secret_name_uses_default_proxy_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IS_IT_DOWN_PROXY_SECRET_PROJECT_ID", "demo-project")
    monkeypatch.setenv("IS_IT_DOWN_DEFAULT_CHECKER_PROXY_SECRET_ID", "checker-proxy-url")
    _reset_settings_cache()
    try:
        name = _resolve_secret_name("default")
    finally:
        _reset_settings_cache()

    assert name == "projects/demo-project/secrets/checker-proxy-url/versions/latest"


def test_resolve_secret_name_requires_project_for_short_secret_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("IS_IT_DOWN_PROXY_SECRET_PROJECT_ID", raising=False)
    monkeypatch.delenv("IS_IT_DOWN_BIGQUERY_PROJECT_ID", raising=False)
    _reset_settings_cache()
    try:
        with pytest.raises(ProxyConfigurationError):
            _resolve_secret_name("checker-proxy-url")
    finally:
        _reset_settings_cache()


def test_default_proxy_url_from_settings_bypasses_secret_manager(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IS_IT_DOWN_DEFAULT_CHECKER_PROXY_URL", "http://127.0.0.1:8080")
    monkeypatch.delenv("IS_IT_DOWN_PROXY_SECRET_PROJECT_ID", raising=False)
    monkeypatch.delenv("IS_IT_DOWN_DEFAULT_CHECKER_PROXY_SECRET_ID", raising=False)
    _reset_settings_cache()
    try:
        proxy_url = resolve_proxy_url_for_setting_sync("default")
    finally:
        _reset_settings_cache()

    assert proxy_url == "http://127.0.0.1:8080"

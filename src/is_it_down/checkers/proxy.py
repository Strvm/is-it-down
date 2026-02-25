from __future__ import annotations

import asyncio
import base64
from functools import lru_cache

import google.auth
from google.auth.transport.requests import AuthorizedSession

from is_it_down.settings import get_settings

_CLOUD_PLATFORM_SCOPE = "https://www.googleapis.com/auth/cloud-platform"
_SECRET_VERSION = "latest"
_DEFAULT_PROXY_SETTING = "default"


class ProxyConfigurationError(RuntimeError):
    """Raised when a checker proxy secret cannot be resolved."""


def _resolve_secret_name(proxy_setting: str) -> str:
    setting = proxy_setting.strip()
    if not setting:
        raise ProxyConfigurationError("proxy_setting must be a non-empty string.")

    settings = get_settings()
    if setting == _DEFAULT_PROXY_SETTING:
        default_secret = settings.default_checker_proxy_secret_id
        if not default_secret:
            raise ProxyConfigurationError(
                "proxy_setting='default' requires IS_IT_DOWN_DEFAULT_CHECKER_PROXY_SECRET_ID.",
            )
        setting = default_secret

    if setting.startswith("projects/"):
        if "/versions/" in setting:
            return setting
        return f"{setting}/versions/{_SECRET_VERSION}"

    project_id = settings.proxy_secret_project_id or settings.bigquery_project_id
    if not project_id:
        raise ProxyConfigurationError(
            "IS_IT_DOWN_PROXY_SECRET_PROJECT_ID is required when proxy_setting is not a full secret resource path.",
        )

    return f"projects/{project_id}/secrets/{setting}/versions/{_SECRET_VERSION}"


@lru_cache
def _authorized_session() -> AuthorizedSession:
    credentials, _ = google.auth.default(scopes=[_CLOUD_PLATFORM_SCOPE])
    return AuthorizedSession(credentials=credentials)


def _default_proxy_url_from_settings() -> str | None:
    settings = get_settings()
    proxy_url = settings.default_checker_proxy_url
    if proxy_url is None:
        return None
    stripped = proxy_url.strip()
    return stripped or None


@lru_cache(maxsize=64)
def resolve_proxy_url_for_setting_sync(proxy_setting: str) -> str:
    if proxy_setting.strip() == _DEFAULT_PROXY_SETTING:
        default_proxy_url = _default_proxy_url_from_settings()
        if default_proxy_url is not None:
            return default_proxy_url

    secret_version_name = _resolve_secret_name(proxy_setting)
    response = _authorized_session().get(
        f"https://secretmanager.googleapis.com/v1/{secret_version_name}:access",
        timeout=10,
    )

    if response.status_code >= 400:
        raise ProxyConfigurationError(
            f"Failed to access proxy secret '{secret_version_name}' (HTTP {response.status_code}).",
        )

    payload = response.json()
    encoded_data = payload.get("payload", {}).get("data")
    if not isinstance(encoded_data, str) or not encoded_data:
        raise ProxyConfigurationError(f"Proxy secret '{secret_version_name}' has no payload data.")

    try:
        proxy_url = base64.b64decode(encoded_data).decode("utf-8").strip()
    except Exception as exc:  # pragma: no cover - defensive path
        raise ProxyConfigurationError(
            f"Failed to decode proxy secret '{secret_version_name}' payload: {exc}",
        ) from exc

    if not proxy_url:
        raise ProxyConfigurationError(f"Proxy secret '{secret_version_name}' is empty.")

    return proxy_url


async def resolve_proxy_url_for_setting(proxy_setting: str) -> str:
    return await asyncio.to_thread(resolve_proxy_url_for_setting_sync, proxy_setting)


def clear_proxy_resolution_cache() -> None:
    resolve_proxy_url_for_setting_sync.cache_clear()

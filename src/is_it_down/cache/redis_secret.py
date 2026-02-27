"""Provide functionality for `is_it_down.cache.redis_secret`."""

from __future__ import annotations

import asyncio
import base64
from functools import lru_cache

import google.auth
from google.auth.transport.requests import AuthorizedSession

from is_it_down.settings import get_settings

_CLOUD_PLATFORM_SCOPE = "https://www.googleapis.com/auth/cloud-platform"
_SECRET_VERSION = "latest"


class RedisSecretConfigurationError(RuntimeError):
    """Raised when Redis secret configuration cannot be resolved."""


def _resolve_secret_name(secret_setting: str) -> str:
    """Resolve secret name.

    Args:
        secret_setting: Redis secret setting value.

    Returns:
        The fully qualified Secret Manager secret version resource name.

    Raises:
        RedisSecretConfigurationError: If the configuration is invalid.
    """
    setting = secret_setting.strip()
    if not setting:
        raise RedisSecretConfigurationError("Redis secret setting must be a non-empty string.")

    if setting.startswith("projects/"):
        if "/versions/" in setting:
            return setting
        return f"{setting}/versions/{_SECRET_VERSION}"

    settings = get_settings()
    project_id = settings.redis_secret_project_id or settings.bigquery_project_id
    if not project_id:
        raise RedisSecretConfigurationError(
            "IS_IT_DOWN_REDIS_SECRET_PROJECT_ID is required when "
            "IS_IT_DOWN_API_CACHE_REDIS_SECRET_ID is not a full secret resource path.",
        )

    return f"projects/{project_id}/secrets/{setting}/versions/{_SECRET_VERSION}"


@lru_cache
def _authorized_session() -> AuthorizedSession:
    """Authorized session.

    Returns:
        The resulting value.
    """
    credentials, _ = google.auth.default(scopes=[_CLOUD_PLATFORM_SCOPE])
    return AuthorizedSession(credentials=credentials)


def _default_redis_url_from_settings() -> str | None:
    """Default redis url from settings.

    Returns:
        The resulting value.
    """
    settings = get_settings()
    redis_url = settings.api_cache_redis_url
    if redis_url is None:
        return None
    stripped = redis_url.strip()
    return stripped or None


@lru_cache(maxsize=1)
def resolve_api_cache_redis_url_sync() -> str:
    """Resolve api cache redis url sync.

    Returns:
        The resulting value.

    Raises:
        RedisSecretConfigurationError: If the secret cannot be loaded.
    """
    default_url = _default_redis_url_from_settings()
    if default_url is not None:
        return default_url

    settings = get_settings()
    secret_setting = settings.api_cache_redis_secret_id
    if not isinstance(secret_setting, str) or not secret_setting.strip():
        raise RedisSecretConfigurationError(
            "IS_IT_DOWN_API_CACHE_REDIS_SECRET_ID is required when IS_IT_DOWN_API_CACHE_REDIS_URL is unset.",
        )

    secret_version_name = _resolve_secret_name(secret_setting)
    response = _authorized_session().get(
        f"https://secretmanager.googleapis.com/v1/{secret_version_name}:access",
        timeout=10,
    )
    if response.status_code >= 400:
        raise RedisSecretConfigurationError(
            f"Failed to access Redis secret '{secret_version_name}' (HTTP {response.status_code}).",
        )

    payload = response.json()
    encoded_data = payload.get("payload", {}).get("data")
    if not isinstance(encoded_data, str) or not encoded_data:
        raise RedisSecretConfigurationError(f"Redis secret '{secret_version_name}' has no payload data.")

    try:
        redis_url = base64.b64decode(encoded_data).decode("utf-8").strip()
    except Exception as exc:  # pragma: no cover - defensive path
        raise RedisSecretConfigurationError(
            f"Failed to decode Redis secret '{secret_version_name}' payload: {exc}",
        ) from exc

    if not redis_url:
        raise RedisSecretConfigurationError(f"Redis secret '{secret_version_name}' is empty.")

    return redis_url


async def resolve_api_cache_redis_url() -> str:
    """Resolve api cache redis url.

    Returns:
        The resulting value.
    """
    return await asyncio.to_thread(resolve_api_cache_redis_url_sync)


def clear_redis_secret_resolution_cache() -> None:
    """Clear redis secret resolution cache."""
    resolve_api_cache_redis_url_sync.cache_clear()
    _authorized_session.cache_clear()

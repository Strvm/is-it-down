"""Provide functionality for `is_it_down.api.cache`."""

from __future__ import annotations

import asyncio
import json
from functools import lru_cache
from typing import Any, Awaitable, Callable, TypeVar

import structlog
from pydantic import TypeAdapter

from is_it_down.cache.redis_secret import RedisSecretConfigurationError, resolve_api_cache_redis_url
from is_it_down.settings import get_settings

try:
    from redis.asyncio import Redis

    _REDIS_LIBRARY_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised in environments without redis installed.
    Redis = Any  # type: ignore[assignment,misc]
    _REDIS_LIBRARY_AVAILABLE = False

logger = structlog.get_logger(__name__)
_CACHE_FALLBACK_PREFIX = "is-it-down:api:v1"
T = TypeVar("T")


class ApiResponseCache:
    """Represent `ApiResponseCache`."""

    def __init__(self) -> None:
        """Initialize cache state from settings."""
        settings = get_settings()
        prefix = settings.api_cache_key_prefix.strip()
        self._enabled = settings.api_cache_enabled
        self._prefix = prefix or _CACHE_FALLBACK_PREFIX
        self._default_ttl_seconds = max(1, settings.api_cache_ttl_seconds)
        self._redis: Redis | None = None
        self._redis_init_lock = asyncio.Lock()
        self._redis_init_failed = False

    @property
    def enabled(self) -> bool:
        """Enabled.

        Returns:
            True when cache is enabled; otherwise, False.
        """
        return self._enabled

    def build_key(self, cache_key: str) -> str:
        """Build key.

        Args:
            cache_key: Logical cache key.

        Returns:
            The resulting value.
        """
        return f"{self._prefix}:{cache_key}"

    async def backend_available(self) -> bool:
        """Backend available.

        Returns:
            True when a Redis backend is available; otherwise, False.
        """
        return await self._redis_client() is not None

    async def _redis_client(self) -> Redis | None:
        """Redis client.

        Returns:
            The resulting value.
        """
        if not self._enabled:
            return None
        if self._redis is not None:
            return self._redis
        if self._redis_init_failed:
            return None
        if not _REDIS_LIBRARY_AVAILABLE:
            self._redis_init_failed = True
            logger.warning("api.cache_disabled_missing_redis_library")
            return None

        async with self._redis_init_lock:
            if self._redis is not None:
                return self._redis
            if self._redis_init_failed:
                return None

            try:
                redis_url = await resolve_api_cache_redis_url()
                client: Redis = Redis.from_url(
                    redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    health_check_interval=30,
                    socket_timeout=2,
                    socket_connect_timeout=2,
                )
                await client.ping()
                self._redis = client
                return self._redis
            except RedisSecretConfigurationError:
                self._redis_init_failed = True
                logger.warning("api.cache_disabled_secret_configuration_error", exc_info=True)
                return None
            except Exception:
                self._redis_init_failed = True
                logger.warning("api.cache_disabled_redis_init_failed", exc_info=True)
                return None

    async def close(self) -> None:
        """Close cache resources."""
        client = self._redis
        self._redis = None
        if client is None:
            return
        try:
            await client.aclose()
        except AttributeError:  # pragma: no cover - compatibility fallback.
            await client.close()  # type: ignore[func-returns-value]

    async def _write(
        self,
        *,
        full_key: str,
        value: T,
        adapter: TypeAdapter[T],
        ttl_seconds: int | None,
        redis_client: Redis | None,
    ) -> None:
        """Write.

        Args:
            full_key: Fully namespaced Redis key.
            value: The value to serialize.
            adapter: Type adapter used for JSON serialization.
            ttl_seconds: Optional per-call ttl override.
            redis_client: Redis client to use.
        """
        if redis_client is None:
            return

        encoded_value = adapter.dump_python(value, mode="json")
        ttl = self._default_ttl_seconds if ttl_seconds is None else max(1, ttl_seconds)
        try:
            payload = json.dumps(encoded_value, separators=(",", ":"), sort_keys=True)
            await redis_client.set(full_key, payload, ex=ttl)
        except Exception:
            logger.warning("api.cache_write_failed", key=full_key, ttl=ttl, exc_info=True)

    async def get_or_set(
        self,
        *,
        cache_key: str,
        adapter: TypeAdapter[T],
        loader: Callable[[], Awaitable[T]],
        ttl_seconds: int | None = None,
    ) -> T:
        """Get or set.

        Args:
            cache_key: Logical cache key.
            adapter: Type adapter used for JSON decode/encode.
            loader: Async loader executed on cache miss.
            ttl_seconds: Optional per-call ttl override.

        Returns:
            The resulting value.
        """
        full_key = self.build_key(cache_key)
        redis_client = await self._redis_client()
        if redis_client is not None:
            try:
                payload = await redis_client.get(full_key)
                if payload is not None:
                    value = adapter.validate_json(payload)
                    logger.debug("api.cache_hit", key=full_key)
                    return value
            except Exception:
                logger.warning("api.cache_read_failed", key=full_key, exc_info=True)

        value = await loader()
        logger.debug("api.cache_miss", key=full_key)
        await self._write(
            full_key=full_key,
            value=value,
            adapter=adapter,
            ttl_seconds=ttl_seconds,
            redis_client=redis_client,
        )
        return value

    async def refresh(
        self,
        *,
        cache_key: str,
        adapter: TypeAdapter[T],
        loader: Callable[[], Awaitable[T]],
        ttl_seconds: int | None = None,
    ) -> T:
        """Refresh.

        Args:
            cache_key: Logical cache key.
            adapter: Type adapter used for JSON decode/encode.
            loader: Async loader executed unconditionally.
            ttl_seconds: Optional per-call ttl override.

        Returns:
            The resulting value.
        """
        full_key = self.build_key(cache_key)
        value = await loader()
        await self._write(
            full_key=full_key,
            value=value,
            adapter=adapter,
            ttl_seconds=ttl_seconds,
            redis_client=await self._redis_client(),
        )
        return value


@lru_cache(maxsize=1)
def get_api_response_cache() -> ApiResponseCache:
    """Get api response cache.

    Returns:
        The resulting value.
    """
    return ApiResponseCache()


async def close_api_response_cache() -> None:
    """Close api response cache."""
    await get_api_response_cache().close()

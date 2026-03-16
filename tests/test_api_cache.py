import asyncio
import json

import pytest
from pydantic import TypeAdapter

from is_it_down.api.cache import ApiResponseCache
from is_it_down.settings import get_settings


class FakeRedis:
    def __init__(
        self,
        *,
        initial: dict[str, str] | None = None,
        raise_get: bool = False,
        raise_set: bool = False,
    ) -> None:
        self.store = dict(initial or {})
        self.raise_get = raise_get
        self.raise_set = raise_set
        self.last_set: tuple[str, str, int | None] | None = None
        self.closed = False

    async def get(self, key: str) -> str | None:
        if self.raise_get:
            raise RuntimeError("get failed")
        return self.store.get(key)

    async def set(self, key: str, payload: str, ex: int | None = None) -> None:
        if self.raise_set:
            raise RuntimeError("set failed")
        self.store[key] = payload
        self.last_set = (key, payload, ex)

    async def ping(self) -> bool:
        return True

    async def aclose(self) -> None:
        self.closed = True


def _reset_settings_cache() -> None:
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_get_or_set_miss_executes_loader_and_writes_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_ENABLED", "true")
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_TTL_SECONDS", "42")
    _reset_settings_cache()

    cache = ApiResponseCache()
    fake_redis = FakeRedis()
    cache._redis = fake_redis
    adapter = TypeAdapter(dict[str, int])
    called = 0

    async def loader() -> dict[str, int]:
        nonlocal called
        called += 1
        return {"value": 7}

    result = await cache.get_or_set(cache_key="services:list", adapter=adapter, loader=loader)

    assert result == {"value": 7}
    assert called == 1
    assert fake_redis.last_set is not None
    cache_key, payload, ttl = fake_redis.last_set
    assert cache_key == cache.build_key("services:list")
    assert ttl == 42
    assert json.loads(payload) == {"value": 7}


@pytest.mark.asyncio
async def test_get_or_set_hit_avoids_loader(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_ENABLED", "true")
    _reset_settings_cache()

    cache = ApiResponseCache()
    key = cache.build_key("incidents:open")
    fake_redis = FakeRedis(initial={key: json.dumps([{"incident_id": 1}])})
    cache._redis = fake_redis
    adapter = TypeAdapter(list[dict[str, int]])
    called = 0

    async def loader() -> list[dict[str, int]]:
        nonlocal called
        called += 1
        return [{"incident_id": 9}]

    result = await cache.get_or_set(cache_key="incidents:open", adapter=adapter, loader=loader)

    assert result == [{"incident_id": 1}]
    assert called == 0


@pytest.mark.asyncio
async def test_get_or_set_redis_read_failure_falls_back_to_loader(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_ENABLED", "true")
    _reset_settings_cache()

    cache = ApiResponseCache()
    fake_redis = FakeRedis(raise_get=True)
    cache._redis = fake_redis
    adapter = TypeAdapter(list[int])

    async def loader() -> list[int]:
        return [1, 2, 3]

    result = await cache.get_or_set(cache_key="numbers", adapter=adapter, loader=loader)

    assert result == [1, 2, 3]


@pytest.mark.asyncio
async def test_refresh_overwrites_existing_cached_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_ENABLED", "true")
    _reset_settings_cache()

    cache = ApiResponseCache()
    key = cache.build_key("services:github:detail")
    fake_redis = FakeRedis(initial={key: json.dumps({"score": 10})})
    cache._redis = fake_redis
    adapter = TypeAdapter(dict[str, int])

    async def loader() -> dict[str, int]:
        return {"score": 99}

    result = await cache.refresh(cache_key="services:github:detail", adapter=adapter, loader=loader)

    assert result == {"score": 99}
    assert json.loads(fake_redis.store[key]) == {"score": 99}


@pytest.mark.asyncio
async def test_get_or_set_coalesces_concurrent_cache_misses(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_ENABLED", "true")
    _reset_settings_cache()

    cache = ApiResponseCache()
    fake_redis = FakeRedis()
    cache._redis = fake_redis
    adapter = TypeAdapter(dict[str, int])
    called = 0

    async def loader() -> dict[str, int]:
        nonlocal called
        called += 1
        await asyncio.sleep(0.01)
        return {"value": 11}

    results = await asyncio.gather(
        *(
            cache.get_or_set(cache_key="services:list", adapter=adapter, loader=loader)
            for _ in range(8)
        )
    )

    assert results == [{"value": 11}] * 8
    assert called == 1


@pytest.mark.asyncio
async def test_get_or_set_uses_in_memory_fallback_when_redis_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_ENABLED", "true")
    _reset_settings_cache()

    cache = ApiResponseCache()
    cache._redis_init_failed = True
    adapter = TypeAdapter(dict[str, int])
    called = 0

    async def loader() -> dict[str, int]:
        nonlocal called
        called += 1
        return {"value": 21}

    first = await cache.get_or_set(cache_key="services:github:detail", adapter=adapter, loader=loader)
    second = await cache.get_or_set(cache_key="services:github:detail", adapter=adapter, loader=loader)

    assert first == {"value": 21}
    assert second == {"value": 21}
    assert called == 1


@pytest.mark.asyncio
async def test_get_or_set_does_not_use_memory_cache_when_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_ENABLED", "false")
    _reset_settings_cache()

    cache = ApiResponseCache()
    cache._redis_init_failed = True
    adapter = TypeAdapter(dict[str, int])
    called = 0

    async def loader() -> dict[str, int]:
        nonlocal called
        called += 1
        return {"value": 33}

    await cache.get_or_set(cache_key="services:list", adapter=adapter, loader=loader)
    await cache.get_or_set(cache_key="services:list", adapter=adapter, loader=loader)

    assert called == 2


@pytest.mark.asyncio
async def test_get_or_set_skips_large_payloads_in_memory_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_ENABLED", "true")
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_MEMORY_MAX_PAYLOAD_BYTES", "16")
    _reset_settings_cache()

    cache = ApiResponseCache()
    cache._redis_init_failed = True
    adapter = TypeAdapter(dict[str, str])
    called = 0

    async def loader() -> dict[str, str]:
        nonlocal called
        called += 1
        return {"value": "x" * 32}

    await cache.get_or_set(cache_key="services:checker-trends:24h", adapter=adapter, loader=loader)
    await cache.get_or_set(cache_key="services:checker-trends:24h", adapter=adapter, loader=loader)

    assert called == 2
    assert cache._memory_cache == {}
    assert cache._memory_cache_bytes == 0


@pytest.mark.asyncio
async def test_get_or_set_evicts_oldest_memory_payloads_by_total_size(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_ENABLED", "true")
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_MEMORY_MAX_BYTES", "48")
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_MEMORY_MAX_PAYLOAD_BYTES", "48")
    monkeypatch.setenv("IS_IT_DOWN_API_CACHE_MEMORY_MAX_ENTRIES", "4")
    _reset_settings_cache()

    cache = ApiResponseCache()
    cache._redis_init_failed = True
    adapter = TypeAdapter(dict[str, str])

    await cache.get_or_set(
        cache_key="services:github:detail",
        adapter=adapter,
        loader=lambda: asyncio.sleep(0, result={"value": "a" * 18}),
    )
    await cache.get_or_set(
        cache_key="services:stripe:detail",
        adapter=adapter,
        loader=lambda: asyncio.sleep(0, result={"value": "b" * 18}),
    )

    assert cache.build_key("services:github:detail") not in cache._memory_cache
    assert cache.build_key("services:stripe:detail") in cache._memory_cache
    assert cache._memory_cache_bytes <= 48

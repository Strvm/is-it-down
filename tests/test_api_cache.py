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

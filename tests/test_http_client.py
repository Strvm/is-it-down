from __future__ import annotations

import json

import httpx
import pytest

from is_it_down.checkers.http_client import BoundedAsyncClient, response_body_truncation_metadata


@pytest.mark.asyncio
async def test_bounded_async_client_truncates_non_json_response() -> None:
    def _handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            text="a" * 128,
            headers={"content-type": "text/plain"},
            request=request,
        )

    async with BoundedAsyncClient(
        transport=httpx.MockTransport(_handler),
        max_response_body_bytes=32,
        max_json_response_body_bytes=64,
    ) as client:
        response = await client.get("https://example.com/plain")

    assert response.status_code == 200
    assert len(response.content) == 32
    assert response_body_truncation_metadata(response) == {
        "body_truncated_by_client": True,
        "body_limit_bytes": 32,
        "body_size_bytes": 32,
    }


@pytest.mark.asyncio
async def test_bounded_async_client_uses_json_specific_limit() -> None:
    payload = {"message": "x" * 80}

    def _handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            content=json.dumps(payload),
            headers={"content-type": "application/json"},
            request=request,
        )

    async with BoundedAsyncClient(
        transport=httpx.MockTransport(_handler),
        max_response_body_bytes=32,
        max_json_response_body_bytes=1024,
    ) as client:
        response = await client.get("https://example.com/json")

    assert response.json() == payload
    assert response_body_truncation_metadata(response) == {}

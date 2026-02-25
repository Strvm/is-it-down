from __future__ import annotations

import httpx

from is_it_down.checkers.utils import json_dict_or_none, json_list_or_none


def _response_with_json(payload: object) -> httpx.Response:
    request = httpx.Request("GET", "https://example.com")
    return httpx.Response(200, json=payload, request=request)


def _response_with_text(payload: str) -> httpx.Response:
    request = httpx.Request("GET", "https://example.com")
    return httpx.Response(200, text=payload, request=request)


def test_json_dict_or_none_returns_mapping() -> None:
    response = _response_with_json({"status": "ok"})
    assert json_dict_or_none(response) == {"status": "ok"}


def test_json_dict_or_none_returns_none_for_non_mapping() -> None:
    response = _response_with_json(["a", "b"])
    assert json_dict_or_none(response) is None


def test_json_dict_or_none_returns_none_for_invalid_json() -> None:
    response = _response_with_text("not json")
    assert json_dict_or_none(response) is None


def test_json_list_or_none_returns_list() -> None:
    response = _response_with_json([{"id": 1}])
    assert json_list_or_none(response) == [{"id": 1}]


def test_json_list_or_none_returns_none_for_non_list() -> None:
    response = _response_with_json({"id": 1})
    assert json_list_or_none(response) is None


def test_json_list_or_none_returns_none_for_invalid_json() -> None:
    response = _response_with_text("invalid")
    assert json_list_or_none(response) is None

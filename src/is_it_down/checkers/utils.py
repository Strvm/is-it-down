"""Provide functionality for `is_it_down.checkers.utils`."""

import json
from datetime import timedelta
from typing import Any, Final

import httpx

from is_it_down.core.models import ServiceStatus

_STATUSPAGE_DEGRADED: Final[set[str]] = {"minor", "major", "maintenance"}
_STATUSPAGE_DOWN: Final[set[str]] = {"critical"}
_ACCESS_CHALLENGE_MARKERS: Final[tuple[str, ...]] = (
    "just a moment",
    "verifying your connection",
    "attention required",
    "request blocked",
    "access denied",
    "captcha",
    "cloudflare",
    "security checkpoint",
    "security check",
    "bot detection",
    "too many requests",
    "rate limit",
)


def json_dict_or_none(response: httpx.Response) -> dict[str, Any] | None:
    """Json dict or none.
    
    Args:
        response: The response value.
    
    Returns:
        The resulting value.
    """
    try:
        payload = response.json()
    except ValueError:
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def json_list_or_none(response: httpx.Response) -> list[Any] | None:
    """Json list or none.
    
    Args:
        response: The response value.
    
    Returns:
        The resulting value.
    """
    try:
        payload = response.json()
    except ValueError:
        return None
    if not isinstance(payload, list):
        return None
    return payload


def response_latency_ms(response: httpx.Response) -> int:
    """Response latency ms.
    
    Args:
        response: The response value.
    
    Returns:
        The resulting value.
    """
    return int(response.elapsed.total_seconds() * 1000)


def status_from_http(response: httpx.Response) -> ServiceStatus:
    """Status from http.
    
    Args:
        response: The response value.
    
    Returns:
        The resulting value.
    """
    if response.status_code in {401, 403, 429}:
        try:
            page_text = response.text.lower()
        except Exception:
            page_text = ""
        if any(marker in page_text for marker in _ACCESS_CHALLENGE_MARKERS):
            return "up"
    if response.status_code >= 500:
        return "down"
    if response.status_code >= 400:
        return "degraded"
    return "up"


def apply_statuspage_indicator(base_status: ServiceStatus, indicator: str | None) -> ServiceStatus:
    """Apply statuspage indicator.
    
    Args:
        base_status: The base status value.
        indicator: The indicator value.
    
    Returns:
        The resulting value.
    """
    if indicator in _STATUSPAGE_DOWN:
        return "down"
    if indicator in _STATUSPAGE_DEGRADED:
        return "degraded"
    return base_status


def _truncated_text(value: str, *, max_chars: int) -> tuple[str, bool]:
    """Truncated text.
    
    Args:
        value: The value value.
        max_chars: The max chars value.
    
    Returns:
        The resulting value.
    """
    if len(value) <= max_chars:
        return value, False
    return value[:max_chars], True


def build_response_debug_blob(
    response: httpx.Response,
    *,
    body_char_limit: int = 1000,
) -> dict[str, Any]:
    """Build response debug blob.
    
    Args:
        response: The response value.
        body_char_limit: The body char limit value.
    
    Returns:
        The resulting value.
    """
    debug: dict[str, Any] = {
        "status_code": response.status_code,
        "reason_phrase": response.reason_phrase,
        "url": str(response.request.url) if response.request is not None else None,
        "content_type": response.headers.get("content-type", ""),
    }

    try:
        body = response.text
    except Exception as exc:  # pragma: no cover - defensive path
        debug["body_read_error"] = str(exc)
        return debug

    if not body:
        debug["body_preview"] = ""
        return debug

    body_preview, body_truncated = _truncated_text(body, max_chars=body_char_limit)
    debug["body_preview"] = body_preview
    debug["body_truncated"] = body_truncated

    content_type = debug["content_type"] or ""
    if "json" in content_type.lower():
        try:
            payload = response.json()
            payload_text = json.dumps(payload, sort_keys=True)
            json_preview, json_truncated = _truncated_text(payload_text, max_chars=body_char_limit)
            debug["json_preview"] = json_preview
            debug["json_truncated"] = json_truncated
        except Exception:
            pass

    return debug


def add_non_up_debug_metadata(
    *,
    metadata: dict[str, Any],
    status: ServiceStatus,
    response: httpx.Response,
    body_char_limit: int = 1000,
) -> dict[str, Any]:
    """Add non up debug metadata.
    
    Args:
        metadata: The metadata value.
        status: The status value.
        response: The response value.
        body_char_limit: The body char limit value.
    
    Returns:
        The resulting value.
    """
    if status == "up":
        return metadata
    metadata.setdefault(
        "debug",
        build_response_debug_blob(response, body_char_limit=body_char_limit),
    )
    return metadata


async def safe_get(client: httpx.AsyncClient, url: str, **kwargs: Any) -> httpx.Response:
    """Issue a GET request with a direct-network fallback for proxy failures.

    Args:
        client: The client value.
        url: The url value.
        **kwargs: Additional keyword arguments for the request.

    Returns:
        The resulting value.
    """
    request = client.build_request("GET", url, **kwargs)

    try:
        return await client.send(request)
    except httpx.ProxyError:
        try:
            async with httpx.AsyncClient(
                timeout=client.timeout,
                headers=dict(client.headers),
                follow_redirects=client.follow_redirects,
                trust_env=False,
            ) as direct_client:
                direct_request = direct_client.build_request("GET", url, **kwargs)
                return await direct_client.send(direct_request)
        except httpx.HTTPError as exc:
            response = httpx.Response(
                status_code=599,
                request=request,
                text=str(exc),
                headers={"content-type": "text/plain; charset=utf-8"},
            )
            response.elapsed = timedelta(0)
            return response
    except httpx.HTTPError as exc:
        response = httpx.Response(
            status_code=599,
            request=request,
            text=str(exc),
            headers={"content-type": "text/plain; charset=utf-8"},
        )
        response.elapsed = timedelta(0)
        return response

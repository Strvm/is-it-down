"""Provide bounded HTTP client utilities for service checker execution."""

from __future__ import annotations

from typing import Any

import httpx

BODY_TRUNCATED_EXTENSION_KEY = "is_it_down_body_truncated"
BODY_LIMIT_EXTENSION_KEY = "is_it_down_body_limit_bytes"
BODY_SIZE_EXTENSION_KEY = "is_it_down_body_size_bytes"


def body_limit_kwargs_from_client(client: httpx.AsyncClient) -> dict[str, int]:
    """Body limit kwargs from client.

    Args:
        client: The client value.

    Returns:
        The resulting value.
    """
    kwargs: dict[str, int] = {}

    max_response_body_bytes = getattr(client, "max_response_body_bytes", None)
    if isinstance(max_response_body_bytes, int) and max_response_body_bytes > 0:
        kwargs["max_response_body_bytes"] = max_response_body_bytes

    max_json_response_body_bytes = getattr(client, "max_json_response_body_bytes", None)
    if isinstance(max_json_response_body_bytes, int) and max_json_response_body_bytes > 0:
        kwargs["max_json_response_body_bytes"] = max_json_response_body_bytes

    return kwargs


def response_body_truncation_metadata(response: httpx.Response) -> dict[str, int | bool]:
    """Response body truncation metadata.

    Args:
        response: The response value.

    Returns:
        The resulting value.
    """
    if response.extensions.get(BODY_TRUNCATED_EXTENSION_KEY) is not True:
        return {}

    metadata: dict[str, int | bool] = {"body_truncated_by_client": True}
    limit_bytes = response.extensions.get(BODY_LIMIT_EXTENSION_KEY)
    if isinstance(limit_bytes, int):
        metadata["body_limit_bytes"] = limit_bytes

    body_size_bytes = response.extensions.get(BODY_SIZE_EXTENSION_KEY)
    if isinstance(body_size_bytes, int):
        metadata["body_size_bytes"] = body_size_bytes

    return metadata


class BoundedAsyncClient(httpx.AsyncClient):
    """Represent `BoundedAsyncClient`."""

    def __init__(
        self,
        *args: Any,
        max_response_body_bytes: int,
        max_json_response_body_bytes: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize.

        Args:
            *args: Positional arguments forwarded to `httpx.AsyncClient`.
            max_response_body_bytes: Maximum decoded bytes to keep for non-JSON responses.
            max_json_response_body_bytes: Maximum decoded bytes to keep for JSON responses.
            **kwargs: Keyword arguments forwarded to `httpx.AsyncClient`.

        Raises:
            ValueError: If an error occurs while executing this function.
        """
        if max_response_body_bytes <= 0:
            raise ValueError("max_response_body_bytes must be greater than 0.")

        if max_json_response_body_bytes is not None and max_json_response_body_bytes <= 0:
            raise ValueError("max_json_response_body_bytes must be greater than 0 when provided.")

        super().__init__(*args, **kwargs)

        self.max_response_body_bytes = max_response_body_bytes
        self.max_json_response_body_bytes = max_json_response_body_bytes or max_response_body_bytes

    async def send(
        self,
        request: httpx.Request,
        *,
        stream: bool = False,
        auth: Any = httpx.USE_CLIENT_DEFAULT,
        follow_redirects: bool | Any = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        """Send request with bounded body buffering.

        Args:
            request: The request value.
            stream: The stream value.
            auth: The auth value.
            follow_redirects: The follow redirects value.

        Returns:
            The resulting value.
        """
        if stream:
            return await super().send(
                request,
                stream=True,
                auth=auth,
                follow_redirects=follow_redirects,
            )

        response = await super().send(
            request,
            stream=True,
            auth=auth,
            follow_redirects=follow_redirects,
        )

        body_limit = self._body_limit_for_response(response)
        try:
            content, truncated = await _read_limited_response_content(response=response, max_bytes=body_limit)
        except BaseException:
            await response.aclose()
            raise

        response._content = content
        if hasattr(response, "_text"):
            delattr(response, "_text")

        if truncated:
            response.extensions[BODY_TRUNCATED_EXTENSION_KEY] = True
            response.extensions[BODY_LIMIT_EXTENSION_KEY] = body_limit
            response.extensions[BODY_SIZE_EXTENSION_KEY] = len(content)

        return response

    def _body_limit_for_response(self, response: httpx.Response) -> int:
        """Body limit for response.

        Args:
            response: The response value.

        Returns:
            The resulting value.
        """
        content_type = response.headers.get("content-type", "").lower()
        if "json" in content_type:
            return self.max_json_response_body_bytes
        return self.max_response_body_bytes


async def _read_limited_response_content(
    *,
    response: httpx.Response,
    max_bytes: int,
) -> tuple[bytes, bool]:
    """Read limited response content.

    Args:
        response: The response value.
        max_bytes: The max bytes value.

    Returns:
        The resulting value.
    """
    if max_bytes <= 0:
        await response.aclose()
        return b"", True

    chunks: list[bytes] = []
    bytes_read = 0
    truncated = False

    async for chunk in response.aiter_bytes():
        if not chunk:
            continue

        remaining = max_bytes - bytes_read
        if remaining <= 0:
            truncated = True
            break

        if len(chunk) > remaining:
            chunks.append(chunk[:remaining])
            bytes_read += remaining
            truncated = True
            break

        chunks.append(chunk)
        bytes_read += len(chunk)

    if truncated:
        await response.aclose()

    return b"".join(chunks), truncated

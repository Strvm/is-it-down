"""Provide functionality for `is_it_down.checkers.services.openai`."""

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

import httpx

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.utils import (
    add_non_up_debug_metadata,
    apply_statuspage_indicator,
    json_dict_or_none,
    response_latency_ms,
    status_from_http,
)
from is_it_down.core.models import CheckResult


def _score_unauthenticated_api_response(response: httpx.Response) -> tuple[str, dict[str, Any]]:
    """Score unauthenticated api response."""
    status = status_from_http(response)
    metadata: dict[str, Any] = {"expected_http_statuses": [401, 403]}

    if response.status_code in {401, 403}:
        status = "up"
        payload = json_dict_or_none(response)
        if payload is None:
            metadata["error_payload_present"] = False
        else:
            error_payload = payload.get("error")
            metadata["error_payload_present"] = isinstance(error_payload, dict)
            if isinstance(error_payload, dict):
                error_type = error_payload.get("type")
                error_code = error_payload.get("code")
                error_message = error_payload.get("message")
                metadata["error_type"] = error_type
                if isinstance(error_code, str):
                    metadata["error_code"] = error_code
                metadata["error_message_present"] = isinstance(error_message, str) and bool(error_message.strip())
                if not isinstance(error_type, str) or not error_type:
                    status = "degraded"
            else:
                status = "degraded"
    elif response.is_success:
        status = "degraded"
        metadata["unexpected_success"] = True

    return status, metadata


class OpenAIStatusPageCheck(BaseCheck):
    """Represent `OpenAIStatusPageCheck`."""

    check_key = "openai_status_page"
    endpoint_key = "https://status.openai.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.4

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        """Run."""
        response = await client.get(self.endpoint_key)
        status = status_from_http(response)
        metadata: dict[str, Any] = {}

        if response.is_success:
            payload = json_dict_or_none(response)
            if payload is None:
                status = "degraded"
            else:
                status_block = payload.get("status")
                indicator: str | None = None
                description: str | None = None

                if isinstance(status_block, dict):
                    raw_indicator = status_block.get("indicator")
                    raw_description = status_block.get("description")
                    if isinstance(raw_indicator, str):
                        indicator = raw_indicator
                    if isinstance(raw_description, str):
                        description = raw_description
                else:
                    status = "degraded"

                metadata["indicator"] = indicator
                if description is not None:
                    metadata["description"] = description

                status = apply_statuspage_indicator(status, indicator)
                if indicator is None:
                    status = "degraded"
        add_non_up_debug_metadata(metadata=metadata, status=status, response=response)

        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=response_latency_ms(response),
            http_status=response.status_code,
            metadata=metadata,
        )


class OpenAIApiModelsAuthCheck(BaseCheck):
    """Represent `OpenAIApiModelsAuthCheck`."""

    check_key = "openai_api_models_auth"
    endpoint_key = "https://api.openai.com/v1/models"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.35
    proxy_setting = "default"

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        """Run."""
        response = await client.get(self.endpoint_key, headers={"Accept": "application/json"})
        status, metadata = _score_unauthenticated_api_response(response)
        add_non_up_debug_metadata(metadata=metadata, status=status, response=response)

        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=response_latency_ms(response),
            http_status=response.status_code,
            metadata=metadata,
        )


class OpenAIApiFilesAuthCheck(BaseCheck):
    """Represent `OpenAIApiFilesAuthCheck`."""

    check_key = "openai_api_files_auth"
    endpoint_key = "https://api.openai.com/v1/files"
    interval_seconds = 60
    timeout_seconds = 5.0
    proxy_setting = "default"

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        """Run."""
        response = await client.get(self.endpoint_key, headers={"Accept": "application/json"})
        status, metadata = _score_unauthenticated_api_response(response)
        add_non_up_debug_metadata(metadata=metadata, status=status, response=response)

        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=response_latency_ms(response),
            http_status=response.status_code,
            metadata=metadata,
        )


class OpenAIServiceChecker(BaseServiceChecker):
    """Represent `OpenAIServiceChecker`."""

    service_key = "openai"
    logo_url = "https://img.logo.dev/openai.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.openai.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks."""
        return [
            OpenAIStatusPageCheck(),
            OpenAIApiModelsAuthCheck(),
            OpenAIApiFilesAuthCheck(),
        ]

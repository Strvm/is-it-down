from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

import httpx

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.services.cloudflare import CloudflareServiceChecker
from is_it_down.checkers.utils import add_non_up_debug_metadata, response_latency_ms
from is_it_down.core.models import CheckResult, ServiceStatus


class _BungiePlatformCheck(BaseCheck):
    def _score_response(
        self,
        response: httpx.Response,
        payload: dict[str, Any] | None,
        *,
        expected_response_type: type,
    ) -> tuple[ServiceStatus, dict[str, Any]]:
        status_code = response.status_code

        metadata: dict[str, Any] = {
            "status_code": status_code,
            "content_type": response.headers.get("content-type", ""),
        }

        error_code: int | None = None
        error_status: str | None = None
        if payload is not None:
            error_code = payload.get("ErrorCode")
            error_status = payload.get("ErrorStatus")
            metadata["bungie_error_code"] = error_code
            metadata["bungie_error_status"] = error_status

        if error_status in {"ApiKeyMissingFromRequest", "AuthenticationInvalid"}:
            metadata["auth_required"] = True
            return "up", metadata

        if status_code >= 500:
            return "down", metadata

        if status_code == 429:
            return "degraded", metadata

        if status_code in {401, 403}:
            # Missing/invalid API key can still indicate platform reachability.
            if payload is not None and "ErrorCode" in payload:
                return "up", metadata
            return "degraded", metadata

        if status_code >= 400:
            return "degraded", metadata

        if payload is None:
            return "degraded", metadata

        if "Response" not in payload:
            return "degraded", metadata

        if not isinstance(payload.get("Response"), expected_response_type):
            return "degraded", metadata

        if error_status == "Success" and error_code in {1, 0, None}:
            return "up", metadata

        if error_code not in {0, 1, None}:
            return "degraded", metadata

        return "up", metadata

    def _parse_payload(self, response: httpx.Response) -> dict[str, Any] | None:
        try:
            data = response.json()
        except ValueError:
            return None

        if not isinstance(data, dict):
            return None
        return data


class DestinyManifestCheck(_BungiePlatformCheck):
    check_key = "destiny_manifest"
    endpoint_key = "https://www.bungie.net/Platform/Destiny2/Manifest/"
    interval_seconds = 60
    timeout_seconds = 6.0
    weight = 0.5

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        response = await client.get(self.endpoint_key)
        payload = self._parse_payload(response)

        status, metadata = self._score_response(
            response,
            payload,
            expected_response_type=dict,
        )

        if payload is not None and isinstance(payload.get("Response"), dict):
            response_keys = list(payload["Response"].keys())
            metadata["response_keys"] = response_keys[:8]
        add_non_up_debug_metadata(metadata=metadata, status=status, response=response)

        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=response_latency_ms(response),
            http_status=response.status_code,
            metadata=metadata,
        )


class DestinyGlobalAlertsCheck(_BungiePlatformCheck):
    check_key = "destiny_global_alerts"
    endpoint_key = "https://www.bungie.net/Platform/GlobalAlerts/?includestreaming=false"
    interval_seconds = 60
    timeout_seconds = 6.0

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        response = await client.get(self.endpoint_key)
        payload = self._parse_payload(response)

        status, metadata = self._score_response(
            response,
            payload,
            expected_response_type=list,
        )

        if payload is not None and isinstance(payload.get("Response"), list):
            metadata["active_alert_count"] = len(payload["Response"])
        add_non_up_debug_metadata(metadata=metadata, status=status, response=response)

        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=response_latency_ms(response),
            http_status=response.status_code,
            metadata=metadata,
        )


class DestinyClanBannerDictionaryCheck(_BungiePlatformCheck):
    check_key = "destiny_clan_banner_dictionary"
    endpoint_key = "https://www.bungie.net/Platform/Destiny2/Clan/ClanBannerDictionary/"
    interval_seconds = 60
    timeout_seconds = 6.0

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        response = await client.get(self.endpoint_key)
        payload = self._parse_payload(response)

        status, metadata = self._score_response(
            response,
            payload,
            expected_response_type=dict,
        )

        if payload is not None and isinstance(payload.get("Response"), dict):
            metadata["banner_option_count"] = len(payload["Response"])
        add_non_up_debug_metadata(metadata=metadata, status=status, response=response)

        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=response_latency_ms(response),
            http_status=response.status_code,
            metadata=metadata,
        )


class DestinyServiceChecker(BaseServiceChecker):
    service_key = "destiny"
    logo_url = "https://cdn.simpleicons.org/bungie"
    official_uptime = "https://help.bungie.net/hc/en-us/articles/360049199271-Destiny-Server-and-Update-Status"
    dependencies: Sequence[type[BaseServiceChecker]] = (CloudflareServiceChecker,)

    def build_checks(self) -> Sequence[BaseCheck]:
        return [
            DestinyManifestCheck(),
            DestinyGlobalAlertsCheck(),
            DestinyClanBannerDictionaryCheck(),
        ]

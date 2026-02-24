from typing import Final

import httpx

from is_it_down.core.models import ServiceStatus

_STATUSPAGE_DEGRADED: Final[set[str]] = {"minor", "major"}
_STATUSPAGE_DOWN: Final[set[str]] = {"critical", "maintenance"}


def response_latency_ms(response: httpx.Response) -> int:
    return int(response.elapsed.total_seconds() * 1000)


def status_from_http(response: httpx.Response) -> ServiceStatus:
    if response.status_code >= 500:
        return "down"
    if response.status_code >= 400:
        return "degraded"
    return "up"


def apply_statuspage_indicator(base_status: ServiceStatus, indicator: str | None) -> ServiceStatus:
    if indicator in _STATUSPAGE_DOWN:
        return "down"
    if indicator in _STATUSPAGE_DEGRADED:
        return "degraded"
    return base_status

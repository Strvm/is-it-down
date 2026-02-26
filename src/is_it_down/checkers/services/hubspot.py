"""Provide functionality for `is_it_down.checkers.services.hubspot`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.services.statuspage_common import (
    ApiAuthResponseCheck,
    HtmlMarkerCheck,
    StatuspageStatusCheck,
    StatuspageSummaryCheck,
)


class HubSpotStatusPageCheck(StatuspageStatusCheck):
    """Represent `HubSpotStatusPageCheck`."""

    check_key = "hubspot_status_page"
    endpoint_key = "https://status.hubspot.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class HubSpotSummaryCheck(StatuspageSummaryCheck):
    """Represent `HubSpotSummaryCheck`."""

    check_key = "hubspot_summary"
    endpoint_key = "https://status.hubspot.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class HubSpotHomepageCheck(HtmlMarkerCheck):
    """Represent `HubSpotHomepageCheck`."""

    check_key = "hubspot_homepage"
    endpoint_key = "https://www.hubspot.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("hubspot",)


class HubSpotDocsCheck(HtmlMarkerCheck):
    """Represent `HubSpotDocsCheck`."""

    check_key = "hubspot_docs"
    endpoint_key = "https://developers.hubspot.com/docs/api/overview"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("hubspot",)


class HubSpotApiAuthCheck(ApiAuthResponseCheck):
    """Represent `HubSpotApiAuthCheck`."""

    check_key = "hubspot_api_auth"
    endpoint_key = "https://api.hubapi.com/crm/v3/objects/contacts?limit=1"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    request_method = "GET"
    request_headers = {"Accept": "application/json"}
    request_json = None
    request_data = None
    expected_http_statuses = (401, 403)


class HubSpotServiceChecker(BaseServiceChecker):
    """Represent `HubSpotServiceChecker`."""

    service_key = "hubspot"
    logo_url = "https://cdn.simpleicons.org/hubspot"
    official_uptime = "https://status.hubspot.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            HubSpotStatusPageCheck(),
            HubSpotSummaryCheck(),
            HubSpotHomepageCheck(),
            HubSpotDocsCheck(),
            HubSpotApiAuthCheck(),
        ]

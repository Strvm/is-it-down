"""Provide functionality for `is_it_down.checkers.services.intercom`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.services.statuspage_common import (
    ApiAuthResponseCheck,
    HtmlMarkerCheck,
    StatuspageStatusCheck,
    StatuspageSummaryCheck,
)


class IntercomStatusPageCheck(StatuspageStatusCheck):
    """Represent `IntercomStatusPageCheck`."""

    check_key = "intercom_status_page"
    endpoint_key = "https://www.intercomstatus.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class IntercomSummaryCheck(StatuspageSummaryCheck):
    """Represent `IntercomSummaryCheck`."""

    check_key = "intercom_summary"
    endpoint_key = "https://www.intercomstatus.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class IntercomHomepageCheck(HtmlMarkerCheck):
    """Represent `IntercomHomepageCheck`."""

    check_key = "intercom_homepage"
    endpoint_key = "https://www.intercom.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("intercom",)


class IntercomDocsCheck(HtmlMarkerCheck):
    """Represent `IntercomDocsCheck`."""

    check_key = "intercom_docs"
    endpoint_key = "https://developers.intercom.com/docs/references/2.12/rest-api/api.intercom.io/admins/admin"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("intercom",)


class IntercomApiAuthCheck(ApiAuthResponseCheck):
    """Represent `IntercomApiAuthCheck`."""

    check_key = "intercom_api_auth"
    endpoint_key = "https://api.intercom.io/me"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    request_method = "GET"
    request_headers = {"Accept": "application/json", "Intercom-Version": "2.12"}
    request_json = None
    request_data = None
    expected_http_statuses = (401, 403)


class IntercomServiceChecker(BaseServiceChecker):
    """Represent `IntercomServiceChecker`."""

    service_key = "intercom"
    logo_url = "https://cdn.simpleicons.org/intercom"
    official_uptime = "https://www.intercomstatus.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            IntercomStatusPageCheck(),
            IntercomSummaryCheck(),
            IntercomHomepageCheck(),
            IntercomDocsCheck(),
            IntercomApiAuthCheck(),
        ]

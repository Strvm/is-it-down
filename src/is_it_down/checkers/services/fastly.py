"""Provide functionality for `is_it_down.checkers.services.fastly`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import (
    ApiAuthResponseCheck,
    HtmlMarkerCheck,
    StatuspageStatusCheck,
    StatuspageSummaryCheck,
)


class FastlyStatusPageCheck(StatuspageStatusCheck):
    """Represent `FastlyStatusPageCheck`."""

    check_key = "fastly_status_page"
    endpoint_key = "https://status.fastly.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    proxy_setting = "default"


class FastlySummaryCheck(StatuspageSummaryCheck):
    """Represent `FastlySummaryCheck`."""

    check_key = "fastly_summary"
    endpoint_key = "https://status.fastly.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    proxy_setting = "default"


class FastlyHomepageCheck(HtmlMarkerCheck):
    """Represent `FastlyHomepageCheck`."""

    check_key = "fastly_homepage"
    endpoint_key = "https://www.fastly.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("fastly",)


class FastlyDocsCheck(HtmlMarkerCheck):
    """Represent `FastlyDocsCheck`."""

    check_key = "fastly_docs"
    endpoint_key = "https://www.fastly.com/documentation/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("fastly",)


class FastlyApiAuthCheck(ApiAuthResponseCheck):
    """Represent `FastlyApiAuthCheck`."""

    check_key = "fastly_api_auth"
    endpoint_key = "https://api.fastly.com/current_customer"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    request_method = "GET"
    request_headers = {"Accept": "application/json"}
    request_json = None
    request_data = None
    expected_http_statuses = (401, 403)


class FastlyServiceChecker(BaseServiceChecker):
    """Represent `FastlyServiceChecker`."""

    service_key = "fastly"
    logo_url = "https://cdn.simpleicons.org/fastly"
    official_uptime = "https://status.fastly.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            FastlyStatusPageCheck(),
            FastlySummaryCheck(),
            FastlyHomepageCheck(),
            FastlyDocsCheck(),
            FastlyApiAuthCheck(),
        ]

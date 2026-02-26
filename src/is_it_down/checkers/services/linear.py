"""Provide functionality for `is_it_down.checkers.services.linear`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import (
    ApiAuthResponseCheck,
    HtmlMarkerCheck,
    StatuspageStatusCheck,
    StatuspageSummaryCheck,
)


class LinearStatusPageCheck(StatuspageStatusCheck):
    """Represent `LinearStatusPageCheck`."""

    check_key = "linear_status_page"
    endpoint_key = "https://linearstatus.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class LinearSummaryCheck(StatuspageSummaryCheck):
    """Represent `LinearSummaryCheck`."""

    check_key = "linear_summary"
    endpoint_key = "https://linearstatus.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class LinearHomepageCheck(HtmlMarkerCheck):
    """Represent `LinearHomepageCheck`."""

    check_key = "linear_homepage"
    endpoint_key = "https://linear.app/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("linear",)


class LinearDocsCheck(HtmlMarkerCheck):
    """Represent `LinearDocsCheck`."""

    check_key = "linear_docs"
    endpoint_key = "https://developers.linear.app/docs/graphql/working-with-the-graphql-api"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("linear", "graphql")


class LinearApiAuthCheck(ApiAuthResponseCheck):
    """Represent `LinearApiAuthCheck`."""

    check_key = "linear_api_auth"
    endpoint_key = "https://api.linear.app/graphql"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    request_method = "POST"
    request_headers = {"Accept": "application/json", "Content-Type": "application/json"}
    request_json = {"query": "query Viewer { viewer { id } }"}
    request_data = None
    expected_http_statuses = (401, 403)


class LinearServiceChecker(BaseServiceChecker):
    """Represent `LinearServiceChecker`."""

    service_key = "linear"
    logo_url = "https://cdn.simpleicons.org/linear"
    official_uptime = "https://linearstatus.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            LinearStatusPageCheck(),
            LinearSummaryCheck(),
            LinearHomepageCheck(),
            LinearDocsCheck(),
            LinearApiAuthCheck(),
        ]

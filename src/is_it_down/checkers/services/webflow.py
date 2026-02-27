"""Provide functionality for `is_it_down.checkers.services.webflow`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck, StatuspageStatusCheck, StatuspageSummaryCheck


class WebflowStatusApiCheck(StatuspageStatusCheck):
    """Represent `WebflowStatusApiCheck`."""

    check_key = "webflow_status_api"
    endpoint_key = "https://status.webflow.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class WebflowSummaryApiCheck(StatuspageSummaryCheck):
    """Represent `WebflowSummaryApiCheck`."""

    check_key = "webflow_summary_api"
    endpoint_key = "https://status.webflow.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class WebflowStatusPageCheck(HtmlMarkerCheck):
    """Represent `WebflowStatusPageCheck`."""

    check_key = "webflow_status_page"
    endpoint_key = "https://status.webflow.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("status",)


class WebflowHomepageCheck(HtmlMarkerCheck):
    """Represent `WebflowHomepageCheck`."""

    check_key = "webflow_homepage"
    endpoint_key = "https://webflow.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("webflow",)


class WebflowDocsCheck(HtmlMarkerCheck):
    """Represent `WebflowDocsCheck`."""

    check_key = "webflow_docs"
    endpoint_key = "https://developers.webflow.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.1
    expected_markers = ("webflow",)


class WebflowServiceChecker(BaseServiceChecker):
    """Represent `WebflowServiceChecker`."""

    service_key = "webflow"
    logo_url = "https://img.logo.dev/webflow.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.webflow.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            WebflowStatusApiCheck(),
            WebflowSummaryApiCheck(),
            WebflowStatusPageCheck(),
            WebflowHomepageCheck(),
            WebflowDocsCheck(),
        ]

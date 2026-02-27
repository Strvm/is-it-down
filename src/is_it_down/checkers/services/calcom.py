"""Provide functionality for `is_it_down.checkers.services.calcom`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class CalComStatusApiCheck(HtmlMarkerCheck):
    """Represent `CalComStatusApiCheck`."""

    check_key = "calcom_status_api"
    endpoint_key = "https://api.cal.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    required_content_type_fragment = "application/json"
    expected_markers = ("welcome to cal.com api",)


class CalComSummaryApiCheck(HtmlMarkerCheck):
    """Represent `CalComSummaryApiCheck`."""

    check_key = "calcom_summary_api"
    endpoint_key = "https://app.cal.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("cal.com",)


class CalComStatusPageCheck(HtmlMarkerCheck):
    """Represent `CalComStatusPageCheck`."""

    check_key = "calcom_status_page"
    endpoint_key = "https://status.cal.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("status",)


class CalComHomepageCheck(HtmlMarkerCheck):
    """Represent `CalComHomepageCheck`."""

    check_key = "calcom_homepage"
    endpoint_key = "https://cal.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("cal.com",)


class CalComDocsCheck(HtmlMarkerCheck):
    """Represent `CalComDocsCheck`."""

    check_key = "calcom_docs"
    endpoint_key = "https://cal.com/docs"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.1
    expected_markers = ("cal.com",)


class CalComServiceChecker(BaseServiceChecker):
    """Represent `CalComServiceChecker`."""

    service_key = "calcom"
    logo_url = "https://img.logo.dev/cal.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.cal.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            CalComStatusApiCheck(),
            CalComSummaryApiCheck(),
            CalComStatusPageCheck(),
            CalComHomepageCheck(),
            CalComDocsCheck(),
        ]

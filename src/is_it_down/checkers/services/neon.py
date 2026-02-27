"""Provide functionality for `is_it_down.checkers.services.neon`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import ApiAuthResponseCheck, HtmlMarkerCheck


class NeonStatusApiCheck(ApiAuthResponseCheck):
    """Represent `NeonStatusApiCheck`."""

    check_key = "neon_status_api"
    endpoint_key = "https://console.neon.tech/api/v2/projects"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_http_statuses = (401, 403)
    request_headers = {"Accept": "application/json"}


class NeonSummaryApiCheck(HtmlMarkerCheck):
    """Represent `NeonSummaryApiCheck`."""

    check_key = "neon_summary_api"
    endpoint_key = "https://console.neon.tech/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("neon",)


class NeonStatusPageCheck(HtmlMarkerCheck):
    """Represent `NeonStatusPageCheck`."""

    check_key = "neon_status_page"
    endpoint_key = "https://neonstatus.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("status",)


class NeonHomepageCheck(HtmlMarkerCheck):
    """Represent `NeonHomepageCheck`."""

    check_key = "neon_homepage"
    endpoint_key = "https://neon.tech/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("neon",)


class NeonDocsCheck(HtmlMarkerCheck):
    """Represent `NeonDocsCheck`."""

    check_key = "neon_docs"
    endpoint_key = "https://neon.tech/docs"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.1
    expected_markers = ("neon",)


class NeonServiceChecker(BaseServiceChecker):
    """Represent `NeonServiceChecker`."""

    service_key = "neon"
    logo_url = "https://img.logo.dev/neon.tech?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://neonstatus.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            NeonStatusApiCheck(),
            NeonSummaryApiCheck(),
            NeonStatusPageCheck(),
            NeonHomepageCheck(),
            NeonDocsCheck(),
        ]

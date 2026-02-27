"""Provide functionality for `is_it_down.checkers.services.clerk`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck, StatuspageStatusCheck


class ClerkStatusApiCheck(StatuspageStatusCheck):
    """Represent `ClerkStatusApiCheck`."""

    check_key = "clerk_status_api"
    endpoint_key = "https://status.clerk.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class ClerkSummaryApiCheck(StatuspageStatusCheck):
    """Represent `ClerkSummaryApiCheck`."""

    check_key = "clerk_summary_api"
    endpoint_key = "https://status.clerk.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class ClerkStatusPageCheck(HtmlMarkerCheck):
    """Represent `ClerkStatusPageCheck`."""

    check_key = "clerk_status_page"
    endpoint_key = "https://status.clerk.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("status",)


class ClerkHomepageCheck(HtmlMarkerCheck):
    """Represent `ClerkHomepageCheck`."""

    check_key = "clerk_homepage"
    endpoint_key = "https://clerk.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("clerk",)


class ClerkDocsCheck(HtmlMarkerCheck):
    """Represent `ClerkDocsCheck`."""

    check_key = "clerk_docs"
    endpoint_key = "https://clerk.com/docs"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.1
    expected_markers = ("clerk",)


class ClerkServiceChecker(BaseServiceChecker):
    """Represent `ClerkServiceChecker`."""

    service_key = "clerk"
    logo_url = "https://img.logo.dev/clerk.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.clerk.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            ClerkStatusApiCheck(),
            ClerkSummaryApiCheck(),
            ClerkStatusPageCheck(),
            ClerkHomepageCheck(),
            ClerkDocsCheck(),
        ]

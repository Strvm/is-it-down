"""Provide functionality for `is_it_down.checkers.services.npm`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck, StatuspageStatusCheck, StatuspageSummaryCheck


class NpmStatusApiCheck(StatuspageStatusCheck):
    """Represent `NpmStatusApiCheck`."""

    check_key = "npm_status_api"
    endpoint_key = "https://status.npmjs.org/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class NpmSummaryApiCheck(StatuspageSummaryCheck):
    """Represent `NpmSummaryApiCheck`."""

    check_key = "npm_summary_api"
    endpoint_key = "https://status.npmjs.org/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class NpmStatusPageCheck(HtmlMarkerCheck):
    """Represent `NpmStatusPageCheck`."""

    check_key = "npm_status_page"
    endpoint_key = "https://status.npmjs.org/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("status",)


class NpmHomepageCheck(HtmlMarkerCheck):
    """Represent `NpmHomepageCheck`."""

    check_key = "npm_homepage"
    endpoint_key = "https://www.npmjs.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("npm",)


class NpmDocsCheck(HtmlMarkerCheck):
    """Represent `NpmDocsCheck`."""

    check_key = "npm_docs"
    endpoint_key = "https://docs.npmjs.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.1
    expected_markers = ("npm",)


class NpmServiceChecker(BaseServiceChecker):
    """Represent `NpmServiceChecker`."""

    service_key = "npm"
    logo_url = "https://img.logo.dev/npmjs.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.npmjs.org/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            NpmStatusApiCheck(),
            NpmSummaryApiCheck(),
            NpmStatusPageCheck(),
            NpmHomepageCheck(),
            NpmDocsCheck(),
        ]

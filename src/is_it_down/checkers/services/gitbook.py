"""Provide functionality for `is_it_down.checkers.services.gitbook`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck, StatuspageStatusCheck


class GitBookStatusApiCheck(StatuspageStatusCheck):
    """Represent `GitBookStatusApiCheck`."""

    check_key = "gitbook_status_api"
    endpoint_key = "https://www.gitbookstatus.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class GitBookSummaryApiCheck(StatuspageStatusCheck):
    """Represent `GitBookSummaryApiCheck`."""

    check_key = "gitbook_summary_api"
    endpoint_key = "https://www.gitbookstatus.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class GitBookStatusPageCheck(HtmlMarkerCheck):
    """Represent `GitBookStatusPageCheck`."""

    check_key = "gitbook_status_page"
    endpoint_key = "https://www.gitbookstatus.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("status",)


class GitBookHomepageCheck(HtmlMarkerCheck):
    """Represent `GitBookHomepageCheck`."""

    check_key = "gitbook_homepage"
    endpoint_key = "https://www.gitbook.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("gitbook",)


class GitBookDocsCheck(HtmlMarkerCheck):
    """Represent `GitBookDocsCheck`."""

    check_key = "gitbook_docs"
    endpoint_key = "https://docs.gitbook.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.1
    expected_markers = ("gitbook",)


class GitBookServiceChecker(BaseServiceChecker):
    """Represent `GitBookServiceChecker`."""

    service_key = "gitbook"
    logo_url = "https://img.logo.dev/gitbook.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://www.gitbookstatus.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            GitBookStatusApiCheck(),
            GitBookSummaryApiCheck(),
            GitBookStatusPageCheck(),
            GitBookHomepageCheck(),
            GitBookDocsCheck(),
        ]

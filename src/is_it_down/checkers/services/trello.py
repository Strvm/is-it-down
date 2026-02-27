"""Provide functionality for `is_it_down.checkers.services.trello`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.services.atlassian import AtlassianServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck, StatuspageStatusCheck, StatuspageSummaryCheck


class TrelloStatusApiCheck(StatuspageStatusCheck):
    """Represent `TrelloStatusApiCheck`."""

    check_key = "trello_status_api"
    endpoint_key = "https://trello.status.atlassian.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class TrelloSummaryApiCheck(StatuspageSummaryCheck):
    """Represent `TrelloSummaryApiCheck`."""

    check_key = "trello_summary_api"
    endpoint_key = "https://trello.status.atlassian.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class TrelloStatusPageCheck(HtmlMarkerCheck):
    """Represent `TrelloStatusPageCheck`."""

    check_key = "trello_status_page"
    endpoint_key = "https://trello.status.atlassian.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("trello",)


class TrelloHomepageCheck(HtmlMarkerCheck):
    """Represent `TrelloHomepageCheck`."""

    check_key = "trello_homepage"
    endpoint_key = "https://trello.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("trello",)


class TrelloSupportCheck(HtmlMarkerCheck):
    """Represent `TrelloSupportCheck`."""

    check_key = "trello_support"
    endpoint_key = "https://support.atlassian.com/trello/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("trello",)


class TrelloServiceChecker(BaseServiceChecker):
    """Represent `TrelloServiceChecker`."""

    service_key = "trello"
    logo_url = "https://img.logo.dev/trello.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://trello.status.atlassian.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = (AtlassianServiceChecker,)

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            TrelloStatusApiCheck(),
            TrelloSummaryApiCheck(),
            TrelloStatusPageCheck(),
            TrelloHomepageCheck(),
            TrelloSupportCheck(),
        ]

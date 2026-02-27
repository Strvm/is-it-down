"""Provide functionality for `is_it_down.checkers.services.braze`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck, StatuspageStatusCheck, StatuspageSummaryCheck


class BrazeStatusApiCheck(StatuspageStatusCheck):
    """Represent `BrazeStatusApiCheck`."""

    check_key = "braze_status_api"
    endpoint_key = "https://status.braze.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class BrazeSummaryApiCheck(StatuspageSummaryCheck):
    """Represent `BrazeSummaryApiCheck`."""

    check_key = "braze_summary_api"
    endpoint_key = "https://status.braze.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class BrazeStatusPageCheck(HtmlMarkerCheck):
    """Represent `BrazeStatusPageCheck`."""

    check_key = "braze_status_page"
    endpoint_key = "https://status.braze.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("braze",)


class BrazeHomepageCheck(HtmlMarkerCheck):
    """Represent `BrazeHomepageCheck`."""

    check_key = "braze_homepage"
    endpoint_key = "https://www.braze.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("braze",)


class BrazeDocsCheck(HtmlMarkerCheck):
    """Represent `BrazeDocsCheck`."""

    check_key = "braze_docs"
    endpoint_key = "https://www.braze.com/docs/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("braze",)


class BrazeServiceChecker(BaseServiceChecker):
    """Represent `BrazeServiceChecker`."""

    service_key = "braze"
    logo_url = "https://img.logo.dev/braze.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.braze.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            BrazeStatusApiCheck(),
            BrazeSummaryApiCheck(),
            BrazeStatusPageCheck(),
            BrazeHomepageCheck(),
            BrazeDocsCheck(),
        ]

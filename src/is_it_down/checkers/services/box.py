"""Provide functionality for `is_it_down.checkers.services.box`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck, StatuspageStatusCheck, StatuspageSummaryCheck


class BoxStatusApiCheck(StatuspageStatusCheck):
    """Represent `BoxStatusApiCheck`."""

    check_key = "box_status_api"
    endpoint_key = "https://status.box.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class BoxSummaryApiCheck(StatuspageSummaryCheck):
    """Represent `BoxSummaryApiCheck`."""

    check_key = "box_summary_api"
    endpoint_key = "https://status.box.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class BoxStatusPageCheck(HtmlMarkerCheck):
    """Represent `BoxStatusPageCheck`."""

    check_key = "box_status_page"
    endpoint_key = "https://status.box.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("status",)


class BoxHomepageCheck(HtmlMarkerCheck):
    """Represent `BoxHomepageCheck`."""

    check_key = "box_homepage"
    endpoint_key = "https://www.box.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("box",)


class BoxDocsCheck(HtmlMarkerCheck):
    """Represent `BoxDocsCheck`."""

    check_key = "box_docs"
    endpoint_key = "https://developer.box.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.1
    expected_markers = ("box",)


class BoxServiceChecker(BaseServiceChecker):
    """Represent `BoxServiceChecker`."""

    service_key = "box"
    logo_url = "https://img.logo.dev/box.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.box.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            BoxStatusApiCheck(),
            BoxSummaryApiCheck(),
            BoxStatusPageCheck(),
            BoxHomepageCheck(),
            BoxDocsCheck(),
        ]

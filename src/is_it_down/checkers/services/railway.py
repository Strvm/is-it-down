"""Provide functionality for `is_it_down.checkers.services.railway`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class RailwayStatusApiCheck(HtmlMarkerCheck):
    """Represent `RailwayStatusApiCheck`."""

    check_key = "railway_status_api"
    endpoint_key = "https://backboard.railway.app/health"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    required_content_type_fragment = "text/plain"
    expected_markers = ("ok",)


class RailwaySummaryApiCheck(HtmlMarkerCheck):
    """Represent `RailwaySummaryApiCheck`."""

    check_key = "railway_summary_api"
    endpoint_key = "https://railway.com/changelog"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("railway",)


class RailwayStatusPageCheck(HtmlMarkerCheck):
    """Represent `RailwayStatusPageCheck`."""

    check_key = "railway_status_page"
    endpoint_key = "https://status.railway.app/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("status",)


class RailwayHomepageCheck(HtmlMarkerCheck):
    """Represent `RailwayHomepageCheck`."""

    check_key = "railway_homepage"
    endpoint_key = "https://railway.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("railway",)


class RailwayDocsCheck(HtmlMarkerCheck):
    """Represent `RailwayDocsCheck`."""

    check_key = "railway_docs"
    endpoint_key = "https://docs.railway.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.1
    expected_markers = ("railway",)


class RailwayServiceChecker(BaseServiceChecker):
    """Represent `RailwayServiceChecker`."""

    service_key = "railway"
    logo_url = "https://img.logo.dev/railway.app?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.railway.app/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            RailwayStatusApiCheck(),
            RailwaySummaryApiCheck(),
            RailwayStatusPageCheck(),
            RailwayHomepageCheck(),
            RailwayDocsCheck(),
        ]

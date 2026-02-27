"""Provide functionality for `is_it_down.checkers.services.optimizely`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck, StatuspageStatusCheck, StatuspageSummaryCheck


class OptimizelyStatusApiCheck(StatuspageStatusCheck):
    """Represent `OptimizelyStatusApiCheck`."""

    check_key = "optimizely_status_api"
    endpoint_key = "https://status.optimizely.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class OptimizelySummaryApiCheck(StatuspageSummaryCheck):
    """Represent `OptimizelySummaryApiCheck`."""

    check_key = "optimizely_summary_api"
    endpoint_key = "https://status.optimizely.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class OptimizelyStatusPageCheck(HtmlMarkerCheck):
    """Represent `OptimizelyStatusPageCheck`."""

    check_key = "optimizely_status_page"
    endpoint_key = "https://status.optimizely.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("optimizely",)


class OptimizelyHomepageCheck(HtmlMarkerCheck):
    """Represent `OptimizelyHomepageCheck`."""

    check_key = "optimizely_homepage"
    endpoint_key = "https://www.optimizely.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("optimizely",)


class OptimizelyDevelopersCheck(HtmlMarkerCheck):
    """Represent `OptimizelyDevelopersCheck`."""

    check_key = "optimizely_developers"
    endpoint_key = "https://docs.developers.optimizely.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("optimizely",)


class OptimizelyServiceChecker(BaseServiceChecker):
    """Represent `OptimizelyServiceChecker`."""

    service_key = "optimizely"
    logo_url = "https://img.logo.dev/optimizely.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.optimizely.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            OptimizelyStatusApiCheck(),
            OptimizelySummaryApiCheck(),
            OptimizelyStatusPageCheck(),
            OptimizelyHomepageCheck(),
            OptimizelyDevelopersCheck(),
        ]

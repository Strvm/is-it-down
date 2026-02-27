"""Provide functionality for `is_it_down.checkers.services.planetscale`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck, StatuspageStatusCheck


class PlanetScaleStatusApiCheck(StatuspageStatusCheck):
    """Represent `PlanetScaleStatusApiCheck`."""

    check_key = "planetscale_status_api"
    endpoint_key = "https://www.planetscalestatus.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class PlanetScaleSummaryApiCheck(StatuspageStatusCheck):
    """Represent `PlanetScaleSummaryApiCheck`."""

    check_key = "planetscale_summary_api"
    endpoint_key = "https://www.planetscalestatus.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class PlanetScaleStatusPageCheck(HtmlMarkerCheck):
    """Represent `PlanetScaleStatusPageCheck`."""

    check_key = "planetscale_status_page"
    endpoint_key = "https://www.planetscalestatus.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("status",)


class PlanetScaleHomepageCheck(HtmlMarkerCheck):
    """Represent `PlanetScaleHomepageCheck`."""

    check_key = "planetscale_homepage"
    endpoint_key = "https://planetscale.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("planetscale",)


class PlanetScaleDocsCheck(HtmlMarkerCheck):
    """Represent `PlanetScaleDocsCheck`."""

    check_key = "planetscale_docs"
    endpoint_key = "https://planetscale.com/docs"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.1
    expected_markers = ("planetscale",)


class PlanetScaleServiceChecker(BaseServiceChecker):
    """Represent `PlanetScaleServiceChecker`."""

    service_key = "planetscale"
    logo_url = "https://img.logo.dev/planetscale.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://www.planetscalestatus.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            PlanetScaleStatusApiCheck(),
            PlanetScaleSummaryApiCheck(),
            PlanetScaleStatusPageCheck(),
            PlanetScaleHomepageCheck(),
            PlanetScaleDocsCheck(),
        ]

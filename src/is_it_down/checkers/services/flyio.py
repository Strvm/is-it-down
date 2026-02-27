"""Provide functionality for `is_it_down.checkers.services.flyio`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck, StatuspageStatusCheck, StatuspageSummaryCheck


class FlyIoStatusApiCheck(StatuspageStatusCheck):
    """Represent `FlyIoStatusApiCheck`."""

    check_key = "flyio_status_api"
    endpoint_key = "https://status.flyio.net/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class FlyIoSummaryApiCheck(StatuspageSummaryCheck):
    """Represent `FlyIoSummaryApiCheck`."""

    check_key = "flyio_summary_api"
    endpoint_key = "https://status.flyio.net/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class FlyIoStatusPageCheck(HtmlMarkerCheck):
    """Represent `FlyIoStatusPageCheck`."""

    check_key = "flyio_status_page"
    endpoint_key = "https://status.flyio.net/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("status",)


class FlyIoHomepageCheck(HtmlMarkerCheck):
    """Represent `FlyIoHomepageCheck`."""

    check_key = "flyio_homepage"
    endpoint_key = "https://fly.io/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("fly.io",)


class FlyIoDocsCheck(HtmlMarkerCheck):
    """Represent `FlyIoDocsCheck`."""

    check_key = "flyio_docs"
    endpoint_key = "https://fly.io/docs/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.1
    expected_markers = ("fly.io",)


class FlyIoServiceChecker(BaseServiceChecker):
    """Represent `FlyIoServiceChecker`."""

    service_key = "flyio"
    logo_url = "https://img.logo.dev/fly.io?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.flyio.net/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            FlyIoStatusApiCheck(),
            FlyIoSummaryApiCheck(),
            FlyIoStatusPageCheck(),
            FlyIoHomepageCheck(),
            FlyIoDocsCheck(),
        ]

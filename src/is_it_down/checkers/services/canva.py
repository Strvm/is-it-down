"""Provide functionality for `is_it_down.checkers.services.canva`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class CanvaStatusPageCheck(HtmlMarkerCheck):
    """Represent `CanvaStatusPageCheck`."""

    check_key = "canva_status_page"
    endpoint_key = "https://status.canva.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("canva",)


class CanvaHomepageCheck(HtmlMarkerCheck):
    """Represent `CanvaHomepageCheck`."""

    check_key = "canva_homepage"
    endpoint_key = "https://www.canva.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("canva",)


class CanvaDevelopersCheck(HtmlMarkerCheck):
    """Represent `CanvaDevelopersCheck`."""

    check_key = "canva_developers"
    endpoint_key = "https://www.canva.dev/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("canva",)


class CanvaHelpCheck(HtmlMarkerCheck):
    """Represent `CanvaHelpCheck`."""

    check_key = "canva_help"
    endpoint_key = "https://www.canva.com/help/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("canva",)


class CanvaNewsroomCheck(HtmlMarkerCheck):
    """Represent `CanvaNewsroomCheck`."""

    check_key = "canva_newsroom"
    endpoint_key = "https://www.canva.com/newsroom/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("canva",)


class CanvaServiceChecker(BaseServiceChecker):
    """Represent `CanvaServiceChecker`."""

    service_key = "canva"
    logo_url = "https://img.logo.dev/canva.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.canva.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            CanvaStatusPageCheck(),
            CanvaHomepageCheck(),
            CanvaDevelopersCheck(),
            CanvaHelpCheck(),
            CanvaNewsroomCheck(),
        ]

"""Provide functionality for `is_it_down.checkers.services.front`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class FrontHomepageCheck(HtmlMarkerCheck):
    """Represent `FrontHomepageCheck`."""

    check_key = "front_home_page"
    endpoint_key = "https://front.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("front",)


class FrontHelpCenterCheck(HtmlMarkerCheck):
    """Represent `FrontHelpCenterCheck`."""

    check_key = "front_helpcenter"
    endpoint_key = "https://help.front.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("front",)


class FrontLoginCheck(HtmlMarkerCheck):
    """Represent `FrontLoginCheck`."""

    check_key = "front_login"
    endpoint_key = "https://app.frontapp.com/login"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("front",)


class FrontDevelopersCheck(HtmlMarkerCheck):
    """Represent `FrontDevelopersCheck`."""

    check_key = "front_developers"
    endpoint_key = "https://dev.frontapp.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("front",)


class FrontStatusPageCheck(HtmlMarkerCheck):
    """Represent `FrontStatusPageCheck`."""

    check_key = "front_status_page"
    endpoint_key = "https://status.front.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("status",)


class FrontServiceChecker(BaseServiceChecker):
    """Represent `FrontServiceChecker`."""

    service_key = "front"
    logo_url = "https://img.logo.dev/front.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.front.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            FrontHomepageCheck(),
            FrontHelpCenterCheck(),
            FrontLoginCheck(),
            FrontDevelopersCheck(),
            FrontStatusPageCheck(),
        ]

"""Provide functionality for `is_it_down.checkers.services.monday`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class MondayStatusPageCheck(HtmlMarkerCheck):
    """Represent `MondayStatusPageCheck`."""

    check_key = "monday_status_page"
    endpoint_key = "https://status.monday.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("monday",)


class MondayHomepageCheck(HtmlMarkerCheck):
    """Represent `MondayHomepageCheck`."""

    check_key = "monday_homepage"
    endpoint_key = "https://monday.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("monday",)


class MondayDevelopersCheck(HtmlMarkerCheck):
    """Represent `MondayDevelopersCheck`."""

    check_key = "monday_developers"
    endpoint_key = "https://developer.monday.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("monday",)


class MondaySupportCheck(HtmlMarkerCheck):
    """Represent `MondaySupportCheck`."""

    check_key = "monday_support"
    endpoint_key = "https://support.monday.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("monday",)


class MondayCommunityCheck(HtmlMarkerCheck):
    """Represent `MondayCommunityCheck`."""

    check_key = "monday_community"
    endpoint_key = "https://community.monday.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("monday",)


class MondayServiceChecker(BaseServiceChecker):
    """Represent `MondayServiceChecker`."""

    service_key = "monday"
    logo_url = "https://img.logo.dev/monday.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.monday.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            MondayStatusPageCheck(),
            MondayHomepageCheck(),
            MondayDevelopersCheck(),
            MondaySupportCheck(),
            MondayCommunityCheck(),
        ]

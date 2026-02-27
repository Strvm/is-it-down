"""Provide functionality for `is_it_down.checkers.services.crisp`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class CrispHomepageCheck(HtmlMarkerCheck):
    """Represent `CrispHomepageCheck`."""

    check_key = "crisp_home_page"
    endpoint_key = "https://crisp.chat/en/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("crisp",)


class CrispHelpCenterCheck(HtmlMarkerCheck):
    """Represent `CrispHelpCenterCheck`."""

    check_key = "crisp_helpcenter"
    endpoint_key = "https://help.crisp.chat/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("crisp",)


class CrispAppCheck(HtmlMarkerCheck):
    """Represent `CrispAppCheck`."""

    check_key = "crisp_app"
    endpoint_key = "https://app.crisp.chat/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("crisp",)


class CrispDevelopersCheck(HtmlMarkerCheck):
    """Represent `CrispDevelopersCheck`."""

    check_key = "crisp_developers"
    endpoint_key = "https://docs.crisp.chat/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("crisp",)


class CrispStatusPageCheck(HtmlMarkerCheck):
    """Represent `CrispStatusPageCheck`."""

    check_key = "crisp_status_page"
    endpoint_key = "https://status.crisp.chat/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("status",)


class CrispServiceChecker(BaseServiceChecker):
    """Represent `CrispServiceChecker`."""

    service_key = "crisp"
    logo_url = "https://img.logo.dev/crisp.chat?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.crisp.chat/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            CrispHomepageCheck(),
            CrispHelpCenterCheck(),
            CrispAppCheck(),
            CrispDevelopersCheck(),
            CrispStatusPageCheck(),
        ]

"""Provide functionality for `is_it_down.checkers.services.microsoft365`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class Microsoft365HomepageCheck(HtmlMarkerCheck):
    """Represent `Microsoft365HomepageCheck`."""

    check_key = "microsoft365_home_page"
    endpoint_key = "https://www.microsoft.com/microsoft-365"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("microsoft",)


class Microsoft365PortalCheck(HtmlMarkerCheck):
    """Represent `Microsoft365PortalCheck`."""

    check_key = "microsoft365_portal"
    endpoint_key = "https://portal.office.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("office",)


class Microsoft365OutlookWebCheck(HtmlMarkerCheck):
    """Represent `Microsoft365OutlookWebCheck`."""

    check_key = "microsoft365_outlookweb"
    endpoint_key = "https://outlook.office.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("outlook",)


class Microsoft365SupportCheck(HtmlMarkerCheck):
    """Represent `Microsoft365SupportCheck`."""

    check_key = "microsoft365_support"
    endpoint_key = "https://support.microsoft.com/office"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("office",)


class Microsoft365StatusPageCheck(HtmlMarkerCheck):
    """Represent `Microsoft365StatusPageCheck`."""

    check_key = "microsoft365_status_page"
    endpoint_key = "https://status.office.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("status",)


class Microsoft365ServiceChecker(BaseServiceChecker):
    """Represent `Microsoft365ServiceChecker`."""

    service_key = "microsoft365"
    logo_url = "https://img.logo.dev/microsoft.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.office.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            Microsoft365HomepageCheck(),
            Microsoft365PortalCheck(),
            Microsoft365OutlookWebCheck(),
            Microsoft365SupportCheck(),
            Microsoft365StatusPageCheck(),
        ]

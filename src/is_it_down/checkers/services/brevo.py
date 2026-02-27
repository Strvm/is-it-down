"""Provide functionality for `is_it_down.checkers.services.brevo`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class BrevoHomepageCheck(HtmlMarkerCheck):
    """Represent `BrevoHomepageCheck`."""

    check_key = "brevo_home_page"
    endpoint_key = "https://www.brevo.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("brevo",)


class BrevoHelpCenterCheck(HtmlMarkerCheck):
    """Represent `BrevoHelpCenterCheck`."""

    check_key = "brevo_helpcenter"
    endpoint_key = "https://help.brevo.com/hc/en-us"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("brevo",)


class BrevoAppLoginCheck(HtmlMarkerCheck):
    """Represent `BrevoAppLoginCheck`."""

    check_key = "brevo_applogin"
    endpoint_key = "https://app.brevo.com/login"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("brevo",)


class BrevoDevelopersCheck(HtmlMarkerCheck):
    """Represent `BrevoDevelopersCheck`."""

    check_key = "brevo_developers"
    endpoint_key = "https://developers.brevo.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("brevo",)


class BrevoStatusPageCheck(HtmlMarkerCheck):
    """Represent `BrevoStatusPageCheck`."""

    check_key = "brevo_status_page"
    endpoint_key = "https://status.brevo.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("status",)


class BrevoServiceChecker(BaseServiceChecker):
    """Represent `BrevoServiceChecker`."""

    service_key = "brevo"
    logo_url = "https://img.logo.dev/brevo.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.brevo.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            BrevoHomepageCheck(),
            BrevoHelpCenterCheck(),
            BrevoAppLoginCheck(),
            BrevoDevelopersCheck(),
            BrevoStatusPageCheck(),
        ]

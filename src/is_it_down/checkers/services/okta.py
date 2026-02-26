"""Provide functionality for `is_it_down.checkers.services.okta`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class OktaStatusPageCheck(HtmlMarkerCheck):
    """Represent `OktaStatusPageCheck`."""

    check_key = "okta_status_page"
    endpoint_key = "https://status.okta.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("okta",)


class OktaHomepageCheck(HtmlMarkerCheck):
    """Represent `OktaHomepageCheck`."""

    check_key = "okta_homepage"
    endpoint_key = "https://okta.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("okta",)


class OktaDevelopersCheck(HtmlMarkerCheck):
    """Represent `OktaDevelopersCheck`."""

    check_key = "okta_developers"
    endpoint_key = "https://developer.okta.com/docs/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("okta",)


class OktaSupportCheck(HtmlMarkerCheck):
    """Represent `OktaSupportCheck`."""

    check_key = "okta_support"
    endpoint_key = "https://support.okta.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("okta",)


class OktaTrustCheck(HtmlMarkerCheck):
    """Represent `OktaTrustCheck`."""

    check_key = "okta_trust"
    endpoint_key = "https://trust.okta.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("okta",)


class OktaServiceChecker(BaseServiceChecker):
    """Represent `OktaServiceChecker`."""

    service_key = "okta"
    logo_url = "https://img.logo.dev/okta.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.okta.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            OktaStatusPageCheck(),
            OktaHomepageCheck(),
            OktaDevelopersCheck(),
            OktaSupportCheck(),
            OktaTrustCheck(),
        ]

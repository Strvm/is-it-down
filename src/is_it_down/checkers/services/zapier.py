"""Provide functionality for `is_it_down.checkers.services.zapier`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class ZapierStatusPageCheck(HtmlMarkerCheck):
    """Represent `ZapierStatusPageCheck`."""

    check_key = "zapier_status_page"
    endpoint_key = "https://status.zapier.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("zapier",)


class ZapierHomepageCheck(HtmlMarkerCheck):
    """Represent `ZapierHomepageCheck`."""

    check_key = "zapier_homepage"
    endpoint_key = "https://zapier.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("zapier",)


class ZapierPlatformDocsCheck(HtmlMarkerCheck):
    """Represent `ZapierPlatformDocsCheck`."""

    check_key = "zapier_platform_docs"
    endpoint_key = "https://docs.zapier.com/platform/home"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("zapier",)


class ZapierHelpCheck(HtmlMarkerCheck):
    """Represent `ZapierHelpCheck`."""

    check_key = "zapier_help"
    endpoint_key = "https://help.zapier.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("zapier",)


class ZapierCommunityCheck(HtmlMarkerCheck):
    """Represent `ZapierCommunityCheck`."""

    check_key = "zapier_community"
    endpoint_key = "https://community.zapier.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("zapier",)


class ZapierServiceChecker(BaseServiceChecker):
    """Represent `ZapierServiceChecker`."""

    service_key = "zapier"
    logo_url = "https://img.logo.dev/zapier.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.zapier.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            ZapierStatusPageCheck(),
            ZapierHomepageCheck(),
            ZapierPlatformDocsCheck(),
            ZapierHelpCheck(),
            ZapierCommunityCheck(),
        ]

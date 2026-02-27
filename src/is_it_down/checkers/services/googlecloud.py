"""Provide functionality for `is_it_down.checkers.services.googlecloud`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class GoogleCloudStatusPageCheck(HtmlMarkerCheck):
    """Represent `GoogleCloudStatusPageCheck`."""

    check_key = "googlecloud_status_page"
    endpoint_key = "https://status.cloud.google.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("google",)


class GoogleCloudHomepageCheck(HtmlMarkerCheck):
    """Represent `GoogleCloudHomepageCheck`."""

    check_key = "googlecloud_homepage"
    endpoint_key = "https://cloud.google.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("google cloud",)


class GoogleCloudDocsCheck(HtmlMarkerCheck):
    """Represent `GoogleCloudDocsCheck`."""

    check_key = "googlecloud_docs"
    endpoint_key = "https://cloud.google.com/docs"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("google cloud",)


class GoogleCloudConsoleCheck(HtmlMarkerCheck):
    """Represent `GoogleCloudConsoleCheck`."""

    check_key = "googlecloud_console"
    endpoint_key = "https://console.cloud.google.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("google",)


class GoogleCloudSupportCheck(HtmlMarkerCheck):
    """Represent `GoogleCloudSupportCheck`."""

    check_key = "googlecloud_support"
    endpoint_key = "https://cloud.google.com/support"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("google",)


class GoogleCloudServiceChecker(BaseServiceChecker):
    """Represent `GoogleCloudServiceChecker`."""

    service_key = "googlecloud"
    logo_url = "https://img.logo.dev/cloud.google.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.cloud.google.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            GoogleCloudStatusPageCheck(),
            GoogleCloudHomepageCheck(),
            GoogleCloudDocsCheck(),
            GoogleCloudConsoleCheck(),
            GoogleCloudSupportCheck(),
        ]

"""Provide functionality for `is_it_down.checkers.services.azure`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class AzureStatusPageCheck(HtmlMarkerCheck):
    """Represent `AzureStatusPageCheck`."""

    check_key = "azure_status_page"
    endpoint_key = "https://azure.status.microsoft/en-us/status"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("azure",)


class AzureHomepageCheck(HtmlMarkerCheck):
    """Represent `AzureHomepageCheck`."""

    check_key = "azure_homepage"
    endpoint_key = "https://azure.microsoft.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("azure",)


class AzureDocsCheck(HtmlMarkerCheck):
    """Represent `AzureDocsCheck`."""

    check_key = "azure_docs"
    endpoint_key = "https://learn.microsoft.com/en-us/azure/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("azure",)


class AzurePortalCheck(HtmlMarkerCheck):
    """Represent `AzurePortalCheck`."""

    check_key = "azure_portal"
    endpoint_key = "https://portal.azure.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("azure",)


class AzureSupportCheck(HtmlMarkerCheck):
    """Represent `AzureSupportCheck`."""

    check_key = "azure_support"
    endpoint_key = "https://azure.microsoft.com/en-us/support/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("azure",)


class AzureServiceChecker(BaseServiceChecker):
    """Represent `AzureServiceChecker`."""

    service_key = "azure"
    logo_url = "https://img.logo.dev/azure.microsoft.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://azure.status.microsoft/en-us/status"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            AzureStatusPageCheck(),
            AzureHomepageCheck(),
            AzureDocsCheck(),
            AzurePortalCheck(),
            AzureSupportCheck(),
        ]

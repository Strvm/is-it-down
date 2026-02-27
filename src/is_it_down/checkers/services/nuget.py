"""Provide functionality for `is_it_down.checkers.services.nuget`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class NuGetHomepageCheck(HtmlMarkerCheck):
    """Represent `NuGetHomepageCheck`."""

    check_key = "nuget_home_page"
    endpoint_key = "https://www.nuget.org/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("nuget",)


class NuGetPackagePageCheck(HtmlMarkerCheck):
    """Represent `NuGetPackagePageCheck`."""

    check_key = "nuget_package_page"
    endpoint_key = "https://www.nuget.org/packages/Newtonsoft.Json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("newtonsoft",)


class NuGetDocsCheck(HtmlMarkerCheck):
    """Represent `NuGetDocsCheck`."""

    check_key = "nuget_docs"
    endpoint_key = "https://learn.microsoft.com/nuget/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("nuget",)


class NuGetStatusPageCheck(HtmlMarkerCheck):
    """Represent `NuGetStatusPageCheck`."""

    check_key = "nuget_status_page"
    endpoint_key = "https://status.nuget.org/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("status",)


class NuGetApiV3IndexCheck(HtmlMarkerCheck):
    """Represent `NuGetApiV3IndexCheck`."""

    check_key = "nuget_apiv3index"
    endpoint_key = "https://api.nuget.org/v3/index.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    required_content_type_fragment = None
    weight = 0.15
    expected_markers = ("version",)


class NuGetServiceChecker(BaseServiceChecker):
    """Represent `NuGetServiceChecker`."""

    service_key = "nuget"
    logo_url = "https://img.logo.dev/nuget.org?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.nuget.org/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            NuGetHomepageCheck(),
            NuGetPackagePageCheck(),
            NuGetDocsCheck(),
            NuGetStatusPageCheck(),
            NuGetApiV3IndexCheck(),
        ]

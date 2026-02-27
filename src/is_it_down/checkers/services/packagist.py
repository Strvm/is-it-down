"""Provide functionality for `is_it_down.checkers.services.packagist`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class PackagistHomepageCheck(HtmlMarkerCheck):
    """Represent `PackagistHomepageCheck`."""

    check_key = "packagist_home_page"
    endpoint_key = "https://packagist.org/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("packagist",)


class PackagistPackagePageCheck(HtmlMarkerCheck):
    """Represent `PackagistPackagePageCheck`."""

    check_key = "packagist_package_page"
    endpoint_key = "https://packagist.org/packages/laravel/framework"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("laravel",)


class PackagistDocsCheck(HtmlMarkerCheck):
    """Represent `PackagistDocsCheck`."""

    check_key = "packagist_docs"
    endpoint_key = "https://packagist.org/about"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("packagist",)


class PackagistStatusPageCheck(HtmlMarkerCheck):
    """Represent `PackagistStatusPageCheck`."""

    check_key = "packagist_status_page"
    endpoint_key = "https://status.packagist.org/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("status",)


class PackagistApiSearchCheck(HtmlMarkerCheck):
    """Represent `PackagistApiSearchCheck`."""

    check_key = "packagist_apisearch"
    endpoint_key = "https://packagist.org/search.json?q=laravel"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("results",)


class PackagistServiceChecker(BaseServiceChecker):
    """Represent `PackagistServiceChecker`."""

    service_key = "packagist"
    logo_url = "https://img.logo.dev/packagist.org?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.packagist.org/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            PackagistHomepageCheck(),
            PackagistPackagePageCheck(),
            PackagistDocsCheck(),
            PackagistStatusPageCheck(),
            PackagistApiSearchCheck(),
        ]

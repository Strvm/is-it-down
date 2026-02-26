"""Provide functionality for `is_it_down.checkers.services.cloudinary`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class CloudinaryStatusPageCheck(HtmlMarkerCheck):
    """Represent `CloudinaryStatusPageCheck`."""

    check_key = "cloudinary_status_page"
    endpoint_key = "https://status.cloudinary.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("cloudinary",)


class CloudinaryHomepageCheck(HtmlMarkerCheck):
    """Represent `CloudinaryHomepageCheck`."""

    check_key = "cloudinary_homepage"
    endpoint_key = "https://cloudinary.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("cloudinary",)


class CloudinaryDocsCheck(HtmlMarkerCheck):
    """Represent `CloudinaryDocsCheck`."""

    check_key = "cloudinary_docs"
    endpoint_key = "https://cloudinary.com/documentation"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("cloudinary",)


class CloudinarySupportCheck(HtmlMarkerCheck):
    """Represent `CloudinarySupportCheck`."""

    check_key = "cloudinary_support"
    endpoint_key = "https://support.cloudinary.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("cloudinary",)


class CloudinaryConsoleCheck(HtmlMarkerCheck):
    """Represent `CloudinaryConsoleCheck`."""

    check_key = "cloudinary_console"
    endpoint_key = "https://console.cloudinary.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("cloudinary",)


class CloudinaryServiceChecker(BaseServiceChecker):
    """Represent `CloudinaryServiceChecker`."""

    service_key = "cloudinary"
    logo_url = "https://img.logo.dev/cloudinary.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.cloudinary.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            CloudinaryStatusPageCheck(),
            CloudinaryHomepageCheck(),
            CloudinaryDocsCheck(),
            CloudinarySupportCheck(),
            CloudinaryConsoleCheck(),
        ]

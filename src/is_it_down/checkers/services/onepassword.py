"""Provide functionality for `is_it_down.checkers.services.onepassword`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class OnePasswordStatusPageCheck(HtmlMarkerCheck):
    """Represent `OnePasswordStatusPageCheck`."""

    check_key = "onepassword_status_page"
    endpoint_key = "https://status.1password.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("1password",)


class OnePasswordHomepageCheck(HtmlMarkerCheck):
    """Represent `OnePasswordHomepageCheck`."""

    check_key = "onepassword_homepage"
    endpoint_key = "https://1password.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("1password",)


class OnePasswordDocsCheck(HtmlMarkerCheck):
    """Represent `OnePasswordDocsCheck`."""

    check_key = "onepassword_docs"
    endpoint_key = "https://developer.1password.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("1password",)


class OnePasswordSupportCheck(HtmlMarkerCheck):
    """Represent `OnePasswordSupportCheck`."""

    check_key = "onepassword_support"
    endpoint_key = "https://support.1password.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("1password",)


class OnePasswordBlogCheck(HtmlMarkerCheck):
    """Represent `OnePasswordBlogCheck`."""

    check_key = "onepassword_blog"
    endpoint_key = "https://blog.1password.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("1password",)


class OnePasswordServiceChecker(BaseServiceChecker):
    """Represent `OnePasswordServiceChecker`."""

    service_key = "onepassword"
    logo_url = "https://img.logo.dev/1password.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.1password.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            OnePasswordStatusPageCheck(),
            OnePasswordHomepageCheck(),
            OnePasswordDocsCheck(),
            OnePasswordSupportCheck(),
            OnePasswordBlogCheck(),
        ]

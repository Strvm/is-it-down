"""Provide functionality for `is_it_down.checkers.services.loom`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class LoomStatusPageCheck(HtmlMarkerCheck):
    """Represent `LoomStatusPageCheck`."""

    check_key = "loom_status_page"
    endpoint_key = "https://status.loom.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("loom",)


class LoomHomepageCheck(HtmlMarkerCheck):
    """Represent `LoomHomepageCheck`."""

    check_key = "loom_homepage"
    endpoint_key = "https://www.loom.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("loom",)


class LoomDocsCheck(HtmlMarkerCheck):
    """Represent `LoomDocsCheck`."""

    check_key = "loom_docs"
    endpoint_key = "https://www.loom.com/help"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("loom",)


class LoomSupportCheck(HtmlMarkerCheck):
    """Represent `LoomSupportCheck`."""

    check_key = "loom_support"
    endpoint_key = "https://support.loom.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("loom",)


class LoomBlogCheck(HtmlMarkerCheck):
    """Represent `LoomBlogCheck`."""

    check_key = "loom_blog"
    endpoint_key = "https://www.loom.com/blog"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("loom",)


class LoomServiceChecker(BaseServiceChecker):
    """Represent `LoomServiceChecker`."""

    service_key = "loom"
    logo_url = "https://img.logo.dev/loom.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.loom.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            LoomStatusPageCheck(),
            LoomHomepageCheck(),
            LoomDocsCheck(),
            LoomSupportCheck(),
            LoomBlogCheck(),
        ]

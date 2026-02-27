"""Provide functionality for `is_it_down.checkers.services.jetbrains`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class JetBrainsStatusPageCheck(HtmlMarkerCheck):
    """Represent `JetBrainsStatusPageCheck`."""

    check_key = "jetbrains_status_page"
    endpoint_key = "https://status.jetbrains.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("status",)


class JetBrainsHomepageCheck(HtmlMarkerCheck):
    """Represent `JetBrainsHomepageCheck`."""

    check_key = "jetbrains_homepage"
    endpoint_key = "https://www.jetbrains.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("jetbrains",)


class JetBrainsDocsCheck(HtmlMarkerCheck):
    """Represent `JetBrainsDocsCheck`."""

    check_key = "jetbrains_docs"
    endpoint_key = "https://www.jetbrains.com/help/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("jetbrains",)


class JetBrainsSupportCheck(HtmlMarkerCheck):
    """Represent `JetBrainsSupportCheck`."""

    check_key = "jetbrains_support"
    endpoint_key = "https://youtrack.jetbrains.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("jetbrains",)


class JetBrainsBlogCheck(HtmlMarkerCheck):
    """Represent `JetBrainsBlogCheck`."""

    check_key = "jetbrains_blog"
    endpoint_key = "https://blog.jetbrains.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("jetbrains",)


class JetBrainsServiceChecker(BaseServiceChecker):
    """Represent `JetBrainsServiceChecker`."""

    service_key = "jetbrains"
    logo_url = "https://img.logo.dev/jetbrains.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.jetbrains.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            JetBrainsStatusPageCheck(),
            JetBrainsHomepageCheck(),
            JetBrainsDocsCheck(),
            JetBrainsSupportCheck(),
            JetBrainsBlogCheck(),
        ]

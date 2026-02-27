"""Provide functionality for `is_it_down.checkers.services.ghost`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class GhostHomepageCheck(HtmlMarkerCheck):
    """Represent `GhostHomepageCheck`."""

    check_key = "ghost_home_page"
    endpoint_key = "https://ghost.org/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("ghost",)


class GhostDocsCheck(HtmlMarkerCheck):
    """Represent `GhostDocsCheck`."""

    check_key = "ghost_docs"
    endpoint_key = "https://ghost.org/docs/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("ghost",)


class GhostDevelopersCheck(HtmlMarkerCheck):
    """Represent `GhostDevelopersCheck`."""

    check_key = "ghost_developers"
    endpoint_key = "https://ghost.org/docs/api/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("ghost",)


class GhostStatusPageCheck(HtmlMarkerCheck):
    """Represent `GhostStatusPageCheck`."""

    check_key = "ghost_status_page"
    endpoint_key = "https://ghost.statuspage.io/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("status",)


class GhostBlogCheck(HtmlMarkerCheck):
    """Represent `GhostBlogCheck`."""

    check_key = "ghost_blog"
    endpoint_key = "https://ghost.org/changelog/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("ghost",)


class GhostServiceChecker(BaseServiceChecker):
    """Represent `GhostServiceChecker`."""

    service_key = "ghost"
    logo_url = "https://img.logo.dev/ghost.org?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://ghost.statuspage.io/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            GhostHomepageCheck(),
            GhostDocsCheck(),
            GhostDevelopersCheck(),
            GhostStatusPageCheck(),
            GhostBlogCheck(),
        ]

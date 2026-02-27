"""Provide functionality for `is_it_down.checkers.services.vimeo`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class VimeoHomepageCheck(HtmlMarkerCheck):
    """Represent `VimeoHomepageCheck`."""

    check_key = "vimeo_home_page"
    endpoint_key = "https://vimeo.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("vimeo",)


class VimeoHelpCheck(HtmlMarkerCheck):
    """Represent `VimeoHelpCheck`."""

    check_key = "vimeo_help"
    endpoint_key = "https://help.vimeo.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("vimeo",)


class VimeoDeveloperCheck(HtmlMarkerCheck):
    """Represent `VimeoDeveloperCheck`."""

    check_key = "vimeo_developer"
    endpoint_key = "https://developer.vimeo.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("vimeo",)


class VimeoStatusPageCheck(HtmlMarkerCheck):
    """Represent `VimeoStatusPageCheck`."""

    check_key = "vimeo_status_page"
    endpoint_key = "https://www.vimeostatus.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("status",)


class VimeoWatchCheck(HtmlMarkerCheck):
    """Represent `VimeoWatchCheck`."""

    check_key = "vimeo_watch"
    endpoint_key = "https://vimeo.com/channels/staffpicks"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("vimeo",)


class VimeoServiceChecker(BaseServiceChecker):
    """Represent `VimeoServiceChecker`."""

    service_key = "vimeo"
    logo_url = "https://img.logo.dev/vimeo.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://www.vimeostatus.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            VimeoHomepageCheck(),
            VimeoHelpCheck(),
            VimeoDeveloperCheck(),
            VimeoStatusPageCheck(),
            VimeoWatchCheck(),
        ]

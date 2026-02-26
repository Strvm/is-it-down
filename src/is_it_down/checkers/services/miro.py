"""Provide functionality for `is_it_down.checkers.services.miro`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class MiroStatusPageCheck(HtmlMarkerCheck):
    """Represent `MiroStatusPageCheck`."""

    check_key = "miro_status_page"
    endpoint_key = "https://status.miro.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("miro",)


class MiroHomepageCheck(HtmlMarkerCheck):
    """Represent `MiroHomepageCheck`."""

    check_key = "miro_homepage"
    endpoint_key = "https://miro.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("miro",)


class MiroDevelopersCheck(HtmlMarkerCheck):
    """Represent `MiroDevelopersCheck`."""

    check_key = "miro_developers"
    endpoint_key = "https://developers.miro.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("miro",)


class MiroHelpCheck(HtmlMarkerCheck):
    """Represent `MiroHelpCheck`."""

    check_key = "miro_help"
    endpoint_key = "https://help.miro.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("miro",)


class MiroCommunityCheck(HtmlMarkerCheck):
    """Represent `MiroCommunityCheck`."""

    check_key = "miro_community"
    endpoint_key = "https://community.miro.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("miro",)


class MiroServiceChecker(BaseServiceChecker):
    """Represent `MiroServiceChecker`."""

    service_key = "miro"
    logo_url = "https://img.logo.dev/miro.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.miro.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            MiroStatusPageCheck(),
            MiroHomepageCheck(),
            MiroDevelopersCheck(),
            MiroHelpCheck(),
            MiroCommunityCheck(),
        ]

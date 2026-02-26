"""Provide functionality for `is_it_down.checkers.services.klaviyo`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class KlaviyoStatusPageCheck(HtmlMarkerCheck):
    """Represent `KlaviyoStatusPageCheck`."""

    check_key = "klaviyo_status_page"
    endpoint_key = "https://status.klaviyo.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("klaviyo",)


class KlaviyoHomepageCheck(HtmlMarkerCheck):
    """Represent `KlaviyoHomepageCheck`."""

    check_key = "klaviyo_homepage"
    endpoint_key = "https://www.klaviyo.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("klaviyo",)


class KlaviyoDevelopersCheck(HtmlMarkerCheck):
    """Represent `KlaviyoDevelopersCheck`."""

    check_key = "klaviyo_developers"
    endpoint_key = "https://developers.klaviyo.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("klaviyo",)


class KlaviyoHelpCheck(HtmlMarkerCheck):
    """Represent `KlaviyoHelpCheck`."""

    check_key = "klaviyo_help"
    endpoint_key = "https://help.klaviyo.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("klaviyo",)


class KlaviyoCommunityCheck(HtmlMarkerCheck):
    """Represent `KlaviyoCommunityCheck`."""

    check_key = "klaviyo_community"
    endpoint_key = "https://community.klaviyo.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("klaviyo",)


class KlaviyoServiceChecker(BaseServiceChecker):
    """Represent `KlaviyoServiceChecker`."""

    service_key = "klaviyo"
    logo_url = "https://img.logo.dev/klaviyo.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.klaviyo.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            KlaviyoStatusPageCheck(),
            KlaviyoHomepageCheck(),
            KlaviyoDevelopersCheck(),
            KlaviyoHelpCheck(),
            KlaviyoCommunityCheck(),
        ]

"""Provide functionality for `is_it_down.checkers.services.apple`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class AppleHomepageCheck(HtmlMarkerCheck):
    """Represent `AppleHomepageCheck`."""

    check_key = "apple_home_page"
    endpoint_key = "https://www.apple.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("apple",)


class AppleSystemStatusCheck(HtmlMarkerCheck):
    """Represent `AppleSystemStatusCheck`."""

    check_key = "apple_systemstatus"
    endpoint_key = "https://www.apple.com/support/systemstatus/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("system status",)


class AppleDeveloperCheck(HtmlMarkerCheck):
    """Represent `AppleDeveloperCheck`."""

    check_key = "apple_developer"
    endpoint_key = "https://developer.apple.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("apple",)


class AppleAppStoreCheck(HtmlMarkerCheck):
    """Represent `AppleAppStoreCheck`."""

    check_key = "apple_appstore"
    endpoint_key = "https://www.apple.com/app-store/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("app store",)


class AppleSupportCheck(HtmlMarkerCheck):
    """Represent `AppleSupportCheck`."""

    check_key = "apple_support"
    endpoint_key = "https://support.apple.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("apple",)


class AppleServiceChecker(BaseServiceChecker):
    """Represent `AppleServiceChecker`."""

    service_key = "apple"
    logo_url = "https://img.logo.dev/apple.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://www.apple.com/support/systemstatus/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            AppleHomepageCheck(),
            AppleSystemStatusCheck(),
            AppleDeveloperCheck(),
            AppleAppStoreCheck(),
            AppleSupportCheck(),
        ]

"""Provide functionality for `is_it_down.checkers.services.pagerduty`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class PagerDutyStatusPageCheck(HtmlMarkerCheck):
    """Represent `PagerDutyStatusPageCheck`."""

    check_key = "pagerduty_status_page"
    endpoint_key = "https://status.pagerduty.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("pagerduty",)


class PagerDutyHomepageCheck(HtmlMarkerCheck):
    """Represent `PagerDutyHomepageCheck`."""

    check_key = "pagerduty_homepage"
    endpoint_key = "https://www.pagerduty.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("pagerduty",)


class PagerDutyDevelopersCheck(HtmlMarkerCheck):
    """Represent `PagerDutyDevelopersCheck`."""

    check_key = "pagerduty_developers"
    endpoint_key = "https://developer.pagerduty.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("developer",)


class PagerDutySupportCheck(HtmlMarkerCheck):
    """Represent `PagerDutySupportCheck`."""

    check_key = "pagerduty_support"
    endpoint_key = "https://support.pagerduty.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("pagerduty",)


class PagerDutyCommunityCheck(HtmlMarkerCheck):
    """Represent `PagerDutyCommunityCheck`."""

    check_key = "pagerduty_community"
    endpoint_key = "https://community.pagerduty.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("pagerduty",)


class PagerDutyServiceChecker(BaseServiceChecker):
    """Represent `PagerDutyServiceChecker`."""

    service_key = "pagerduty"
    logo_url = "https://img.logo.dev/pagerduty.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.pagerduty.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            PagerDutyStatusPageCheck(),
            PagerDutyHomepageCheck(),
            PagerDutyDevelopersCheck(),
            PagerDutySupportCheck(),
            PagerDutyCommunityCheck(),
        ]

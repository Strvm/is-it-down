"""Provide functionality for `is_it_down.checkers.services.zendesk`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class ZendeskStatusPageCheck(HtmlMarkerCheck):
    """Represent `ZendeskStatusPageCheck`."""

    check_key = "zendesk_status_page"
    endpoint_key = "https://status.zendesk.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("zendesk",)


class ZendeskHomepageCheck(HtmlMarkerCheck):
    """Represent `ZendeskHomepageCheck`."""

    check_key = "zendesk_homepage"
    endpoint_key = "https://www.zendesk.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("zendesk",)


class ZendeskDevelopersCheck(HtmlMarkerCheck):
    """Represent `ZendeskDevelopersCheck`."""

    check_key = "zendesk_developers"
    endpoint_key = "https://developer.zendesk.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("zendesk",)


class ZendeskSupportCheck(HtmlMarkerCheck):
    """Represent `ZendeskSupportCheck`."""

    check_key = "zendesk_support"
    endpoint_key = "https://support.zendesk.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("zendesk",)


class ZendeskCommunityCheck(HtmlMarkerCheck):
    """Represent `ZendeskCommunityCheck`."""

    check_key = "zendesk_community"
    endpoint_key = "https://community.zendesk.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("zendesk",)


class ZendeskServiceChecker(BaseServiceChecker):
    """Represent `ZendeskServiceChecker`."""

    service_key = "zendesk"
    logo_url = "https://img.logo.dev/zendesk.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.zendesk.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            ZendeskStatusPageCheck(),
            ZendeskHomepageCheck(),
            ZendeskDevelopersCheck(),
            ZendeskSupportCheck(),
            ZendeskCommunityCheck(),
        ]

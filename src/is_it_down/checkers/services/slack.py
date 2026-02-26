"""Provide functionality for `is_it_down.checkers.services.slack`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class SlackStatusPageCheck(HtmlMarkerCheck):
    """Represent `SlackStatusPageCheck`."""

    check_key = "slack_status_page"
    endpoint_key = "https://status.slack.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("slack",)


class SlackHomepageCheck(HtmlMarkerCheck):
    """Represent `SlackHomepageCheck`."""

    check_key = "slack_homepage"
    endpoint_key = "https://slack.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("slack",)


class SlackApiDocsCheck(HtmlMarkerCheck):
    """Represent `SlackApiDocsCheck`."""

    check_key = "slack_api_docs"
    endpoint_key = "https://api.slack.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("slack",)


class SlackHelpCheck(HtmlMarkerCheck):
    """Represent `SlackHelpCheck`."""

    check_key = "slack_help"
    endpoint_key = "https://slack.com/help"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("slack",)


class SlackCommunityCheck(HtmlMarkerCheck):
    """Represent `SlackCommunityCheck`."""

    check_key = "slack_community"
    endpoint_key = "https://slackcommunity.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("slack",)


class SlackServiceChecker(BaseServiceChecker):
    """Represent `SlackServiceChecker`."""

    service_key = "slack"
    logo_url = "https://img.logo.dev/slack.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.slack.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            SlackStatusPageCheck(),
            SlackHomepageCheck(),
            SlackApiDocsCheck(),
            SlackHelpCheck(),
            SlackCommunityCheck(),
        ]

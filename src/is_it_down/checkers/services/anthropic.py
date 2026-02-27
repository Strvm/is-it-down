"""Provide functionality for `is_it_down.checkers.services.anthropic`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck, StatuspageStatusCheck, StatuspageSummaryCheck


class AnthropicStatusApiCheck(StatuspageStatusCheck):
    """Represent `AnthropicStatusApiCheck`."""

    check_key = "anthropic_status_api"
    endpoint_key = "https://status.anthropic.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class AnthropicSummaryApiCheck(StatuspageSummaryCheck):
    """Represent `AnthropicSummaryApiCheck`."""

    check_key = "anthropic_summary_api"
    endpoint_key = "https://status.anthropic.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class AnthropicStatusPageCheck(HtmlMarkerCheck):
    """Represent `AnthropicStatusPageCheck`."""

    check_key = "anthropic_status_page"
    endpoint_key = "https://status.anthropic.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("status",)


class AnthropicHomepageCheck(HtmlMarkerCheck):
    """Represent `AnthropicHomepageCheck`."""

    check_key = "anthropic_homepage"
    endpoint_key = "https://www.anthropic.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("anthropic",)


class AnthropicDocsCheck(HtmlMarkerCheck):
    """Represent `AnthropicDocsCheck`."""

    check_key = "anthropic_docs"
    endpoint_key = "https://docs.anthropic.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.1
    expected_markers = ("anthropic",)


class AnthropicServiceChecker(BaseServiceChecker):
    """Represent `AnthropicServiceChecker`."""

    service_key = "anthropic"
    logo_url = "https://img.logo.dev/anthropic.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.anthropic.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            AnthropicStatusApiCheck(),
            AnthropicSummaryApiCheck(),
            AnthropicStatusPageCheck(),
            AnthropicHomepageCheck(),
            AnthropicDocsCheck(),
        ]

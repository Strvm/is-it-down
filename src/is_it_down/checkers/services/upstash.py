"""Provide functionality for `is_it_down.checkers.services.upstash`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck, StatuspageStatusCheck, StatuspageSummaryCheck


class UpstashStatusApiCheck(StatuspageStatusCheck):
    """Represent `UpstashStatusApiCheck`."""

    check_key = "upstash_status_api"
    endpoint_key = "https://status.upstash.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class UpstashSummaryApiCheck(StatuspageSummaryCheck):
    """Represent `UpstashSummaryApiCheck`."""

    check_key = "upstash_summary_api"
    endpoint_key = "https://status.upstash.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class UpstashStatusPageCheck(HtmlMarkerCheck):
    """Represent `UpstashStatusPageCheck`."""

    check_key = "upstash_status_page"
    endpoint_key = "https://status.upstash.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("upstash",)


class UpstashHomepageCheck(HtmlMarkerCheck):
    """Represent `UpstashHomepageCheck`."""

    check_key = "upstash_homepage"
    endpoint_key = "https://upstash.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("upstash",)


class UpstashDocsCheck(HtmlMarkerCheck):
    """Represent `UpstashDocsCheck`."""

    check_key = "upstash_docs"
    endpoint_key = "https://docs.upstash.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("upstash",)


class UpstashServiceChecker(BaseServiceChecker):
    """Represent `UpstashServiceChecker`."""

    service_key = "upstash"
    logo_url = "https://img.logo.dev/upstash.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.upstash.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            UpstashStatusApiCheck(),
            UpstashSummaryApiCheck(),
            UpstashStatusPageCheck(),
            UpstashHomepageCheck(),
            UpstashDocsCheck(),
        ]

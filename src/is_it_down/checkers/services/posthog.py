"""Provide functionality for `is_it_down.checkers.services.posthog`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck, StatuspageStatusCheck


class PostHogStatusApiCheck(StatuspageStatusCheck):
    """Represent `PostHogStatusApiCheck`."""

    check_key = "posthog_status_api"
    endpoint_key = "https://www.posthogstatus.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class PostHogSummaryApiCheck(StatuspageStatusCheck):
    """Represent `PostHogSummaryApiCheck`."""

    check_key = "posthog_summary_api"
    endpoint_key = "https://www.posthogstatus.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class PostHogStatusPageCheck(HtmlMarkerCheck):
    """Represent `PostHogStatusPageCheck`."""

    check_key = "posthog_status_page"
    endpoint_key = "https://www.posthogstatus.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("status",)


class PostHogHomepageCheck(HtmlMarkerCheck):
    """Represent `PostHogHomepageCheck`."""

    check_key = "posthog_homepage"
    endpoint_key = "https://posthog.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("posthog",)


class PostHogDocsCheck(HtmlMarkerCheck):
    """Represent `PostHogDocsCheck`."""

    check_key = "posthog_docs"
    endpoint_key = "https://posthog.com/docs"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.1
    expected_markers = ("posthog",)


class PostHogServiceChecker(BaseServiceChecker):
    """Represent `PostHogServiceChecker`."""

    service_key = "posthog"
    logo_url = "https://img.logo.dev/posthog.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://www.posthogstatus.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            PostHogStatusApiCheck(),
            PostHogSummaryApiCheck(),
            PostHogStatusPageCheck(),
            PostHogHomepageCheck(),
            PostHogDocsCheck(),
        ]

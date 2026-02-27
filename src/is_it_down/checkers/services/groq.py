"""Provide functionality for `is_it_down.checkers.services.groq`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class GroqStatusPageCheck(HtmlMarkerCheck):
    """Represent `GroqStatusPageCheck`."""

    check_key = "groq_status_page"
    endpoint_key = "https://status.groq.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("groq",)


class GroqHomepageCheck(HtmlMarkerCheck):
    """Represent `GroqHomepageCheck`."""

    check_key = "groq_homepage"
    endpoint_key = "https://groq.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("groq",)


class GroqDocsCheck(HtmlMarkerCheck):
    """Represent `GroqDocsCheck`."""

    check_key = "groq_docs"
    endpoint_key = "https://console.groq.com/docs/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("groq",)


class GroqSupportCheck(HtmlMarkerCheck):
    """Represent `GroqSupportCheck`."""

    check_key = "groq_support"
    endpoint_key = "https://console.groq.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("groq",)


class GroqBlogCheck(HtmlMarkerCheck):
    """Represent `GroqBlogCheck`."""

    check_key = "groq_blog"
    endpoint_key = "https://groq.com/newsroom/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("groq",)


class GroqServiceChecker(BaseServiceChecker):
    """Represent `GroqServiceChecker`."""

    service_key = "groq"
    logo_url = "https://img.logo.dev/groq.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.groq.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            GroqStatusPageCheck(),
            GroqHomepageCheck(),
            GroqDocsCheck(),
            GroqSupportCheck(),
            GroqBlogCheck(),
        ]

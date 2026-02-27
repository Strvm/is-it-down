"""Provide functionality for `is_it_down.checkers.services.togetherai`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class TogetherAiStatusPageCheck(HtmlMarkerCheck):
    """Represent `TogetherAiStatusPageCheck`."""

    check_key = "togetherai_status_page"
    endpoint_key = "https://status.together.ai/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("together",)


class TogetherAiHomepageCheck(HtmlMarkerCheck):
    """Represent `TogetherAiHomepageCheck`."""

    check_key = "togetherai_homepage"
    endpoint_key = "https://www.together.ai/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("together",)


class TogetherAiDocsCheck(HtmlMarkerCheck):
    """Represent `TogetherAiDocsCheck`."""

    check_key = "togetherai_docs"
    endpoint_key = "https://docs.together.ai/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("together",)


class TogetherAiSupportCheck(HtmlMarkerCheck):
    """Represent `TogetherAiSupportCheck`."""

    check_key = "togetherai_support"
    endpoint_key = "https://api.together.ai/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("together",)


class TogetherAiBlogCheck(HtmlMarkerCheck):
    """Represent `TogetherAiBlogCheck`."""

    check_key = "togetherai_blog"
    endpoint_key = "https://www.together.ai/blog"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("together",)


class TogetherAiServiceChecker(BaseServiceChecker):
    """Represent `TogetherAiServiceChecker`."""

    service_key = "togetherai"
    logo_url = "https://img.logo.dev/together.ai?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.together.ai/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            TogetherAiStatusPageCheck(),
            TogetherAiHomepageCheck(),
            TogetherAiDocsCheck(),
            TogetherAiSupportCheck(),
            TogetherAiBlogCheck(),
        ]

"""Provide functionality for `is_it_down.checkers.services.mistral`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class MistralStatusPageCheck(HtmlMarkerCheck):
    """Represent `MistralStatusPageCheck`."""

    check_key = "mistral_status_page"
    endpoint_key = "https://status.mistral.ai/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("mistral",)


class MistralHomepageCheck(HtmlMarkerCheck):
    """Represent `MistralHomepageCheck`."""

    check_key = "mistral_homepage"
    endpoint_key = "https://mistral.ai/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("mistral",)


class MistralDocsCheck(HtmlMarkerCheck):
    """Represent `MistralDocsCheck`."""

    check_key = "mistral_docs"
    endpoint_key = "https://docs.mistral.ai/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("mistral",)


class MistralSupportCheck(HtmlMarkerCheck):
    """Represent `MistralSupportCheck`."""

    check_key = "mistral_support"
    endpoint_key = "https://console.mistral.ai/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("mistral",)


class MistralBlogCheck(HtmlMarkerCheck):
    """Represent `MistralBlogCheck`."""

    check_key = "mistral_blog"
    endpoint_key = "https://mistral.ai/news"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("mistral",)


class MistralServiceChecker(BaseServiceChecker):
    """Represent `MistralServiceChecker`."""

    service_key = "mistral"
    logo_url = "https://img.logo.dev/mistral.ai?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.mistral.ai/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            MistralStatusPageCheck(),
            MistralHomepageCheck(),
            MistralDocsCheck(),
            MistralSupportCheck(),
            MistralBlogCheck(),
        ]

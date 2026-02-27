"""Provide functionality for `is_it_down.checkers.services.cohere`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class CohereStatusPageCheck(HtmlMarkerCheck):
    """Represent `CohereStatusPageCheck`."""

    check_key = "cohere_status_page"
    endpoint_key = "https://status.cohere.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("cohere",)


class CohereHomepageCheck(HtmlMarkerCheck):
    """Represent `CohereHomepageCheck`."""

    check_key = "cohere_homepage"
    endpoint_key = "https://cohere.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("cohere",)


class CohereDocsCheck(HtmlMarkerCheck):
    """Represent `CohereDocsCheck`."""

    check_key = "cohere_docs"
    endpoint_key = "https://docs.cohere.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("cohere",)


class CohereSupportCheck(HtmlMarkerCheck):
    """Represent `CohereSupportCheck`."""

    check_key = "cohere_support"
    endpoint_key = "https://dashboard.cohere.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("cohere",)


class CohereBlogCheck(HtmlMarkerCheck):
    """Represent `CohereBlogCheck`."""

    check_key = "cohere_blog"
    endpoint_key = "https://cohere.com/blog"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("cohere",)


class CohereServiceChecker(BaseServiceChecker):
    """Represent `CohereServiceChecker`."""

    service_key = "cohere"
    logo_url = "https://img.logo.dev/cohere.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.cohere.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            CohereStatusPageCheck(),
            CohereHomepageCheck(),
            CohereDocsCheck(),
            CohereSupportCheck(),
            CohereBlogCheck(),
        ]

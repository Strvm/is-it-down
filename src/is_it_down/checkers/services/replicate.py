"""Provide functionality for `is_it_down.checkers.services.replicate`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class ReplicateStatusPageCheck(HtmlMarkerCheck):
    """Represent `ReplicateStatusPageCheck`."""

    check_key = "replicate_status_page"
    endpoint_key = "https://status.replicate.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("replicate",)


class ReplicateHomepageCheck(HtmlMarkerCheck):
    """Represent `ReplicateHomepageCheck`."""

    check_key = "replicate_homepage"
    endpoint_key = "https://replicate.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("replicate",)


class ReplicateDocsCheck(HtmlMarkerCheck):
    """Represent `ReplicateDocsCheck`."""

    check_key = "replicate_docs"
    endpoint_key = "https://replicate.com/docs"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("replicate",)


class ReplicateSupportCheck(HtmlMarkerCheck):
    """Represent `ReplicateSupportCheck`."""

    check_key = "replicate_support"
    endpoint_key = "https://replicate.com/explore"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("replicate",)


class ReplicateBlogCheck(HtmlMarkerCheck):
    """Represent `ReplicateBlogCheck`."""

    check_key = "replicate_blog"
    endpoint_key = "https://replicate.com/blog"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("replicate",)


class ReplicateServiceChecker(BaseServiceChecker):
    """Represent `ReplicateServiceChecker`."""

    service_key = "replicate"
    logo_url = "https://img.logo.dev/replicate.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.replicate.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            ReplicateStatusPageCheck(),
            ReplicateHomepageCheck(),
            ReplicateDocsCheck(),
            ReplicateSupportCheck(),
            ReplicateBlogCheck(),
        ]

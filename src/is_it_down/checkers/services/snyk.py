"""Provide functionality for `is_it_down.checkers.services.snyk`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class SnykStatusPageCheck(HtmlMarkerCheck):
    """Represent `SnykStatusPageCheck`."""

    check_key = "snyk_status_page"
    endpoint_key = "https://status.snyk.io/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("snyk",)


class SnykHomepageCheck(HtmlMarkerCheck):
    """Represent `SnykHomepageCheck`."""

    check_key = "snyk_homepage"
    endpoint_key = "https://snyk.io/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("snyk",)


class SnykDocsCheck(HtmlMarkerCheck):
    """Represent `SnykDocsCheck`."""

    check_key = "snyk_docs"
    endpoint_key = "https://docs.snyk.io/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("snyk",)


class SnykSupportCheck(HtmlMarkerCheck):
    """Represent `SnykSupportCheck`."""

    check_key = "snyk_support"
    endpoint_key = "https://support.snyk.io/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("snyk",)


class SnykBlogCheck(HtmlMarkerCheck):
    """Represent `SnykBlogCheck`."""

    check_key = "snyk_blog"
    endpoint_key = "https://snyk.io/blog/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("snyk",)


class SnykServiceChecker(BaseServiceChecker):
    """Represent `SnykServiceChecker`."""

    service_key = "snyk"
    logo_url = "https://img.logo.dev/snyk.io?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.snyk.io/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            SnykStatusPageCheck(),
            SnykHomepageCheck(),
            SnykDocsCheck(),
            SnykSupportCheck(),
            SnykBlogCheck(),
        ]

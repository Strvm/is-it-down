"""Provide functionality for `is_it_down.checkers.services.codecov`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class CodecovStatusPageCheck(HtmlMarkerCheck):
    """Represent `CodecovStatusPageCheck`."""

    check_key = "codecov_status_page"
    endpoint_key = "https://status.codecov.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("codecov",)


class CodecovHomepageCheck(HtmlMarkerCheck):
    """Represent `CodecovHomepageCheck`."""

    check_key = "codecov_homepage"
    endpoint_key = "https://about.codecov.io/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("codecov",)


class CodecovDocsCheck(HtmlMarkerCheck):
    """Represent `CodecovDocsCheck`."""

    check_key = "codecov_docs"
    endpoint_key = "https://docs.codecov.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("codecov",)


class CodecovSupportCheck(HtmlMarkerCheck):
    """Represent `CodecovSupportCheck`."""

    check_key = "codecov_support"
    endpoint_key = "https://community.codecov.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("codecov",)


class CodecovBlogCheck(HtmlMarkerCheck):
    """Represent `CodecovBlogCheck`."""

    check_key = "codecov_blog"
    endpoint_key = "https://about.codecov.io/blog"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("codecov",)


class CodecovServiceChecker(BaseServiceChecker):
    """Represent `CodecovServiceChecker`."""

    service_key = "codecov"
    logo_url = "https://img.logo.dev/codecov.io?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.codecov.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            CodecovStatusPageCheck(),
            CodecovHomepageCheck(),
            CodecovDocsCheck(),
            CodecovSupportCheck(),
            CodecovBlogCheck(),
        ]

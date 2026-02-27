"""Provide functionality for `is_it_down.checkers.services.datastax`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class DataStaxStatusPageCheck(HtmlMarkerCheck):
    """Represent `DataStaxStatusPageCheck`."""

    check_key = "datastax_status_page"
    endpoint_key = "https://status.datastax.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("datastax",)


class DataStaxHomepageCheck(HtmlMarkerCheck):
    """Represent `DataStaxHomepageCheck`."""

    check_key = "datastax_homepage"
    endpoint_key = "https://www.datastax.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("datastax",)


class DataStaxDocsCheck(HtmlMarkerCheck):
    """Represent `DataStaxDocsCheck`."""

    check_key = "datastax_docs"
    endpoint_key = "https://docs.datastax.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("datastax",)


class DataStaxSupportCheck(HtmlMarkerCheck):
    """Represent `DataStaxSupportCheck`."""

    check_key = "datastax_support"
    endpoint_key = "https://support.datastax.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("datastax",)


class DataStaxBlogCheck(HtmlMarkerCheck):
    """Represent `DataStaxBlogCheck`."""

    check_key = "datastax_blog"
    endpoint_key = "https://www.datastax.com/blog"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("datastax",)


class DataStaxServiceChecker(BaseServiceChecker):
    """Represent `DataStaxServiceChecker`."""

    service_key = "datastax"
    logo_url = "https://img.logo.dev/datastax.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.datastax.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            DataStaxStatusPageCheck(),
            DataStaxHomepageCheck(),
            DataStaxDocsCheck(),
            DataStaxSupportCheck(),
            DataStaxBlogCheck(),
        ]

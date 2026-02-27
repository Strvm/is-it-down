"""Provide functionality for `is_it_down.checkers.services.clickhouse`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class ClickHouseStatusPageCheck(HtmlMarkerCheck):
    """Represent `ClickHouseStatusPageCheck`."""

    check_key = "clickhouse_status_page"
    endpoint_key = "https://status.clickhouse.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("clickhouse",)


class ClickHouseHomepageCheck(HtmlMarkerCheck):
    """Represent `ClickHouseHomepageCheck`."""

    check_key = "clickhouse_homepage"
    endpoint_key = "https://clickhouse.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("clickhouse",)


class ClickHouseDocsCheck(HtmlMarkerCheck):
    """Represent `ClickHouseDocsCheck`."""

    check_key = "clickhouse_docs"
    endpoint_key = "https://clickhouse.com/docs/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("clickhouse",)


class ClickHouseSupportCheck(HtmlMarkerCheck):
    """Represent `ClickHouseSupportCheck`."""

    check_key = "clickhouse_support"
    endpoint_key = "https://clickhouse.com/company/contact"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("clickhouse",)


class ClickHouseBlogCheck(HtmlMarkerCheck):
    """Represent `ClickHouseBlogCheck`."""

    check_key = "clickhouse_blog"
    endpoint_key = "https://clickhouse.com/blog/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("clickhouse",)


class ClickHouseServiceChecker(BaseServiceChecker):
    """Represent `ClickHouseServiceChecker`."""

    service_key = "clickhouse"
    logo_url = "https://img.logo.dev/clickhouse.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.clickhouse.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            ClickHouseStatusPageCheck(),
            ClickHouseHomepageCheck(),
            ClickHouseDocsCheck(),
            ClickHouseSupportCheck(),
            ClickHouseBlogCheck(),
        ]

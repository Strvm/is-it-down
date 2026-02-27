"""Provide functionality for `is_it_down.checkers.services.snowflake`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck, StatuspageStatusCheck, StatuspageSummaryCheck


class SnowflakeStatusApiCheck(StatuspageStatusCheck):
    """Represent `SnowflakeStatusApiCheck`."""

    check_key = "snowflake_status_api"
    endpoint_key = "https://status.snowflake.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class SnowflakeSummaryApiCheck(StatuspageSummaryCheck):
    """Represent `SnowflakeSummaryApiCheck`."""

    check_key = "snowflake_summary_api"
    endpoint_key = "https://status.snowflake.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class SnowflakeStatusPageCheck(HtmlMarkerCheck):
    """Represent `SnowflakeStatusPageCheck`."""

    check_key = "snowflake_status_page"
    endpoint_key = "https://status.snowflake.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("status",)


class SnowflakeHomepageCheck(HtmlMarkerCheck):
    """Represent `SnowflakeHomepageCheck`."""

    check_key = "snowflake_homepage"
    endpoint_key = "https://www.snowflake.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("snowflake",)


class SnowflakeDocsCheck(HtmlMarkerCheck):
    """Represent `SnowflakeDocsCheck`."""

    check_key = "snowflake_docs"
    endpoint_key = "https://docs.snowflake.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.1
    expected_markers = ("snowflake",)


class SnowflakeServiceChecker(BaseServiceChecker):
    """Represent `SnowflakeServiceChecker`."""

    service_key = "snowflake"
    logo_url = "https://img.logo.dev/snowflake.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.snowflake.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            SnowflakeStatusApiCheck(),
            SnowflakeSummaryApiCheck(),
            SnowflakeStatusPageCheck(),
            SnowflakeHomepageCheck(),
            SnowflakeDocsCheck(),
        ]

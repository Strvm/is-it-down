"""Provide functionality for `is_it_down.checkers.services.databricks`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class DatabricksStatusApiCheck(HtmlMarkerCheck):
    """Represent `DatabricksStatusApiCheck`."""

    check_key = "databricks_status_api"
    endpoint_key = "https://accounts.cloud.databricks.com/login"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("databricks",)


class DatabricksSummaryApiCheck(HtmlMarkerCheck):
    """Represent `DatabricksSummaryApiCheck`."""

    check_key = "databricks_summary_api"
    endpoint_key = "https://www.databricks.com/solutions"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("databricks",)


class DatabricksStatusPageCheck(HtmlMarkerCheck):
    """Represent `DatabricksStatusPageCheck`."""

    check_key = "databricks_status_page"
    endpoint_key = "https://status.databricks.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("status",)


class DatabricksHomepageCheck(HtmlMarkerCheck):
    """Represent `DatabricksHomepageCheck`."""

    check_key = "databricks_homepage"
    endpoint_key = "https://www.databricks.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("databricks",)


class DatabricksDocsCheck(HtmlMarkerCheck):
    """Represent `DatabricksDocsCheck`."""

    check_key = "databricks_docs"
    endpoint_key = "https://docs.databricks.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.1
    expected_markers = ("databricks",)


class DatabricksServiceChecker(BaseServiceChecker):
    """Represent `DatabricksServiceChecker`."""

    service_key = "databricks"
    logo_url = "https://img.logo.dev/databricks.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.databricks.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            DatabricksStatusApiCheck(),
            DatabricksSummaryApiCheck(),
            DatabricksStatusPageCheck(),
            DatabricksHomepageCheck(),
            DatabricksDocsCheck(),
        ]

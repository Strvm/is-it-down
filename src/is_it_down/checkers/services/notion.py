"""Provide functionality for `is_it_down.checkers.services.notion`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.services.statuspage_common import (
    ApiAuthResponseCheck,
    HtmlMarkerCheck,
    StatuspageStatusCheck,
    StatuspageSummaryCheck,
)


class NotionStatusPageCheck(StatuspageStatusCheck):
    """Represent `NotionStatusPageCheck`."""

    check_key = "notion_status_page"
    endpoint_key = "https://www.notion-status.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class NotionSummaryCheck(StatuspageSummaryCheck):
    """Represent `NotionSummaryCheck`."""

    check_key = "notion_summary"
    endpoint_key = "https://www.notion-status.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class NotionHomepageCheck(HtmlMarkerCheck):
    """Represent `NotionHomepageCheck`."""

    check_key = "notion_homepage"
    endpoint_key = "https://www.notion.so/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("notion",)


class NotionDocsCheck(HtmlMarkerCheck):
    """Represent `NotionDocsCheck`."""

    check_key = "notion_docs"
    endpoint_key = "https://developers.notion.com/reference/intro"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("notion",)


class NotionApiAuthCheck(ApiAuthResponseCheck):
    """Represent `NotionApiAuthCheck`."""

    check_key = "notion_api_auth"
    endpoint_key = "https://api.notion.com/v1/users/me"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    request_method = "GET"
    request_headers = {"Accept": "application/json", "Notion-Version": "2022-06-28"}
    request_json = None
    request_data = None
    expected_http_statuses = (401, 403)


class NotionServiceChecker(BaseServiceChecker):
    """Represent `NotionServiceChecker`."""

    service_key = "notion"
    logo_url = "https://cdn.simpleicons.org/notion"
    official_uptime = "https://www.notion-status.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            NotionStatusPageCheck(),
            NotionSummaryCheck(),
            NotionHomepageCheck(),
            NotionDocsCheck(),
            NotionApiAuthCheck(),
        ]

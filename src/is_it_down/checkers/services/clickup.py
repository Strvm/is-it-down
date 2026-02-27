"""Provide functionality for `is_it_down.checkers.services.clickup`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import ApiAuthResponseCheck, HtmlMarkerCheck


class ClickUpStatusApiCheck(ApiAuthResponseCheck):
    """Represent `ClickUpStatusApiCheck`."""

    check_key = "clickup_status_api"
    endpoint_key = "https://api.clickup.com/api/v2/user"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_http_statuses = (400, 401, 403)
    request_headers = {"Accept": "application/json"}
    require_error_signal = False


class ClickUpSummaryApiCheck(HtmlMarkerCheck):
    """Represent `ClickUpSummaryApiCheck`."""

    check_key = "clickup_summary_api"
    endpoint_key = "https://app.clickup.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("clickup",)


class ClickUpStatusPageCheck(HtmlMarkerCheck):
    """Represent `ClickUpStatusPageCheck`."""

    check_key = "clickup_status_page"
    endpoint_key = "https://status.clickup.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("status",)


class ClickUpHomepageCheck(HtmlMarkerCheck):
    """Represent `ClickUpHomepageCheck`."""

    check_key = "clickup_homepage"
    endpoint_key = "https://clickup.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("clickup",)


class ClickUpDocsCheck(HtmlMarkerCheck):
    """Represent `ClickUpDocsCheck`."""

    check_key = "clickup_docs"
    endpoint_key = "https://developer.clickup.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.1
    expected_markers = ("clickup",)


class ClickUpServiceChecker(BaseServiceChecker):
    """Represent `ClickUpServiceChecker`."""

    service_key = "clickup"
    logo_url = "https://img.logo.dev/clickup.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.clickup.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            ClickUpStatusApiCheck(),
            ClickUpSummaryApiCheck(),
            ClickUpStatusPageCheck(),
            ClickUpHomepageCheck(),
            ClickUpDocsCheck(),
        ]

"""Provide functionality for `is_it_down.checkers.services.dropbox`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import (
    ApiAuthResponseCheck,
    HtmlMarkerCheck,
    StatuspageStatusCheck,
    StatuspageSummaryCheck,
)


class DropboxStatusPageCheck(StatuspageStatusCheck):
    """Represent `DropboxStatusPageCheck`."""

    check_key = "dropbox_status_page"
    endpoint_key = "https://status.dropbox.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class DropboxSummaryCheck(StatuspageSummaryCheck):
    """Represent `DropboxSummaryCheck`."""

    check_key = "dropbox_summary"
    endpoint_key = "https://status.dropbox.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class DropboxHomepageCheck(HtmlMarkerCheck):
    """Represent `DropboxHomepageCheck`."""

    check_key = "dropbox_homepage"
    endpoint_key = "https://www.dropbox.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("dropbox",)


class DropboxDocsCheck(HtmlMarkerCheck):
    """Represent `DropboxDocsCheck`."""

    check_key = "dropbox_docs"
    endpoint_key = "https://help.dropbox.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("dropbox",)


class DropboxApiAuthCheck(ApiAuthResponseCheck):
    """Represent `DropboxApiAuthCheck`."""

    check_key = "dropbox_api_auth"
    endpoint_key = "https://api.dropboxapi.com/2/users/get_current_account"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    request_method = "POST"
    request_headers = {"Accept": "application/json", "Content-Type": "application/json"}
    request_json = {}
    request_data = None
    expected_http_statuses = (400, 401, 403)


class DropboxServiceChecker(BaseServiceChecker):
    """Represent `DropboxServiceChecker`."""

    service_key = "dropbox"
    logo_url = "https://cdn.simpleicons.org/dropbox"
    official_uptime = "https://status.dropbox.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            DropboxStatusPageCheck(),
            DropboxSummaryCheck(),
            DropboxHomepageCheck(),
            DropboxDocsCheck(),
            DropboxApiAuthCheck(),
        ]

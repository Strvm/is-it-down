"""Provide functionality for `is_it_down.checkers.services.sendgrid`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.services.twilio import TwilioServiceChecker
from is_it_down.checkers.statuspage_common import (
    ApiAuthResponseCheck,
    HtmlMarkerCheck,
    StatuspageStatusCheck,
    StatuspageSummaryCheck,
)


class SendGridStatusPageCheck(StatuspageStatusCheck):
    """Represent `SendGridStatusPageCheck`."""

    check_key = "sendgrid_status_page"
    endpoint_key = "https://status.sendgrid.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class SendGridSummaryCheck(StatuspageSummaryCheck):
    """Represent `SendGridSummaryCheck`."""

    check_key = "sendgrid_summary"
    endpoint_key = "https://status.sendgrid.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class SendGridHomepageCheck(HtmlMarkerCheck):
    """Represent `SendGridHomepageCheck`."""

    check_key = "sendgrid_homepage"
    endpoint_key = "https://sendgrid.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("sendgrid",)


class SendGridDocsCheck(HtmlMarkerCheck):
    """Represent `SendGridDocsCheck`."""

    check_key = "sendgrid_docs"
    endpoint_key = "https://www.twilio.com/docs/sendgrid/api-reference/how-to-use-the-sendgrid-v3-api"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("sendgrid",)


class SendGridApiAuthCheck(ApiAuthResponseCheck):
    """Represent `SendGridApiAuthCheck`."""

    check_key = "sendgrid_api_auth"
    endpoint_key = "https://api.sendgrid.com/v3/user/profile"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    request_method = "GET"
    request_headers = {"Accept": "application/json"}
    request_json = None
    request_data = None
    expected_http_statuses = (401, 403)


class SendGridServiceChecker(BaseServiceChecker):
    """Represent `SendGridServiceChecker`."""

    service_key = "sendgrid"
    logo_url = "https://img.logo.dev/sendgrid.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.sendgrid.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = (TwilioServiceChecker,)

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            SendGridStatusPageCheck(),
            SendGridSummaryCheck(),
            SendGridHomepageCheck(),
            SendGridDocsCheck(),
            SendGridApiAuthCheck(),
        ]

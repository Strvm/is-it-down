"""Provide functionality for `is_it_down.checkers.services.paypal`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import (
    ApiAuthResponseCheck,
    HtmlMarkerCheck,
    StatuspageStatusCheck,
    StatuspageSummaryCheck,
)


class PayPalStatusPageCheck(StatuspageStatusCheck):
    """Represent `PayPalStatusPageCheck`."""

    check_key = "paypal_status_page"
    endpoint_key = "https://www.paypal-status.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class PayPalSummaryCheck(StatuspageSummaryCheck):
    """Represent `PayPalSummaryCheck`."""

    check_key = "paypal_summary"
    endpoint_key = "https://www.paypal-status.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class PayPalHomepageCheck(HtmlMarkerCheck):
    """Represent `PayPalHomepageCheck`."""

    check_key = "paypal_homepage"
    endpoint_key = "https://www.paypal.com/us/home"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("paypal",)


class PayPalDocsCheck(HtmlMarkerCheck):
    """Represent `PayPalDocsCheck`."""

    check_key = "paypal_docs"
    endpoint_key = "https://developer.paypal.com/api/rest/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("paypal",)


class PayPalApiAuthCheck(ApiAuthResponseCheck):
    """Represent `PayPalApiAuthCheck`."""

    check_key = "paypal_api_auth"
    endpoint_key = "https://api-m.paypal.com/v1/reporting/balances"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    request_method = "GET"
    request_headers = {"Accept": "application/json"}
    request_json = None
    request_data = None
    expected_http_statuses = (401, 403)


class PayPalServiceChecker(BaseServiceChecker):
    """Represent `PayPalServiceChecker`."""

    service_key = "paypal"
    logo_url = "https://cdn.simpleicons.org/paypal"
    official_uptime = "https://www.paypal-status.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            PayPalStatusPageCheck(),
            PayPalSummaryCheck(),
            PayPalHomepageCheck(),
            PayPalDocsCheck(),
            PayPalApiAuthCheck(),
        ]

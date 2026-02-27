"""Provide functionality for `is_it_down.checkers.services.yahoo`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class YahooHomepageCheck(HtmlMarkerCheck):
    """Represent `YahooHomepageCheck`."""

    check_key = "yahoo_home_page"
    endpoint_key = "https://www.yahoo.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("yahoo",)


class YahooMailCheck(HtmlMarkerCheck):
    """Represent `YahooMailCheck`."""

    check_key = "yahoo_mail"
    endpoint_key = "https://mail.yahoo.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("yahoo",)


class YahooFinanceCheck(HtmlMarkerCheck):
    """Represent `YahooFinanceCheck`."""

    check_key = "yahoo_finance"
    endpoint_key = "https://finance.yahoo.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("yahoo",)


class YahooSportsCheck(HtmlMarkerCheck):
    """Represent `YahooSportsCheck`."""

    check_key = "yahoo_sports"
    endpoint_key = "https://sports.yahoo.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("yahoo",)


class YahooStatusPageCheck(HtmlMarkerCheck):
    """Represent `YahooStatusPageCheck`."""

    check_key = "yahoo_status_page"
    endpoint_key = "https://status.yahoo.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("status",)


class YahooServiceChecker(BaseServiceChecker):
    """Represent `YahooServiceChecker`."""

    service_key = "yahoo"
    logo_url = "https://img.logo.dev/yahoo.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.yahoo.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            YahooHomepageCheck(),
            YahooMailCheck(),
            YahooFinanceCheck(),
            YahooSportsCheck(),
            YahooStatusPageCheck(),
        ]

"""Provide functionality for `is_it_down.checkers.services.coinbase`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck, StatuspageStatusCheck, StatuspageSummaryCheck


class CoinbaseStatusApiCheck(StatuspageStatusCheck):
    """Represent `CoinbaseStatusApiCheck`."""

    check_key = "coinbase_status_api"
    endpoint_key = "https://status.coinbase.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class CoinbaseSummaryApiCheck(StatuspageSummaryCheck):
    """Represent `CoinbaseSummaryApiCheck`."""

    check_key = "coinbase_summary_api"
    endpoint_key = "https://status.coinbase.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class CoinbaseStatusPageCheck(HtmlMarkerCheck):
    """Represent `CoinbaseStatusPageCheck`."""

    check_key = "coinbase_status_page"
    endpoint_key = "https://status.coinbase.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("status",)


class CoinbaseHomepageCheck(HtmlMarkerCheck):
    """Represent `CoinbaseHomepageCheck`."""

    check_key = "coinbase_homepage"
    endpoint_key = "https://www.coinbase.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("coinbase",)


class CoinbaseDocsCheck(HtmlMarkerCheck):
    """Represent `CoinbaseDocsCheck`."""

    check_key = "coinbase_docs"
    endpoint_key = "https://docs.cdp.coinbase.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.1
    expected_markers = ("coinbase",)


class CoinbaseServiceChecker(BaseServiceChecker):
    """Represent `CoinbaseServiceChecker`."""

    service_key = "coinbase"
    logo_url = "https://img.logo.dev/coinbase.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.coinbase.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            CoinbaseStatusApiCheck(),
            CoinbaseSummaryApiCheck(),
            CoinbaseStatusPageCheck(),
            CoinbaseHomepageCheck(),
            CoinbaseDocsCheck(),
        ]

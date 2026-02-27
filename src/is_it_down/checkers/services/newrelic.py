"""Provide functionality for `is_it_down.checkers.services.newrelic`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck, StatuspageStatusCheck, StatuspageSummaryCheck


class NewRelicStatusApiCheck(StatuspageStatusCheck):
    """Represent `NewRelicStatusApiCheck`."""

    check_key = "newrelic_status_api"
    endpoint_key = "https://status.newrelic.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class NewRelicSummaryApiCheck(StatuspageSummaryCheck):
    """Represent `NewRelicSummaryApiCheck`."""

    check_key = "newrelic_summary_api"
    endpoint_key = "https://status.newrelic.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class NewRelicStatusPageCheck(HtmlMarkerCheck):
    """Represent `NewRelicStatusPageCheck`."""

    check_key = "newrelic_status_page"
    endpoint_key = "https://status.newrelic.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("new relic",)


class NewRelicHomepageCheck(HtmlMarkerCheck):
    """Represent `NewRelicHomepageCheck`."""

    check_key = "newrelic_homepage"
    endpoint_key = "https://newrelic.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("new relic",)


class NewRelicDocsCheck(HtmlMarkerCheck):
    """Represent `NewRelicDocsCheck`."""

    check_key = "newrelic_docs"
    endpoint_key = "https://docs.newrelic.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("new relic",)


class NewRelicServiceChecker(BaseServiceChecker):
    """Represent `NewRelicServiceChecker`."""

    service_key = "newrelic"
    logo_url = "https://img.logo.dev/newrelic.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.newrelic.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            NewRelicStatusApiCheck(),
            NewRelicSummaryApiCheck(),
            NewRelicStatusPageCheck(),
            NewRelicHomepageCheck(),
            NewRelicDocsCheck(),
        ]

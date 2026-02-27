"""Provide functionality for `is_it_down.checkers.services.elastic`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck, StatuspageStatusCheck, StatuspageSummaryCheck


class ElasticStatusApiCheck(StatuspageStatusCheck):
    """Represent `ElasticStatusApiCheck`."""

    check_key = "elastic_status_api"
    endpoint_key = "https://status.elastic.co/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class ElasticSummaryApiCheck(StatuspageSummaryCheck):
    """Represent `ElasticSummaryApiCheck`."""

    check_key = "elastic_summary_api"
    endpoint_key = "https://status.elastic.co/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class ElasticStatusPageCheck(HtmlMarkerCheck):
    """Represent `ElasticStatusPageCheck`."""

    check_key = "elastic_status_page"
    endpoint_key = "https://status.elastic.co/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("status",)


class ElasticHomepageCheck(HtmlMarkerCheck):
    """Represent `ElasticHomepageCheck`."""

    check_key = "elastic_homepage"
    endpoint_key = "https://www.elastic.co/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("elastic",)


class ElasticDocsCheck(HtmlMarkerCheck):
    """Represent `ElasticDocsCheck`."""

    check_key = "elastic_docs"
    endpoint_key = "https://www.elastic.co/docs"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.1
    expected_markers = ("elastic",)


class ElasticServiceChecker(BaseServiceChecker):
    """Represent `ElasticServiceChecker`."""

    service_key = "elastic"
    logo_url = "https://img.logo.dev/elastic.co?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.elastic.co/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            ElasticStatusApiCheck(),
            ElasticSummaryApiCheck(),
            ElasticStatusPageCheck(),
            ElasticHomepageCheck(),
            ElasticDocsCheck(),
        ]

"""Provide functionality for `is_it_down.checkers.services.confluent`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck, StatuspageStatusCheck, StatuspageSummaryCheck


class ConfluentStatusApiCheck(StatuspageStatusCheck):
    """Represent `ConfluentStatusApiCheck`."""

    check_key = "confluent_status_api"
    endpoint_key = "https://status.confluent.cloud/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class ConfluentSummaryApiCheck(StatuspageSummaryCheck):
    """Represent `ConfluentSummaryApiCheck`."""

    check_key = "confluent_summary_api"
    endpoint_key = "https://status.confluent.cloud/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class ConfluentStatusPageCheck(HtmlMarkerCheck):
    """Represent `ConfluentStatusPageCheck`."""

    check_key = "confluent_status_page"
    endpoint_key = "https://status.confluent.cloud/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("confluent",)


class ConfluentHomepageCheck(HtmlMarkerCheck):
    """Represent `ConfluentHomepageCheck`."""

    check_key = "confluent_homepage"
    endpoint_key = "https://www.confluent.io/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("confluent",)


class ConfluentDocsCheck(HtmlMarkerCheck):
    """Represent `ConfluentDocsCheck`."""

    check_key = "confluent_docs"
    endpoint_key = "https://docs.confluent.io/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("confluent",)


class ConfluentServiceChecker(BaseServiceChecker):
    """Represent `ConfluentServiceChecker`."""

    service_key = "confluent"
    logo_url = "https://img.logo.dev/confluent.io?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.confluent.cloud/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            ConfluentStatusApiCheck(),
            ConfluentSummaryApiCheck(),
            ConfluentStatusPageCheck(),
            ConfluentHomepageCheck(),
            ConfluentDocsCheck(),
        ]

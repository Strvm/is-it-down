"""Provide functionality for `is_it_down.checkers.services.mongodb`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck, StatuspageStatusCheck, StatuspageSummaryCheck


class MongoDBStatusApiCheck(StatuspageStatusCheck):
    """Represent `MongoDBStatusApiCheck`."""

    check_key = "mongodb_status_api"
    endpoint_key = "https://status.mongodb.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class MongoDBSummaryApiCheck(StatuspageSummaryCheck):
    """Represent `MongoDBSummaryApiCheck`."""

    check_key = "mongodb_summary_api"
    endpoint_key = "https://status.mongodb.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class MongoDBStatusPageCheck(HtmlMarkerCheck):
    """Represent `MongoDBStatusPageCheck`."""

    check_key = "mongodb_status_page"
    endpoint_key = "https://status.mongodb.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("status",)


class MongoDBHomepageCheck(HtmlMarkerCheck):
    """Represent `MongoDBHomepageCheck`."""

    check_key = "mongodb_homepage"
    endpoint_key = "https://www.mongodb.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("mongodb",)


class MongoDBDocsCheck(HtmlMarkerCheck):
    """Represent `MongoDBDocsCheck`."""

    check_key = "mongodb_docs"
    endpoint_key = "https://www.mongodb.com/docs/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.1
    expected_markers = ("mongodb",)


class MongoDBServiceChecker(BaseServiceChecker):
    """Represent `MongoDBServiceChecker`."""

    service_key = "mongodb"
    logo_url = "https://img.logo.dev/mongodb.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.mongodb.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            MongoDBStatusApiCheck(),
            MongoDBSummaryApiCheck(),
            MongoDBStatusPageCheck(),
            MongoDBHomepageCheck(),
            MongoDBDocsCheck(),
        ]

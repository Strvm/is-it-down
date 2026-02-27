"""Provide functionality for `is_it_down.checkers.services.contentful`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck, StatuspageStatusCheck, StatuspageSummaryCheck


class ContentfulStatusApiCheck(StatuspageStatusCheck):
    """Represent `ContentfulStatusApiCheck`."""

    check_key = "contentful_status_api"
    endpoint_key = "https://status.contentful.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class ContentfulSummaryApiCheck(StatuspageSummaryCheck):
    """Represent `ContentfulSummaryApiCheck`."""

    check_key = "contentful_summary_api"
    endpoint_key = "https://status.contentful.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class ContentfulStatusPageCheck(HtmlMarkerCheck):
    """Represent `ContentfulStatusPageCheck`."""

    check_key = "contentful_status_page"
    endpoint_key = "https://status.contentful.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("status",)


class ContentfulHomepageCheck(HtmlMarkerCheck):
    """Represent `ContentfulHomepageCheck`."""

    check_key = "contentful_homepage"
    endpoint_key = "https://www.contentful.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("contentful",)


class ContentfulDocsCheck(HtmlMarkerCheck):
    """Represent `ContentfulDocsCheck`."""

    check_key = "contentful_docs"
    endpoint_key = "https://www.contentful.com/developers/docs/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.1
    expected_markers = ("contentful",)


class ContentfulServiceChecker(BaseServiceChecker):
    """Represent `ContentfulServiceChecker`."""

    service_key = "contentful"
    logo_url = "https://img.logo.dev/contentful.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.contentful.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            ContentfulStatusApiCheck(),
            ContentfulSummaryApiCheck(),
            ContentfulStatusPageCheck(),
            ContentfulHomepageCheck(),
            ContentfulDocsCheck(),
        ]

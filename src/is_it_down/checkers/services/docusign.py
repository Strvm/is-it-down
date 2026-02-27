"""Provide functionality for `is_it_down.checkers.services.docusign`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck, StatuspageStatusCheck, StatuspageSummaryCheck


class DocuSignStatusApiCheck(StatuspageStatusCheck):
    """Represent `DocuSignStatusApiCheck`."""

    check_key = "docusign_status_api"
    endpoint_key = "https://status.docusign.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class DocuSignSummaryApiCheck(StatuspageSummaryCheck):
    """Represent `DocuSignSummaryApiCheck`."""

    check_key = "docusign_summary_api"
    endpoint_key = "https://status.docusign.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class DocuSignStatusPageCheck(HtmlMarkerCheck):
    """Represent `DocuSignStatusPageCheck`."""

    check_key = "docusign_status_page"
    endpoint_key = "https://status.docusign.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("docusign",)


class DocuSignHomepageCheck(HtmlMarkerCheck):
    """Represent `DocuSignHomepageCheck`."""

    check_key = "docusign_homepage"
    endpoint_key = "https://www.docusign.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("docusign",)


class DocuSignDevelopersCheck(HtmlMarkerCheck):
    """Represent `DocuSignDevelopersCheck`."""

    check_key = "docusign_developers"
    endpoint_key = "https://developers.docusign.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("docusign",)


class DocuSignServiceChecker(BaseServiceChecker):
    """Represent `DocuSignServiceChecker`."""

    service_key = "docusign"
    logo_url = "https://img.logo.dev/docusign.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.docusign.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            DocuSignStatusApiCheck(),
            DocuSignSummaryApiCheck(),
            DocuSignStatusPageCheck(),
            DocuSignHomepageCheck(),
            DocuSignDevelopersCheck(),
        ]

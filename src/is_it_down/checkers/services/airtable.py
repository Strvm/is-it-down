"""Provide functionality for `is_it_down.checkers.services.airtable`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class AirtableStatusPageCheck(HtmlMarkerCheck):
    """Represent `AirtableStatusPageCheck`."""

    check_key = "airtable_status_page"
    endpoint_key = "https://status.airtable.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("airtable",)


class AirtableHomepageCheck(HtmlMarkerCheck):
    """Represent `AirtableHomepageCheck`."""

    check_key = "airtable_homepage"
    endpoint_key = "https://www.airtable.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("airtable",)


class AirtableDevelopersCheck(HtmlMarkerCheck):
    """Represent `AirtableDevelopersCheck`."""

    check_key = "airtable_developers"
    endpoint_key = "https://airtable.com/developers/web/api/introduction"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("airtable",)


class AirtableSupportCheck(HtmlMarkerCheck):
    """Represent `AirtableSupportCheck`."""

    check_key = "airtable_support"
    endpoint_key = "https://support.airtable.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("airtable",)


class AirtableCommunityCheck(HtmlMarkerCheck):
    """Represent `AirtableCommunityCheck`."""

    check_key = "airtable_community"
    endpoint_key = "https://community.airtable.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("airtable",)


class AirtableServiceChecker(BaseServiceChecker):
    """Represent `AirtableServiceChecker`."""

    service_key = "airtable"
    logo_url = "https://img.logo.dev/airtable.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.airtable.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            AirtableStatusPageCheck(),
            AirtableHomepageCheck(),
            AirtableDevelopersCheck(),
            AirtableSupportCheck(),
            AirtableCommunityCheck(),
        ]

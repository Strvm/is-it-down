"""Provide functionality for `is_it_down.checkers.services.salesforce`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class SalesforceStatusPageCheck(HtmlMarkerCheck):
    """Represent `SalesforceStatusPageCheck`."""

    check_key = "salesforce_status_page"
    endpoint_key = "https://status.salesforce.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("salesforce",)


class SalesforceHomepageCheck(HtmlMarkerCheck):
    """Represent `SalesforceHomepageCheck`."""

    check_key = "salesforce_homepage"
    endpoint_key = "https://www.salesforce.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("salesforce",)


class SalesforceDeveloperCheck(HtmlMarkerCheck):
    """Represent `SalesforceDeveloperCheck`."""

    check_key = "salesforce_developer"
    endpoint_key = "https://developer.salesforce.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("salesforce",)


class SalesforceHelpCheck(HtmlMarkerCheck):
    """Represent `SalesforceHelpCheck`."""

    check_key = "salesforce_help"
    endpoint_key = "https://help.salesforce.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("salesforce",)


class SalesforceTrailheadCheck(HtmlMarkerCheck):
    """Represent `SalesforceTrailheadCheck`."""

    check_key = "salesforce_trailhead"
    endpoint_key = "https://trailhead.salesforce.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("salesforce",)


class SalesforceServiceChecker(BaseServiceChecker):
    """Represent `SalesforceServiceChecker`."""

    service_key = "salesforce"
    logo_url = "https://img.logo.dev/salesforce.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.salesforce.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            SalesforceStatusPageCheck(),
            SalesforceHomepageCheck(),
            SalesforceDeveloperCheck(),
            SalesforceHelpCheck(),
            SalesforceTrailheadCheck(),
        ]

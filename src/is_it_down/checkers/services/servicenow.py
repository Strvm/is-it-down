"""Provide functionality for `is_it_down.checkers.services.servicenow`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class ServiceNowCommunityCheck(HtmlMarkerCheck):
    """Represent `ServiceNowCommunityCheck`."""

    check_key = "servicenow_community"
    endpoint_key = "https://community.servicenow.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("servicenow",)


class ServiceNowDocsCheck(HtmlMarkerCheck):
    """Represent `ServiceNowDocsCheck`."""

    check_key = "servicenow_docs"
    endpoint_key = "https://docs.servicenow.com/en-US/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("servicenow",)


class ServiceNowDeveloperCheck(HtmlMarkerCheck):
    """Represent `ServiceNowDeveloperCheck`."""

    check_key = "servicenow_developer"
    endpoint_key = "https://developer.servicenow.com/dev.do"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("servicenow",)


class ServiceNowSupportCheck(HtmlMarkerCheck):
    """Represent `ServiceNowSupportCheck`."""

    check_key = "servicenow_support"
    endpoint_key = "https://support.servicenow.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("servicenow",)


class ServiceNowStoreCheck(HtmlMarkerCheck):
    """Represent `ServiceNowStoreCheck`."""

    check_key = "servicenow_store"
    endpoint_key = "https://store.servicenow.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("servicenow",)


class ServiceNowServiceChecker(BaseServiceChecker):
    """Represent `ServiceNowServiceChecker`."""

    service_key = "servicenow"
    logo_url = "https://img.logo.dev/servicenow.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.servicenow.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            ServiceNowCommunityCheck(),
            ServiceNowDocsCheck(),
            ServiceNowDeveloperCheck(),
            ServiceNowSupportCheck(),
            ServiceNowStoreCheck(),
        ]

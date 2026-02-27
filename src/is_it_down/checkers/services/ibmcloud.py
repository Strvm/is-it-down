"""Provide functionality for `is_it_down.checkers.services.ibmcloud`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class IBMCloudStatusPageCheck(HtmlMarkerCheck):
    """Represent `IBMCloudStatusPageCheck`."""

    check_key = "ibmcloud_status_page"
    endpoint_key = "https://cloud.ibm.com/status"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("ibm",)


class IBMCloudHomepageCheck(HtmlMarkerCheck):
    """Represent `IBMCloudHomepageCheck`."""

    check_key = "ibmcloud_homepage"
    endpoint_key = "https://www.ibm.com/cloud"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("ibm",)


class IBMCloudDocsCheck(HtmlMarkerCheck):
    """Represent `IBMCloudDocsCheck`."""

    check_key = "ibmcloud_docs"
    endpoint_key = "https://cloud.ibm.com/docs"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("ibm",)


class IBMCloudDeveloperCheck(HtmlMarkerCheck):
    """Represent `IBMCloudDeveloperCheck`."""

    check_key = "ibmcloud_developer"
    endpoint_key = "https://developer.ibm.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("ibm",)


class IBMCloudSupportCheck(HtmlMarkerCheck):
    """Represent `IBMCloudSupportCheck`."""

    check_key = "ibmcloud_support"
    endpoint_key = "https://www.ibm.com/support"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("ibm",)


class IBMCloudServiceChecker(BaseServiceChecker):
    """Represent `IBMCloudServiceChecker`."""

    service_key = "ibmcloud"
    logo_url = "https://img.logo.dev/ibm.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://cloud.ibm.com/status"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            IBMCloudStatusPageCheck(),
            IBMCloudHomepageCheck(),
            IBMCloudDocsCheck(),
            IBMCloudDeveloperCheck(),
            IBMCloudSupportCheck(),
        ]

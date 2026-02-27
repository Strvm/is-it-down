"""Provide functionality for `is_it_down.checkers.services.oraclecloud`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class OracleCloudStatusPageCheck(HtmlMarkerCheck):
    """Represent `OracleCloudStatusPageCheck`."""

    check_key = "oraclecloud_status_page"
    endpoint_key = "https://ocistatus.oraclecloud.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("oci",)


class OracleCloudDocsCheck(HtmlMarkerCheck):
    """Represent `OracleCloudDocsCheck`."""

    check_key = "oraclecloud_docs"
    endpoint_key = "https://docs.oracle.com/en-us/iaas/Content/home.htm"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("oracle",)


class OracleCloudSignInCheck(HtmlMarkerCheck):
    """Represent `OracleCloudSignInCheck`."""

    check_key = "oraclecloud_sign_in"
    endpoint_key = "https://www.oracle.com/cloud/sign-in.html"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("oracle",)


class OracleCloudSupportCheck(HtmlMarkerCheck):
    """Represent `OracleCloudSupportCheck`."""

    check_key = "oraclecloud_support"
    endpoint_key = "https://www.oracle.com/support/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("oracle",)


class OracleCloudFreeTierCheck(HtmlMarkerCheck):
    """Represent `OracleCloudFreeTierCheck`."""

    check_key = "oraclecloud_free_tier"
    endpoint_key = "https://www.oracle.com/cloud/free/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("oracle",)


class OracleCloudServiceChecker(BaseServiceChecker):
    """Represent `OracleCloudServiceChecker`."""

    service_key = "oraclecloud"
    logo_url = "https://img.logo.dev/oracle.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://ocistatus.oraclecloud.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            OracleCloudStatusPageCheck(),
            OracleCloudDocsCheck(),
            OracleCloudSignInCheck(),
            OracleCloudSupportCheck(),
            OracleCloudFreeTierCheck(),
        ]

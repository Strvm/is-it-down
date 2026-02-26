"""Provide functionality for `is_it_down.checkers.services.coda`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class CodaStatusPageCheck(HtmlMarkerCheck):
    """Represent `CodaStatusPageCheck`."""

    check_key = "coda_status_page"
    endpoint_key = "https://status.coda.io/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("coda",)


class CodaHomepageCheck(HtmlMarkerCheck):
    """Represent `CodaHomepageCheck`."""

    check_key = "coda_homepage"
    endpoint_key = "https://coda.io/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("coda",)


class CodaDevelopersCheck(HtmlMarkerCheck):
    """Represent `CodaDevelopersCheck`."""

    check_key = "coda_developers"
    endpoint_key = "https://coda.io/developers/apis/v1"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("coda",)


class CodaHelpCheck(HtmlMarkerCheck):
    """Represent `CodaHelpCheck`."""

    check_key = "coda_help"
    endpoint_key = "https://help.coda.io/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("coda",)


class CodaCommunityCheck(HtmlMarkerCheck):
    """Represent `CodaCommunityCheck`."""

    check_key = "coda_community"
    endpoint_key = "https://community.coda.io/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("coda",)


class CodaServiceChecker(BaseServiceChecker):
    """Represent `CodaServiceChecker`."""

    service_key = "coda"
    logo_url = "https://img.logo.dev/coda.io?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.coda.io/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            CodaStatusPageCheck(),
            CodaHomepageCheck(),
            CodaDevelopersCheck(),
            CodaHelpCheck(),
            CodaCommunityCheck(),
        ]

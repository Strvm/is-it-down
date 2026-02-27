"""Provide functionality for `is_it_down.checkers.services.akamai`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck, StatuspageStatusCheck, StatuspageSummaryCheck


class AkamaiStatusApiCheck(StatuspageStatusCheck):
    """Represent `AkamaiStatusApiCheck`."""

    check_key = "akamai_status_api"
    endpoint_key = "https://www.akamaistatus.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class AkamaiSummaryApiCheck(StatuspageSummaryCheck):
    """Represent `AkamaiSummaryApiCheck`."""

    check_key = "akamai_summary_api"
    endpoint_key = "https://www.akamaistatus.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class AkamaiStatusPageCheck(HtmlMarkerCheck):
    """Represent `AkamaiStatusPageCheck`."""

    check_key = "akamai_status_page"
    endpoint_key = "https://www.akamaistatus.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("akamai",)


class AkamaiDeveloperCheck(HtmlMarkerCheck):
    """Represent `AkamaiDeveloperCheck`."""

    check_key = "akamai_developer"
    endpoint_key = "https://developer.akamai.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("akamai",)


class AkamaiTechdocsCheck(HtmlMarkerCheck):
    """Represent `AkamaiTechdocsCheck`."""

    check_key = "akamai_techdocs"
    endpoint_key = "https://techdocs.akamai.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("akamai",)


class AkamaiServiceChecker(BaseServiceChecker):
    """Represent `AkamaiServiceChecker`."""

    service_key = "akamai"
    logo_url = "https://img.logo.dev/akamai.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://www.akamaistatus.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            AkamaiStatusApiCheck(),
            AkamaiSummaryApiCheck(),
            AkamaiStatusPageCheck(),
            AkamaiDeveloperCheck(),
            AkamaiTechdocsCheck(),
        ]

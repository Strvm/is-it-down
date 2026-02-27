"""Provide functionality for `is_it_down.checkers.services.amplitude`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck, StatuspageStatusCheck, StatuspageSummaryCheck


class AmplitudeStatusApiCheck(StatuspageStatusCheck):
    """Represent `AmplitudeStatusApiCheck`."""

    check_key = "amplitude_status_api"
    endpoint_key = "https://status.amplitude.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class AmplitudeSummaryApiCheck(StatuspageSummaryCheck):
    """Represent `AmplitudeSummaryApiCheck`."""

    check_key = "amplitude_summary_api"
    endpoint_key = "https://status.amplitude.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class AmplitudeStatusPageCheck(HtmlMarkerCheck):
    """Represent `AmplitudeStatusPageCheck`."""

    check_key = "amplitude_status_page"
    endpoint_key = "https://status.amplitude.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("amplitude",)


class AmplitudeHomepageCheck(HtmlMarkerCheck):
    """Represent `AmplitudeHomepageCheck`."""

    check_key = "amplitude_homepage"
    endpoint_key = "https://amplitude.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("amplitude",)


class AmplitudeDocsCheck(HtmlMarkerCheck):
    """Represent `AmplitudeDocsCheck`."""

    check_key = "amplitude_docs"
    endpoint_key = "https://amplitude.com/docs"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("amplitude",)


class AmplitudeServiceChecker(BaseServiceChecker):
    """Represent `AmplitudeServiceChecker`."""

    service_key = "amplitude"
    logo_url = "https://img.logo.dev/amplitude.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.amplitude.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            AmplitudeStatusApiCheck(),
            AmplitudeSummaryApiCheck(),
            AmplitudeStatusPageCheck(),
            AmplitudeHomepageCheck(),
            AmplitudeDocsCheck(),
        ]

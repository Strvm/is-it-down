"""Provide functionality for `is_it_down.checkers.services.mixpanel`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck, StatuspageStatusCheck, StatuspageSummaryCheck


class MixpanelStatusApiCheck(StatuspageStatusCheck):
    """Represent `MixpanelStatusApiCheck`."""

    check_key = "mixpanel_status_api"
    endpoint_key = "https://status.mixpanel.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class MixpanelSummaryApiCheck(StatuspageSummaryCheck):
    """Represent `MixpanelSummaryApiCheck`."""

    check_key = "mixpanel_summary_api"
    endpoint_key = "https://status.mixpanel.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class MixpanelStatusPageCheck(HtmlMarkerCheck):
    """Represent `MixpanelStatusPageCheck`."""

    check_key = "mixpanel_status_page"
    endpoint_key = "https://status.mixpanel.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("mixpanel",)


class MixpanelHomepageCheck(HtmlMarkerCheck):
    """Represent `MixpanelHomepageCheck`."""

    check_key = "mixpanel_homepage"
    endpoint_key = "https://mixpanel.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("mixpanel",)


class MixpanelDocsCheck(HtmlMarkerCheck):
    """Represent `MixpanelDocsCheck`."""

    check_key = "mixpanel_docs"
    endpoint_key = "https://docs.mixpanel.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("mixpanel",)


class MixpanelServiceChecker(BaseServiceChecker):
    """Represent `MixpanelServiceChecker`."""

    service_key = "mixpanel"
    logo_url = "https://img.logo.dev/mixpanel.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.mixpanel.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            MixpanelStatusApiCheck(),
            MixpanelSummaryApiCheck(),
            MixpanelStatusPageCheck(),
            MixpanelHomepageCheck(),
            MixpanelDocsCheck(),
        ]

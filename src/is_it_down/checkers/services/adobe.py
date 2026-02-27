"""Provide functionality for `is_it_down.checkers.services.adobe`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class AdobeStatusPageCheck(HtmlMarkerCheck):
    """Represent `AdobeStatusPageCheck`."""

    check_key = "adobe_status_page"
    endpoint_key = "https://status.adobe.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("adobe",)


class AdobeHomepageCheck(HtmlMarkerCheck):
    """Represent `AdobeHomepageCheck`."""

    check_key = "adobe_homepage"
    endpoint_key = "https://www.adobe.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("adobe",)


class AdobeDeveloperCheck(HtmlMarkerCheck):
    """Represent `AdobeDeveloperCheck`."""

    check_key = "adobe_developer"
    endpoint_key = "https://developer.adobe.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("adobe",)


class AdobeHelpCheck(HtmlMarkerCheck):
    """Represent `AdobeHelpCheck`."""

    check_key = "adobe_help"
    endpoint_key = "https://helpx.adobe.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("adobe",)


class AdobeExperienceLeagueCheck(HtmlMarkerCheck):
    """Represent `AdobeExperienceLeagueCheck`."""

    check_key = "adobe_experience_league"
    endpoint_key = "https://experienceleague.adobe.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("adobe",)


class AdobeServiceChecker(BaseServiceChecker):
    """Represent `AdobeServiceChecker`."""

    service_key = "adobe"
    logo_url = "https://img.logo.dev/adobe.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.adobe.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            AdobeStatusPageCheck(),
            AdobeHomepageCheck(),
            AdobeDeveloperCheck(),
            AdobeHelpCheck(),
            AdobeExperienceLeagueCheck(),
        ]

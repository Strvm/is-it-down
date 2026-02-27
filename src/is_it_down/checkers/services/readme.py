"""Provide functionality for `is_it_down.checkers.services.readme`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class ReadmeHomepageCheck(HtmlMarkerCheck):
    """Represent `ReadmeHomepageCheck`."""

    check_key = "readme_home_page"
    endpoint_key = "https://readme.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("readme",)


class ReadmeDocsCheck(HtmlMarkerCheck):
    """Represent `ReadmeDocsCheck`."""

    check_key = "readme_docs"
    endpoint_key = "https://docs.readme.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("readme",)


class ReadmeLoginCheck(HtmlMarkerCheck):
    """Represent `ReadmeLoginCheck`."""

    check_key = "readme_login"
    endpoint_key = "https://dash.readme.com/login"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("readme",)


class ReadmeApiReferenceCheck(HtmlMarkerCheck):
    """Represent `ReadmeApiReferenceCheck`."""

    check_key = "readme_apireference"
    endpoint_key = "https://docs.readme.com/main/docs"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("readme",)


class ReadmeStatusPageCheck(HtmlMarkerCheck):
    """Represent `ReadmeStatusPageCheck`."""

    check_key = "readme_status_page"
    endpoint_key = "https://status.readme.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("status",)


class ReadmeServiceChecker(BaseServiceChecker):
    """Represent `ReadmeServiceChecker`."""

    service_key = "readme"
    logo_url = "https://img.logo.dev/readme.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.readme.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            ReadmeHomepageCheck(),
            ReadmeDocsCheck(),
            ReadmeLoginCheck(),
            ReadmeApiReferenceCheck(),
            ReadmeStatusPageCheck(),
        ]

"""Provide functionality for `is_it_down.checkers.services.xing`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class XingHomepageCheck(HtmlMarkerCheck):
    """Represent `XingHomepageCheck`."""

    check_key = "xing_home_page"
    endpoint_key = "https://www.xing.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("xing",)


class XingJobsCheck(HtmlMarkerCheck):
    """Represent `XingJobsCheck`."""

    check_key = "xing_jobs"
    endpoint_key = "https://www.xing.com/jobs"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("xing",)


class XingNewsCheck(HtmlMarkerCheck):
    """Represent `XingNewsCheck`."""

    check_key = "xing_news"
    endpoint_key = "https://www.xing.com/news"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("xing",)


class XingHelpCheck(HtmlMarkerCheck):
    """Represent `XingHelpCheck`."""

    check_key = "xing_help"
    endpoint_key = "https://help.xing.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("xing",)


class XingLoginCheck(HtmlMarkerCheck):
    """Represent `XingLoginCheck`."""

    check_key = "xing_login"
    endpoint_key = "https://login.xing.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("xing",)


class XingServiceChecker(BaseServiceChecker):
    """Represent `XingServiceChecker`."""

    service_key = "xing"
    logo_url = "https://img.logo.dev/xing.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://www.xing.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            XingHomepageCheck(),
            XingJobsCheck(),
            XingNewsCheck(),
            XingHelpCheck(),
            XingLoginCheck(),
        ]

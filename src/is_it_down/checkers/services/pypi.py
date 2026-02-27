"""Provide functionality for `is_it_down.checkers.services.pypi`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class PyPIHomepageCheck(HtmlMarkerCheck):
    """Represent `PyPIHomepageCheck`."""

    check_key = "pypi_home_page"
    endpoint_key = "https://pypi.org/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("pypi",)


class PyPIProjectPageCheck(HtmlMarkerCheck):
    """Represent `PyPIProjectPageCheck`."""

    check_key = "pypi_project_page"
    endpoint_key = "https://pypi.org/project/pip/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("python",)


class PyPIHelpCheck(HtmlMarkerCheck):
    """Represent `PyPIHelpCheck`."""

    check_key = "pypi_help"
    endpoint_key = "https://pypi.org/help/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("help",)


class PyPIStatsCheck(HtmlMarkerCheck):
    """Represent `PyPIStatsCheck`."""

    check_key = "pypi_stats"
    endpoint_key = "https://pypistats.org/packages/pip"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("pypi",)


class PyPIStatusPageCheck(HtmlMarkerCheck):
    """Represent `PyPIStatusPageCheck`."""

    check_key = "pypi_status_page"
    endpoint_key = "https://status.python.org/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("python",)


class PyPIServiceChecker(BaseServiceChecker):
    """Represent `PyPIServiceChecker`."""

    service_key = "pypi"
    logo_url = "https://img.logo.dev/pypi.org?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.python.org/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            PyPIHomepageCheck(),
            PyPIProjectPageCheck(),
            PyPIHelpCheck(),
            PyPIStatsCheck(),
            PyPIStatusPageCheck(),
        ]

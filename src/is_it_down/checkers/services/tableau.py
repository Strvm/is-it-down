"""Provide functionality for `is_it_down.checkers.services.tableau`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class TableauTrustPageCheck(HtmlMarkerCheck):
    """Represent `TableauTrustPageCheck`."""

    check_key = "tableau_trust_page"
    endpoint_key = "https://trust.tableau.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("tableau",)


class TableauHomepageCheck(HtmlMarkerCheck):
    """Represent `TableauHomepageCheck`."""

    check_key = "tableau_homepage"
    endpoint_key = "https://www.tableau.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("tableau",)


class TableauHelpCheck(HtmlMarkerCheck):
    """Represent `TableauHelpCheck`."""

    check_key = "tableau_help"
    endpoint_key = "https://help.tableau.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("tableau",)


class TableauSupportCheck(HtmlMarkerCheck):
    """Represent `TableauSupportCheck`."""

    check_key = "tableau_support"
    endpoint_key = "https://www.tableau.com/support"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("tableau",)


class TableauDeveloperCheck(HtmlMarkerCheck):
    """Represent `TableauDeveloperCheck`."""

    check_key = "tableau_developer"
    endpoint_key = "https://www.tableau.com/developer"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("tableau",)


class TableauServiceChecker(BaseServiceChecker):
    """Represent `TableauServiceChecker`."""

    service_key = "tableau"
    logo_url = "https://img.logo.dev/tableau.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://trust.tableau.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            TableauTrustPageCheck(),
            TableauHomepageCheck(),
            TableauHelpCheck(),
            TableauSupportCheck(),
            TableauDeveloperCheck(),
        ]

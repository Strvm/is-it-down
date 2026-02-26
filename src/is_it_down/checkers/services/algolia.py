"""Provide functionality for `is_it_down.checkers.services.algolia`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class AlgoliaStatusPageCheck(HtmlMarkerCheck):
    """Represent `AlgoliaStatusPageCheck`."""

    check_key = "algolia_status_page"
    endpoint_key = "https://status.algolia.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("algolia",)


class AlgoliaHomepageCheck(HtmlMarkerCheck):
    """Represent `AlgoliaHomepageCheck`."""

    check_key = "algolia_homepage"
    endpoint_key = "https://www.algolia.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("algolia",)


class AlgoliaDocsCheck(HtmlMarkerCheck):
    """Represent `AlgoliaDocsCheck`."""

    check_key = "algolia_docs"
    endpoint_key = "https://www.algolia.com/doc/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("algolia",)


class AlgoliaSupportCheck(HtmlMarkerCheck):
    """Represent `AlgoliaSupportCheck`."""

    check_key = "algolia_support"
    endpoint_key = "https://support.algolia.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("algolia",)


class AlgoliaCustomersCheck(HtmlMarkerCheck):
    """Represent `AlgoliaCustomersCheck`."""

    check_key = "algolia_customers"
    endpoint_key = "https://www.algolia.com/customers/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("algolia",)


class AlgoliaServiceChecker(BaseServiceChecker):
    """Represent `AlgoliaServiceChecker`."""

    service_key = "algolia"
    logo_url = "https://img.logo.dev/algolia.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.algolia.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            AlgoliaStatusPageCheck(),
            AlgoliaHomepageCheck(),
            AlgoliaDocsCheck(),
            AlgoliaSupportCheck(),
            AlgoliaCustomersCheck(),
        ]

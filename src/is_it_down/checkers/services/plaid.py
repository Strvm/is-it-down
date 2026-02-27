"""Provide functionality for `is_it_down.checkers.services.plaid`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class PlaidStatusPageCheck(HtmlMarkerCheck):
    """Represent `PlaidStatusPageCheck`."""

    check_key = "plaid_status_page"
    endpoint_key = "https://status.plaid.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("plaid",)


class PlaidHomepageCheck(HtmlMarkerCheck):
    """Represent `PlaidHomepageCheck`."""

    check_key = "plaid_homepage"
    endpoint_key = "https://plaid.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("plaid",)


class PlaidDocsCheck(HtmlMarkerCheck):
    """Represent `PlaidDocsCheck`."""

    check_key = "plaid_docs"
    endpoint_key = "https://plaid.com/docs/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("plaid",)


class PlaidSupportCheck(HtmlMarkerCheck):
    """Represent `PlaidSupportCheck`."""

    check_key = "plaid_support"
    endpoint_key = "https://support.plaid.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("plaid",)


class PlaidBlogCheck(HtmlMarkerCheck):
    """Represent `PlaidBlogCheck`."""

    check_key = "plaid_blog"
    endpoint_key = "https://plaid.com/blog/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("plaid",)


class PlaidServiceChecker(BaseServiceChecker):
    """Represent `PlaidServiceChecker`."""

    service_key = "plaid"
    logo_url = "https://img.logo.dev/plaid.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.plaid.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            PlaidStatusPageCheck(),
            PlaidHomepageCheck(),
            PlaidDocsCheck(),
            PlaidSupportCheck(),
            PlaidBlogCheck(),
        ]

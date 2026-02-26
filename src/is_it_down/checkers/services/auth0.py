"""Provide functionality for `is_it_down.checkers.services.auth0`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class Auth0StatusPageCheck(HtmlMarkerCheck):
    """Represent `Auth0StatusPageCheck`."""

    check_key = "auth0_status_page"
    endpoint_key = "https://status.auth0.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("auth0",)


class Auth0HomepageCheck(HtmlMarkerCheck):
    """Represent `Auth0HomepageCheck`."""

    check_key = "auth0_homepage"
    endpoint_key = "https://auth0.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("auth0",)


class Auth0DocsCheck(HtmlMarkerCheck):
    """Represent `Auth0DocsCheck`."""

    check_key = "auth0_docs"
    endpoint_key = "https://auth0.com/docs"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("auth0",)


class Auth0CommunityCheck(HtmlMarkerCheck):
    """Represent `Auth0CommunityCheck`."""

    check_key = "auth0_community"
    endpoint_key = "https://community.auth0.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("auth0",)


class Auth0BlogCheck(HtmlMarkerCheck):
    """Represent `Auth0BlogCheck`."""

    check_key = "auth0_blog"
    endpoint_key = "https://auth0.com/blog/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("auth0",)


class Auth0ServiceChecker(BaseServiceChecker):
    """Represent `Auth0ServiceChecker`."""

    service_key = "auth0"
    logo_url = "https://img.logo.dev/auth0.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.auth0.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            Auth0StatusPageCheck(),
            Auth0HomepageCheck(),
            Auth0DocsCheck(),
            Auth0CommunityCheck(),
            Auth0BlogCheck(),
        ]

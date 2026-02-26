"""Provide functionality for `is_it_down.checkers.services.launchdarkly`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class LaunchDarklyStatusPageCheck(HtmlMarkerCheck):
    """Represent `LaunchDarklyStatusPageCheck`."""

    check_key = "launchdarkly_status_page"
    endpoint_key = "https://status.launchdarkly.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("launchdarkly",)


class LaunchDarklyHomepageCheck(HtmlMarkerCheck):
    """Represent `LaunchDarklyHomepageCheck`."""

    check_key = "launchdarkly_homepage"
    endpoint_key = "https://launchdarkly.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("launchdarkly",)


class LaunchDarklyDocsCheck(HtmlMarkerCheck):
    """Represent `LaunchDarklyDocsCheck`."""

    check_key = "launchdarkly_docs"
    endpoint_key = "https://docs.launchdarkly.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("launchdarkly",)


class LaunchDarklyBlogCheck(HtmlMarkerCheck):
    """Represent `LaunchDarklyBlogCheck`."""

    check_key = "launchdarkly_blog"
    endpoint_key = "https://launchdarkly.com/blog/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("launchdarkly",)


class LaunchDarklyResourcesCheck(HtmlMarkerCheck):
    """Represent `LaunchDarklyResourcesCheck`."""

    check_key = "launchdarkly_resources"
    endpoint_key = "https://launchdarkly.com/resources/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("launchdarkly",)


class LaunchDarklyServiceChecker(BaseServiceChecker):
    """Represent `LaunchDarklyServiceChecker`."""

    service_key = "launchdarkly"
    logo_url = "https://img.logo.dev/launchdarkly.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.launchdarkly.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            LaunchDarklyStatusPageCheck(),
            LaunchDarklyHomepageCheck(),
            LaunchDarklyDocsCheck(),
            LaunchDarklyBlogCheck(),
            LaunchDarklyResourcesCheck(),
        ]

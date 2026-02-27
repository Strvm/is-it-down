"""Provide functionality for `is_it_down.checkers.services.bugsnag`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class BugsnagStatusPageCheck(HtmlMarkerCheck):
    """Represent `BugsnagStatusPageCheck`."""

    check_key = "bugsnag_status_page"
    endpoint_key = "https://status.bugsnag.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("bugsnag",)


class BugsnagHomepageCheck(HtmlMarkerCheck):
    """Represent `BugsnagHomepageCheck`."""

    check_key = "bugsnag_homepage"
    endpoint_key = "https://www.bugsnag.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("bugsnag",)


class BugsnagDocsCheck(HtmlMarkerCheck):
    """Represent `BugsnagDocsCheck`."""

    check_key = "bugsnag_docs"
    endpoint_key = "https://docs.bugsnag.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("bugsnag",)


class BugsnagSupportCheck(HtmlMarkerCheck):
    """Represent `BugsnagSupportCheck`."""

    check_key = "bugsnag_support"
    endpoint_key = "https://support.bugsnag.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("bugsnag",)


class BugsnagBlogCheck(HtmlMarkerCheck):
    """Represent `BugsnagBlogCheck`."""

    check_key = "bugsnag_blog"
    endpoint_key = "https://www.bugsnag.com/blog"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("bugsnag",)


class BugsnagServiceChecker(BaseServiceChecker):
    """Represent `BugsnagServiceChecker`."""

    service_key = "bugsnag"
    logo_url = "https://img.logo.dev/bugsnag.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.bugsnag.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            BugsnagStatusPageCheck(),
            BugsnagHomepageCheck(),
            BugsnagDocsCheck(),
            BugsnagSupportCheck(),
            BugsnagBlogCheck(),
        ]

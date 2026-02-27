"""Provide functionality for `is_it_down.checkers.services.superset`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class SupersetHomepageCheck(HtmlMarkerCheck):
    """Represent `SupersetHomepageCheck`."""

    check_key = "superset_home_page"
    endpoint_key = "https://superset.apache.org/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("superset",)


class SupersetDocsCheck(HtmlMarkerCheck):
    """Represent `SupersetDocsCheck`."""

    check_key = "superset_docs"
    endpoint_key = "https://superset.apache.org/user-docs/intro"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("superset",)


class SupersetGithubCheck(HtmlMarkerCheck):
    """Represent `SupersetGithubCheck`."""

    check_key = "superset_github"
    endpoint_key = "https://github.com/apache/superset"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("superset",)


class SupersetSlackInfoCheck(HtmlMarkerCheck):
    """Represent `SupersetSlackInfoCheck`."""

    check_key = "superset_slackinfo"
    endpoint_key = "https://superset.apache.org/community"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("superset",)


class SupersetStatusPageCheck(HtmlMarkerCheck):
    """Represent `SupersetStatusPageCheck`."""

    check_key = "superset_status_page"
    endpoint_key = "https://superset.statuspage.io/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("status",)


class SupersetServiceChecker(BaseServiceChecker):
    """Represent `SupersetServiceChecker`."""

    service_key = "superset"
    logo_url = "https://img.logo.dev/superset.apache.org?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://superset.statuspage.io/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            SupersetHomepageCheck(),
            SupersetDocsCheck(),
            SupersetGithubCheck(),
            SupersetSlackInfoCheck(),
            SupersetStatusPageCheck(),
        ]

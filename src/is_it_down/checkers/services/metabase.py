"""Provide functionality for `is_it_down.checkers.services.metabase`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class MetabaseHomepageCheck(HtmlMarkerCheck):
    """Represent `MetabaseHomepageCheck`."""

    check_key = "metabase_home_page"
    endpoint_key = "https://www.metabase.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("metabase",)


class MetabaseDocsCheck(HtmlMarkerCheck):
    """Represent `MetabaseDocsCheck`."""

    check_key = "metabase_docs"
    endpoint_key = "https://www.metabase.com/docs/latest/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("metabase",)


class MetabaseCloudLoginCheck(HtmlMarkerCheck):
    """Represent `MetabaseCloudLoginCheck`."""

    check_key = "metabase_cloudlogin"
    endpoint_key = "https://www.metabase.com/cloud/login"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("metabase",)


class MetabaseGithubCheck(HtmlMarkerCheck):
    """Represent `MetabaseGithubCheck`."""

    check_key = "metabase_github"
    endpoint_key = "https://github.com/metabase/metabase"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("metabase",)


class MetabaseStatusPageCheck(HtmlMarkerCheck):
    """Represent `MetabaseStatusPageCheck`."""

    check_key = "metabase_status_page"
    endpoint_key = "https://status.metabase.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("status",)


class MetabaseServiceChecker(BaseServiceChecker):
    """Represent `MetabaseServiceChecker`."""

    service_key = "metabase"
    logo_url = "https://img.logo.dev/metabase.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.metabase.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            MetabaseHomepageCheck(),
            MetabaseDocsCheck(),
            MetabaseCloudLoginCheck(),
            MetabaseGithubCheck(),
            MetabaseStatusPageCheck(),
        ]

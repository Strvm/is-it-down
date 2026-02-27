"""Provide functionality for `is_it_down.checkers.services.snowplow`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class SnowplowStatusPageCheck(HtmlMarkerCheck):
    """Represent `SnowplowStatusPageCheck`."""

    check_key = "snowplow_status_page"
    endpoint_key = "https://status.snowplow.io/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("snowplow",)


class SnowplowHomepageCheck(HtmlMarkerCheck):
    """Represent `SnowplowHomepageCheck`."""

    check_key = "snowplow_homepage"
    endpoint_key = "https://snowplow.io/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("snowplow",)


class SnowplowDocsCheck(HtmlMarkerCheck):
    """Represent `SnowplowDocsCheck`."""

    check_key = "snowplow_docs"
    endpoint_key = "https://docs.snowplow.io/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("snowplow",)


class SnowplowSupportCheck(HtmlMarkerCheck):
    """Represent `SnowplowSupportCheck`."""

    check_key = "snowplow_support"
    endpoint_key = "https://support.snowplowanalytics.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("snowplow",)


class SnowplowBlogCheck(HtmlMarkerCheck):
    """Represent `SnowplowBlogCheck`."""

    check_key = "snowplow_blog"
    endpoint_key = "https://snowplow.io/blog/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("snowplow",)


class SnowplowServiceChecker(BaseServiceChecker):
    """Represent `SnowplowServiceChecker`."""

    service_key = "snowplow"
    logo_url = "https://img.logo.dev/snowplow.io?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.snowplow.io/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            SnowplowStatusPageCheck(),
            SnowplowHomepageCheck(),
            SnowplowDocsCheck(),
            SnowplowSupportCheck(),
            SnowplowBlogCheck(),
        ]

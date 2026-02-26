"""Provide functionality for `is_it_down.checkers.services.segment`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class SegmentStatusPageCheck(HtmlMarkerCheck):
    """Represent `SegmentStatusPageCheck`."""

    check_key = "segment_status_page"
    endpoint_key = "https://status.segment.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("segment",)


class SegmentHomepageCheck(HtmlMarkerCheck):
    """Represent `SegmentHomepageCheck`."""

    check_key = "segment_homepage"
    endpoint_key = "https://segment.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("segment",)


class SegmentDocsCheck(HtmlMarkerCheck):
    """Represent `SegmentDocsCheck`."""

    check_key = "segment_docs"
    endpoint_key = "https://segment.com/docs/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("segment",)


class SegmentBlogCheck(HtmlMarkerCheck):
    """Represent `SegmentBlogCheck`."""

    check_key = "segment_blog"
    endpoint_key = "https://segment.com/blog/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("segment",)


class SegmentCommunityCheck(HtmlMarkerCheck):
    """Represent `SegmentCommunityCheck`."""

    check_key = "segment_community"
    endpoint_key = "https://community.segment.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("segment",)


class SegmentServiceChecker(BaseServiceChecker):
    """Represent `SegmentServiceChecker`."""

    service_key = "segment"
    logo_url = "https://img.logo.dev/segment.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.segment.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            SegmentStatusPageCheck(),
            SegmentHomepageCheck(),
            SegmentDocsCheck(),
            SegmentBlogCheck(),
            SegmentCommunityCheck(),
        ]

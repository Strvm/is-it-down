"""Provide functionality for `is_it_down.checkers.services.elevenlabs`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class ElevenLabsStatusPageCheck(HtmlMarkerCheck):
    """Represent `ElevenLabsStatusPageCheck`."""

    check_key = "elevenlabs_status_page"
    endpoint_key = "https://status.elevenlabs.io/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("elevenlabs",)


class ElevenLabsHomepageCheck(HtmlMarkerCheck):
    """Represent `ElevenLabsHomepageCheck`."""

    check_key = "elevenlabs_homepage"
    endpoint_key = "https://elevenlabs.io/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("elevenlabs",)


class ElevenLabsDocsCheck(HtmlMarkerCheck):
    """Represent `ElevenLabsDocsCheck`."""

    check_key = "elevenlabs_docs"
    endpoint_key = "https://elevenlabs.io/docs"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("elevenlabs",)


class ElevenLabsSupportCheck(HtmlMarkerCheck):
    """Represent `ElevenLabsSupportCheck`."""

    check_key = "elevenlabs_support"
    endpoint_key = "https://help.elevenlabs.io/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("elevenlabs",)


class ElevenLabsBlogCheck(HtmlMarkerCheck):
    """Represent `ElevenLabsBlogCheck`."""

    check_key = "elevenlabs_blog"
    endpoint_key = "https://elevenlabs.io/blog"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("elevenlabs",)


class ElevenLabsServiceChecker(BaseServiceChecker):
    """Represent `ElevenLabsServiceChecker`."""

    service_key = "elevenlabs"
    logo_url = "https://img.logo.dev/elevenlabs.io?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.elevenlabs.io/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            ElevenLabsStatusPageCheck(),
            ElevenLabsHomepageCheck(),
            ElevenLabsDocsCheck(),
            ElevenLabsSupportCheck(),
            ElevenLabsBlogCheck(),
        ]

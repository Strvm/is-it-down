"""Provide functionality for `is_it_down.checkers.services.firebase`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class FirebaseStatusPageCheck(HtmlMarkerCheck):
    """Represent `FirebaseStatusPageCheck`."""

    check_key = "firebase_status_page"
    endpoint_key = "https://status.firebase.google.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("firebase",)


class FirebaseHomepageCheck(HtmlMarkerCheck):
    """Represent `FirebaseHomepageCheck`."""

    check_key = "firebase_homepage"
    endpoint_key = "https://firebase.google.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("firebase",)


class FirebaseDocsCheck(HtmlMarkerCheck):
    """Represent `FirebaseDocsCheck`."""

    check_key = "firebase_docs"
    endpoint_key = "https://firebase.google.com/docs"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("firebase",)


class FirebaseConsoleCheck(HtmlMarkerCheck):
    """Represent `FirebaseConsoleCheck`."""

    check_key = "firebase_console"
    endpoint_key = "https://console.firebase.google.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("firebase",)


class FirebaseBlogCheck(HtmlMarkerCheck):
    """Represent `FirebaseBlogCheck`."""

    check_key = "firebase_blog"
    endpoint_key = "https://firebase.blog/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("firebase",)


class FirebaseServiceChecker(BaseServiceChecker):
    """Represent `FirebaseServiceChecker`."""

    service_key = "firebase"
    logo_url = "https://img.logo.dev/firebase.google.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.firebase.google.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            FirebaseStatusPageCheck(),
            FirebaseHomepageCheck(),
            FirebaseDocsCheck(),
            FirebaseConsoleCheck(),
            FirebaseBlogCheck(),
        ]

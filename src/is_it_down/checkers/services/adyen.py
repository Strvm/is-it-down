"""Provide functionality for `is_it_down.checkers.services.adyen`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class AdyenStatusPageCheck(HtmlMarkerCheck):
    """Represent `AdyenStatusPageCheck`."""

    check_key = "adyen_status_page"
    endpoint_key = "https://status.adyen.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("adyen",)


class AdyenHomepageCheck(HtmlMarkerCheck):
    """Represent `AdyenHomepageCheck`."""

    check_key = "adyen_homepage"
    endpoint_key = "https://www.adyen.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("adyen",)


class AdyenDocsCheck(HtmlMarkerCheck):
    """Represent `AdyenDocsCheck`."""

    check_key = "adyen_docs"
    endpoint_key = "https://docs.adyen.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("adyen",)


class AdyenSupportCheck(HtmlMarkerCheck):
    """Represent `AdyenSupportCheck`."""

    check_key = "adyen_support"
    endpoint_key = "https://help.adyen.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("adyen",)


class AdyenBlogCheck(HtmlMarkerCheck):
    """Represent `AdyenBlogCheck`."""

    check_key = "adyen_blog"
    endpoint_key = "https://www.adyen.com/knowledge-hub"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("adyen",)


class AdyenServiceChecker(BaseServiceChecker):
    """Represent `AdyenServiceChecker`."""

    service_key = "adyen"
    logo_url = "https://img.logo.dev/adyen.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.adyen.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            AdyenStatusPageCheck(),
            AdyenHomepageCheck(),
            AdyenDocsCheck(),
            AdyenSupportCheck(),
            AdyenBlogCheck(),
        ]

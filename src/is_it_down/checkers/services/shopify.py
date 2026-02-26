"""Provide functionality for `is_it_down.checkers.services.shopify`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class ShopifyStatusPageCheck(HtmlMarkerCheck):
    """Represent `ShopifyStatusPageCheck`."""

    check_key = "shopify_status_page"
    endpoint_key = "https://status.shopify.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("shopify",)


class ShopifyHomepageCheck(HtmlMarkerCheck):
    """Represent `ShopifyHomepageCheck`."""

    check_key = "shopify_homepage"
    endpoint_key = "https://www.shopify.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("shopify",)


class ShopifyDevelopersCheck(HtmlMarkerCheck):
    """Represent `ShopifyDevelopersCheck`."""

    check_key = "shopify_developers"
    endpoint_key = "https://shopify.dev/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("shopify",)


class ShopifyHelpCheck(HtmlMarkerCheck):
    """Represent `ShopifyHelpCheck`."""

    check_key = "shopify_help"
    endpoint_key = "https://help.shopify.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("shopify",)


class ShopifyCommunityCheck(HtmlMarkerCheck):
    """Represent `ShopifyCommunityCheck`."""

    check_key = "shopify_community"
    endpoint_key = "https://community.shopify.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("shopify",)


class ShopifyServiceChecker(BaseServiceChecker):
    """Represent `ShopifyServiceChecker`."""

    service_key = "shopify"
    logo_url = "https://img.logo.dev/shopify.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.shopify.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            ShopifyStatusPageCheck(),
            ShopifyHomepageCheck(),
            ShopifyDevelopersCheck(),
            ShopifyHelpCheck(),
            ShopifyCommunityCheck(),
        ]

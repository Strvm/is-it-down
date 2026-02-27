"""Provide functionality for `is_it_down.checkers.services.n8n`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class N8NHomepageCheck(HtmlMarkerCheck):
    """Represent `N8NHomepageCheck`."""

    check_key = "n8n_home_page"
    endpoint_key = "https://n8n.io/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("n8n",)


class N8NDocsCheck(HtmlMarkerCheck):
    """Represent `N8NDocsCheck`."""

    check_key = "n8n_docs"
    endpoint_key = "https://docs.n8n.io/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("n8n",)


class N8NCloudLoginCheck(HtmlMarkerCheck):
    """Represent `N8NCloudLoginCheck`."""

    check_key = "n8n_cloudlogin"
    endpoint_key = "https://app.n8n.cloud/login"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("n8n",)


class N8NPricingCheck(HtmlMarkerCheck):
    """Represent `N8NPricingCheck`."""

    check_key = "n8n_pricing"
    endpoint_key = "https://n8n.io/pricing/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("n8n",)


class N8NStatusPageCheck(HtmlMarkerCheck):
    """Represent `N8NStatusPageCheck`."""

    check_key = "n8n_status_page"
    endpoint_key = "https://status.n8n.io/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("status",)


class N8NServiceChecker(BaseServiceChecker):
    """Represent `N8NServiceChecker`."""

    service_key = "n8n"
    logo_url = "https://img.logo.dev/n8n.io?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.n8n.io/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            N8NHomepageCheck(),
            N8NDocsCheck(),
            N8NCloudLoginCheck(),
            N8NPricingCheck(),
            N8NStatusPageCheck(),
        ]

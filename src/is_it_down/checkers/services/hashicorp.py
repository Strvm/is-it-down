"""Provide functionality for `is_it_down.checkers.services.hashicorp`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class HashiCorpStatusPageCheck(HtmlMarkerCheck):
    """Represent `HashiCorpStatusPageCheck`."""

    check_key = "hashicorp_status_page"
    endpoint_key = "https://status.hashicorp.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("hashicorp",)


class HashiCorpHomepageCheck(HtmlMarkerCheck):
    """Represent `HashiCorpHomepageCheck`."""

    check_key = "hashicorp_homepage"
    endpoint_key = "https://www.hashicorp.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("hashicorp",)


class HashiCorpDocsCheck(HtmlMarkerCheck):
    """Represent `HashiCorpDocsCheck`."""

    check_key = "hashicorp_docs"
    endpoint_key = "https://developer.hashicorp.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("hashicorp",)


class HashiCorpSupportCheck(HtmlMarkerCheck):
    """Represent `HashiCorpSupportCheck`."""

    check_key = "hashicorp_support"
    endpoint_key = "https://support.hashicorp.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("hashicorp",)


class HashiCorpBlogCheck(HtmlMarkerCheck):
    """Represent `HashiCorpBlogCheck`."""

    check_key = "hashicorp_blog"
    endpoint_key = "https://discuss.hashicorp.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("hashicorp",)


class HashiCorpServiceChecker(BaseServiceChecker):
    """Represent `HashiCorpServiceChecker`."""

    service_key = "hashicorp"
    logo_url = "https://img.logo.dev/hashicorp.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.hashicorp.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            HashiCorpStatusPageCheck(),
            HashiCorpHomepageCheck(),
            HashiCorpDocsCheck(),
            HashiCorpSupportCheck(),
            HashiCorpBlogCheck(),
        ]

"""Provide functionality for `is_it_down.checkers.services.pulumi`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class PulumiStatusPageCheck(HtmlMarkerCheck):
    """Represent `PulumiStatusPageCheck`."""

    check_key = "pulumi_status_page"
    endpoint_key = "https://status.pulumi.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("pulumi",)


class PulumiHomepageCheck(HtmlMarkerCheck):
    """Represent `PulumiHomepageCheck`."""

    check_key = "pulumi_homepage"
    endpoint_key = "https://www.pulumi.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("pulumi",)


class PulumiDocsCheck(HtmlMarkerCheck):
    """Represent `PulumiDocsCheck`."""

    check_key = "pulumi_docs"
    endpoint_key = "https://www.pulumi.com/docs/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("pulumi",)


class PulumiSupportCheck(HtmlMarkerCheck):
    """Represent `PulumiSupportCheck`."""

    check_key = "pulumi_support"
    endpoint_key = "https://www.pulumi.com/support/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("pulumi",)


class PulumiBlogCheck(HtmlMarkerCheck):
    """Represent `PulumiBlogCheck`."""

    check_key = "pulumi_blog"
    endpoint_key = "https://www.pulumi.com/blog/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("pulumi",)


class PulumiServiceChecker(BaseServiceChecker):
    """Represent `PulumiServiceChecker`."""

    service_key = "pulumi"
    logo_url = "https://img.logo.dev/pulumi.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.pulumi.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            PulumiStatusPageCheck(),
            PulumiHomepageCheck(),
            PulumiDocsCheck(),
            PulumiSupportCheck(),
            PulumiBlogCheck(),
        ]

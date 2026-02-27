"""Provide functionality for `is_it_down.checkers.services.npmjs`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class NpmjsHomepageCheck(HtmlMarkerCheck):
    """Represent `NpmjsHomepageCheck`."""

    check_key = "npmjs_home_page"
    endpoint_key = "https://www.npmjs.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("npm",)


class NpmjsPackagePageCheck(HtmlMarkerCheck):
    """Represent `NpmjsPackagePageCheck`."""

    check_key = "npmjs_package_page"
    endpoint_key = "https://www.npmjs.com/package/react"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("npm",)


class NpmjsDocsCheck(HtmlMarkerCheck):
    """Represent `NpmjsDocsCheck`."""

    check_key = "npmjs_docs"
    endpoint_key = "https://docs.npmjs.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("npm",)


class NpmjsRegistryStatusCheck(HtmlMarkerCheck):
    """Represent `NpmjsRegistryStatusCheck`."""

    check_key = "npmjs_registrystatus"
    endpoint_key = "https://status.npmjs.org/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("status",)


class NpmjsRegistryWebCheck(HtmlMarkerCheck):
    """Represent `NpmjsRegistryWebCheck`."""

    check_key = "npmjs_registryweb"
    endpoint_key = "https://registry.npmjs.org/react"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("name",)


class NpmjsServiceChecker(BaseServiceChecker):
    """Represent `NpmjsServiceChecker`."""

    service_key = "npmjs"
    logo_url = "https://img.logo.dev/npmjs.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.npmjs.org/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            NpmjsHomepageCheck(),
            NpmjsPackagePageCheck(),
            NpmjsDocsCheck(),
            NpmjsRegistryStatusCheck(),
            NpmjsRegistryWebCheck(),
        ]

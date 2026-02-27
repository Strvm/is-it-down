"""Provide functionality for `is_it_down.checkers.services.grafana`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class GrafanaStatusPageCheck(HtmlMarkerCheck):
    """Represent `GrafanaStatusPageCheck`."""

    check_key = "grafana_status_page"
    endpoint_key = "https://status.grafana.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("grafana",)


class GrafanaHomepageCheck(HtmlMarkerCheck):
    """Represent `GrafanaHomepageCheck`."""

    check_key = "grafana_homepage"
    endpoint_key = "https://grafana.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("grafana",)


class GrafanaDocsCheck(HtmlMarkerCheck):
    """Represent `GrafanaDocsCheck`."""

    check_key = "grafana_docs"
    endpoint_key = "https://grafana.com/docs/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("grafana",)


class GrafanaSupportCheck(HtmlMarkerCheck):
    """Represent `GrafanaSupportCheck`."""

    check_key = "grafana_support"
    endpoint_key = "https://community.grafana.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("grafana",)


class GrafanaBlogCheck(HtmlMarkerCheck):
    """Represent `GrafanaBlogCheck`."""

    check_key = "grafana_blog"
    endpoint_key = "https://grafana.com/blog/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("grafana",)


class GrafanaServiceChecker(BaseServiceChecker):
    """Represent `GrafanaServiceChecker`."""

    service_key = "grafana"
    logo_url = "https://img.logo.dev/grafana.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.grafana.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            GrafanaStatusPageCheck(),
            GrafanaHomepageCheck(),
            GrafanaDocsCheck(),
            GrafanaSupportCheck(),
            GrafanaBlogCheck(),
        ]

"""Provide functionality for `is_it_down.checkers.services.docker`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.services.statuspage_common import (
    ApiAuthResponseCheck,
    HtmlMarkerCheck,
    StatuspageStatusCheck,
    StatuspageSummaryCheck,
)


class DockerStatusPageCheck(StatuspageStatusCheck):
    """Represent `DockerStatusPageCheck`."""

    check_key = "docker_status_page"
    endpoint_key = "https://www.dockerstatus.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class DockerSummaryCheck(StatuspageSummaryCheck):
    """Represent `DockerSummaryCheck`."""

    check_key = "docker_summary"
    endpoint_key = "https://www.dockerstatus.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class DockerHomepageCheck(HtmlMarkerCheck):
    """Represent `DockerHomepageCheck`."""

    check_key = "docker_homepage"
    endpoint_key = "https://www.docker.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("docker",)


class DockerDocsCheck(HtmlMarkerCheck):
    """Represent `DockerDocsCheck`."""

    check_key = "docker_docs"
    endpoint_key = "https://docs.docker.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("docker",)


class DockerApiAuthCheck(ApiAuthResponseCheck):
    """Represent `DockerApiAuthCheck`."""

    check_key = "docker_api_auth"
    endpoint_key = "https://hub.docker.com/v2/user/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    request_method = "GET"
    request_headers = {"Accept": "application/json"}
    request_json = None
    request_data = None
    expected_http_statuses = (401, 403)


class DockerServiceChecker(BaseServiceChecker):
    """Represent `DockerServiceChecker`."""

    service_key = "docker"
    logo_url = "https://cdn.simpleicons.org/docker"
    official_uptime = "https://www.dockerstatus.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            DockerStatusPageCheck(),
            DockerSummaryCheck(),
            DockerHomepageCheck(),
            DockerDocsCheck(),
            DockerApiAuthCheck(),
        ]

"""Provide functionality for `is_it_down.checkers.services.circleci`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class CircleCIStatusPageCheck(HtmlMarkerCheck):
    """Represent `CircleCIStatusPageCheck`."""

    check_key = "circleci_status_page"
    endpoint_key = "https://status.circleci.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("circleci",)


class CircleCIHomepageCheck(HtmlMarkerCheck):
    """Represent `CircleCIHomepageCheck`."""

    check_key = "circleci_homepage"
    endpoint_key = "https://circleci.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("circleci",)


class CircleCIDocsCheck(HtmlMarkerCheck):
    """Represent `CircleCIDocsCheck`."""

    check_key = "circleci_docs"
    endpoint_key = "https://circleci.com/docs/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("circleci",)


class CircleCISupportCheck(HtmlMarkerCheck):
    """Represent `CircleCISupportCheck`."""

    check_key = "circleci_support"
    endpoint_key = "https://support.circleci.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("circleci",)


class CircleCICommunityCheck(HtmlMarkerCheck):
    """Represent `CircleCICommunityCheck`."""

    check_key = "circleci_community"
    endpoint_key = "https://discuss.circleci.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("circleci",)


class CircleCIServiceChecker(BaseServiceChecker):
    """Represent `CircleCIServiceChecker`."""

    service_key = "circleci"
    logo_url = "https://img.logo.dev/circleci.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.circleci.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            CircleCIStatusPageCheck(),
            CircleCIHomepageCheck(),
            CircleCIDocsCheck(),
            CircleCISupportCheck(),
            CircleCICommunityCheck(),
        ]

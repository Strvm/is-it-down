"""Provide functionality for `is_it_down.checkers.services.bitbucket`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.services.atlassian import AtlassianServiceChecker
from is_it_down.checkers.statuspage_common import (
    ApiAuthResponseCheck,
    HtmlMarkerCheck,
    StatuspageStatusCheck,
    StatuspageSummaryCheck,
)


class BitbucketStatusPageCheck(StatuspageStatusCheck):
    """Represent `BitbucketStatusPageCheck`."""

    check_key = "bitbucket_status_page"
    endpoint_key = "https://bitbucket.status.atlassian.com/api/v2/status.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3


class BitbucketSummaryCheck(StatuspageSummaryCheck):
    """Represent `BitbucketSummaryCheck`."""

    check_key = "bitbucket_summary"
    endpoint_key = "https://bitbucket.status.atlassian.com/api/v2/summary.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25


class BitbucketHomepageCheck(HtmlMarkerCheck):
    """Represent `BitbucketHomepageCheck`."""

    check_key = "bitbucket_homepage"
    endpoint_key = "https://bitbucket.org/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("bitbucket",)


class BitbucketDocsCheck(HtmlMarkerCheck):
    """Represent `BitbucketDocsCheck`."""

    check_key = "bitbucket_docs"
    endpoint_key = "https://support.atlassian.com/bitbucket-cloud/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("bitbucket",)


class BitbucketApiAuthCheck(ApiAuthResponseCheck):
    """Represent `BitbucketApiAuthCheck`."""

    check_key = "bitbucket_api_auth"
    endpoint_key = "https://api.bitbucket.org/2.0/user"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    request_method = "GET"
    request_headers = {"Accept": "application/json"}
    request_json = None
    request_data = None
    expected_http_statuses = (401, 403)


class BitbucketServiceChecker(BaseServiceChecker):
    """Represent `BitbucketServiceChecker`."""

    service_key = "bitbucket"
    logo_url = "https://cdn.simpleicons.org/bitbucket"
    official_uptime = "https://bitbucket.status.atlassian.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = (AtlassianServiceChecker,)

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            BitbucketStatusPageCheck(),
            BitbucketSummaryCheck(),
            BitbucketHomepageCheck(),
            BitbucketDocsCheck(),
            BitbucketApiAuthCheck(),
        ]

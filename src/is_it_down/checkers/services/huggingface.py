"""Provide functionality for `is_it_down.checkers.services.huggingface`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import ApiAuthResponseCheck, HtmlMarkerCheck


class HuggingFaceStatusApiCheck(ApiAuthResponseCheck):
    """Represent `HuggingFaceStatusApiCheck`."""

    check_key = "huggingface_status_api"
    endpoint_key = "https://huggingface.co/api/whoami-v2"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_http_statuses = (401,)
    request_headers = {"Accept": "application/json"}


class HuggingFaceSummaryApiCheck(HtmlMarkerCheck):
    """Represent `HuggingFaceSummaryApiCheck`."""

    check_key = "huggingface_summary_api"
    endpoint_key = "https://huggingface.co/models"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    required_content_type_fragment = None
    expected_markers = ("hugging face",)


class HuggingFaceStatusPageCheck(HtmlMarkerCheck):
    """Represent `HuggingFaceStatusPageCheck`."""

    check_key = "huggingface_status_page"
    endpoint_key = "https://status.huggingface.co/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("status",)


class HuggingFaceHomepageCheck(HtmlMarkerCheck):
    """Represent `HuggingFaceHomepageCheck`."""

    check_key = "huggingface_homepage"
    endpoint_key = "https://huggingface.co/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("hugging face",)


class HuggingFaceDocsCheck(HtmlMarkerCheck):
    """Represent `HuggingFaceDocsCheck`."""

    check_key = "huggingface_docs"
    endpoint_key = "https://huggingface.co/docs"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.1
    expected_markers = ("hugging face",)


class HuggingFaceServiceChecker(BaseServiceChecker):
    """Represent `HuggingFaceServiceChecker`."""

    service_key = "huggingface"
    logo_url = "https://img.logo.dev/huggingface.co?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.huggingface.co/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            HuggingFaceStatusApiCheck(),
            HuggingFaceSummaryApiCheck(),
            HuggingFaceStatusPageCheck(),
            HuggingFaceHomepageCheck(),
            HuggingFaceDocsCheck(),
        ]

"""Provide functionality for `is_it_down.checkers.services.huggingfacehub`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class HuggingFaceHubHomepageCheck(HtmlMarkerCheck):
    """Represent `HuggingFaceHubHomepageCheck`."""

    check_key = "huggingfacehub_home_page"
    endpoint_key = "https://huggingface.co/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("hugging face",)


class HuggingFaceHubModelsCheck(HtmlMarkerCheck):
    """Represent `HuggingFaceHubModelsCheck`."""

    check_key = "huggingfacehub_models"
    endpoint_key = "https://huggingface.co/models"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("hugging face",)


class HuggingFaceHubDocsCheck(HtmlMarkerCheck):
    """Represent `HuggingFaceHubDocsCheck`."""

    check_key = "huggingfacehub_docs"
    endpoint_key = "https://huggingface.co/docs"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("hugging face",)


class HuggingFaceHubApiDocsCheck(HtmlMarkerCheck):
    """Represent `HuggingFaceHubApiDocsCheck`."""

    check_key = "huggingfacehub_apidocs"
    endpoint_key = "https://huggingface.co/docs/api-inference/index"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("hugging face",)


class HuggingFaceHubStatusPageCheck(HtmlMarkerCheck):
    """Represent `HuggingFaceHubStatusPageCheck`."""

    check_key = "huggingfacehub_status_page"
    endpoint_key = "https://status.huggingface.co/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("status",)


class HuggingFaceHubServiceChecker(BaseServiceChecker):
    """Represent `HuggingFaceHubServiceChecker`."""

    service_key = "huggingfacehub"
    logo_url = "https://img.logo.dev/huggingface.co?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.huggingface.co/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            HuggingFaceHubHomepageCheck(),
            HuggingFaceHubModelsCheck(),
            HuggingFaceHubDocsCheck(),
            HuggingFaceHubApiDocsCheck(),
            HuggingFaceHubStatusPageCheck(),
        ]

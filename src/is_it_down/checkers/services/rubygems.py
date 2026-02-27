"""Provide functionality for `is_it_down.checkers.services.rubygems`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class RubyGemsHomepageCheck(HtmlMarkerCheck):
    """Represent `RubyGemsHomepageCheck`."""

    check_key = "rubygems_home_page"
    endpoint_key = "https://rubygems.org/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("rubygems",)


class RubyGemsGemPageCheck(HtmlMarkerCheck):
    """Represent `RubyGemsGemPageCheck`."""

    check_key = "rubygems_gem_page"
    endpoint_key = "https://rubygems.org/gems/rails"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("rails",)


class RubyGemsGuidesCheck(HtmlMarkerCheck):
    """Represent `RubyGemsGuidesCheck`."""

    check_key = "rubygems_guides"
    endpoint_key = "https://guides.rubygems.org/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("rubygems",)


class RubyGemsStatusPageCheck(HtmlMarkerCheck):
    """Represent `RubyGemsStatusPageCheck`."""

    check_key = "rubygems_status_page"
    endpoint_key = "https://status.rubygems.org/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("status",)


class RubyGemsApiVersionsCheck(HtmlMarkerCheck):
    """Represent `RubyGemsApiVersionsCheck`."""

    check_key = "rubygems_apiversions"
    endpoint_key = "https://rubygems.org/api/v1/versions/rails.json"
    interval_seconds = 60
    timeout_seconds = 5.0
    required_content_type_fragment = None
    weight = 0.15
    expected_markers = ("number",)


class RubyGemsServiceChecker(BaseServiceChecker):
    """Represent `RubyGemsServiceChecker`."""

    service_key = "rubygems"
    logo_url = "https://img.logo.dev/rubygems.org?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.rubygems.org/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            RubyGemsHomepageCheck(),
            RubyGemsGemPageCheck(),
            RubyGemsGuidesCheck(),
            RubyGemsStatusPageCheck(),
            RubyGemsApiVersionsCheck(),
        ]

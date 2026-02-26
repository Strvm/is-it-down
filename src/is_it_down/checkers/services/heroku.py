"""Provide functionality for `is_it_down.checkers.services.heroku`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class HerokuStatusPageCheck(HtmlMarkerCheck):
    """Represent `HerokuStatusPageCheck`."""

    check_key = "heroku_status_page"
    endpoint_key = "https://status.heroku.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("heroku",)


class HerokuHomepageCheck(HtmlMarkerCheck):
    """Represent `HerokuHomepageCheck`."""

    check_key = "heroku_homepage"
    endpoint_key = "https://www.heroku.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("heroku",)


class HerokuDevCenterCheck(HtmlMarkerCheck):
    """Represent `HerokuDevCenterCheck`."""

    check_key = "heroku_devcenter"
    endpoint_key = "https://devcenter.heroku.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("heroku",)


class HerokuHelpCheck(HtmlMarkerCheck):
    """Represent `HerokuHelpCheck`."""

    check_key = "heroku_help"
    endpoint_key = "https://help.heroku.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("heroku",)


class HerokuElementsCheck(HtmlMarkerCheck):
    """Represent `HerokuElementsCheck`."""

    check_key = "heroku_elements"
    endpoint_key = "https://elements.heroku.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("heroku",)


class HerokuServiceChecker(BaseServiceChecker):
    """Represent `HerokuServiceChecker`."""

    service_key = "heroku"
    logo_url = "https://img.logo.dev/heroku.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.heroku.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            HerokuStatusPageCheck(),
            HerokuHomepageCheck(),
            HerokuDevCenterCheck(),
            HerokuHelpCheck(),
            HerokuElementsCheck(),
        ]

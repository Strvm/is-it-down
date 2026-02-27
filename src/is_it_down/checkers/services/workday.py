"""Provide functionality for `is_it_down.checkers.services.workday`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class WorkdayStatusPageCheck(HtmlMarkerCheck):
    """Represent `WorkdayStatusPageCheck`."""

    check_key = "workday_status_page"
    endpoint_key = "https://status.workday.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("workday",)


class WorkdayHomepageCheck(HtmlMarkerCheck):
    """Represent `WorkdayHomepageCheck`."""

    check_key = "workday_homepage"
    endpoint_key = "https://www.workday.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("workday",)


class WorkdayDeveloperCheck(HtmlMarkerCheck):
    """Represent `WorkdayDeveloperCheck`."""

    check_key = "workday_developer"
    endpoint_key = "https://developer.workday.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("workday",)


class WorkdayBlogCheck(HtmlMarkerCheck):
    """Represent `WorkdayBlogCheck`."""

    check_key = "workday_blog"
    endpoint_key = "https://blog.workday.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("workday",)


class WorkdayProductsCheck(HtmlMarkerCheck):
    """Represent `WorkdayProductsCheck`."""

    check_key = "workday_products"
    endpoint_key = "https://www.workday.com/en-us/products/human-capital-management.html"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("workday",)


class WorkdayServiceChecker(BaseServiceChecker):
    """Represent `WorkdayServiceChecker`."""

    service_key = "workday"
    logo_url = "https://img.logo.dev/workday.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.workday.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            WorkdayStatusPageCheck(),
            WorkdayHomepageCheck(),
            WorkdayDeveloperCheck(),
            WorkdayBlogCheck(),
            WorkdayProductsCheck(),
        ]

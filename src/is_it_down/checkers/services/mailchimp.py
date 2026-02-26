"""Provide functionality for `is_it_down.checkers.services.mailchimp`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class MailchimpStatusPageCheck(HtmlMarkerCheck):
    """Represent `MailchimpStatusPageCheck`."""

    check_key = "mailchimp_status_page"
    endpoint_key = "https://status.mailchimp.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.3
    expected_markers = ("mailchimp",)


class MailchimpHomepageCheck(HtmlMarkerCheck):
    """Represent `MailchimpHomepageCheck`."""

    check_key = "mailchimp_homepage"
    endpoint_key = "https://mailchimp.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("mailchimp",)


class MailchimpDevelopersCheck(HtmlMarkerCheck):
    """Represent `MailchimpDevelopersCheck`."""

    check_key = "mailchimp_developers"
    endpoint_key = "https://mailchimp.com/developer/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("mailchimp",)


class MailchimpHelpCheck(HtmlMarkerCheck):
    """Represent `MailchimpHelpCheck`."""

    check_key = "mailchimp_help"
    endpoint_key = "https://mailchimp.com/help/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("mailchimp",)


class MailchimpResourcesCheck(HtmlMarkerCheck):
    """Represent `MailchimpResourcesCheck`."""

    check_key = "mailchimp_resources"
    endpoint_key = "https://mailchimp.com/resources/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("mailchimp",)


class MailchimpServiceChecker(BaseServiceChecker):
    """Represent `MailchimpServiceChecker`."""

    service_key = "mailchimp"
    logo_url = "https://img.logo.dev/mailchimp.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.mailchimp.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            MailchimpStatusPageCheck(),
            MailchimpHomepageCheck(),
            MailchimpDevelopersCheck(),
            MailchimpHelpCheck(),
            MailchimpResourcesCheck(),
        ]

"""Provide functionality for `is_it_down.checkers.services.mailgun`."""

from collections.abc import Sequence

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.statuspage_common import HtmlMarkerCheck


class MailgunHomepageCheck(HtmlMarkerCheck):
    """Represent `MailgunHomepageCheck`."""

    check_key = "mailgun_home_page"
    endpoint_key = "https://www.mailgun.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.25
    expected_markers = ("mailgun",)


class MailgunDocsCheck(HtmlMarkerCheck):
    """Represent `MailgunDocsCheck`."""

    check_key = "mailgun_docs"
    endpoint_key = "https://documentation.mailgun.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("mailgun",)


class MailgunAppLoginCheck(HtmlMarkerCheck):
    """Represent `MailgunAppLoginCheck`."""

    check_key = "mailgun_applogin"
    endpoint_key = "https://app.mailgun.com/login"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("mailgun",)


class MailgunApiDocsCheck(HtmlMarkerCheck):
    """Represent `MailgunApiDocsCheck`."""

    check_key = "mailgun_apidocs"
    endpoint_key = "https://documentation.mailgun.com/docs/mailgun/api-reference/send/mailgun/messages/post-v3--domain-name--messages"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.2
    expected_markers = ("mailgun",)


class MailgunStatusPageCheck(HtmlMarkerCheck):
    """Represent `MailgunStatusPageCheck`."""

    check_key = "mailgun_status_page"
    endpoint_key = "https://status.mailgun.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.15
    expected_markers = ("status",)


class MailgunServiceChecker(BaseServiceChecker):
    """Represent `MailgunServiceChecker`."""

    service_key = "mailgun"
    logo_url = "https://img.logo.dev/mailgun.com?token=pk_Ob37anqtSYSOl80OeGoACA"
    official_uptime = "https://status.mailgun.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = ()

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.

        Returns:
            The resulting value.
        """
        return [
            MailgunHomepageCheck(),
            MailgunDocsCheck(),
            MailgunAppLoginCheck(),
            MailgunApiDocsCheck(),
            MailgunStatusPageCheck(),
        ]

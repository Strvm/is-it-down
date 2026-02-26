"""Provide functionality for `is_it_down.checkers.services.gitlab`."""

import re
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

import httpx

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.services.cloudflare import CloudflareServiceChecker
from is_it_down.checkers.utils import (
    add_non_up_debug_metadata,
    json_list_or_none,
    response_latency_ms,
    status_from_http,
)
from is_it_down.core.models import CheckResult

_GITLAB_COMPONENT_STATUS_PATTERN = re.compile(
    r"""<p[^>]*class=["'][^"']*component-status[^"']*["'][^>]*>([^<]+)</p>""",
    re.IGNORECASE,
)
_GITLAB_COMPONENT_DOWN_STATUSES = {"major outage", "major service disruption"}
_GITLAB_COMPONENT_DEGRADED_STATUSES = {"partial outage", "degraded performance", "under maintenance", "maintenance"}
_GITLAB_COMPONENT_UP_STATUSES = {"operational"}


def _extract_gitlab_component_statuses(page_text: str) -> list[str]:
    """Extract gitlab component statuses.

    Args:
        page_text: The page text value.

    Returns:
        The resulting value.
    """
    statuses: list[str] = []
    for match in _GITLAB_COMPONENT_STATUS_PATTERN.finditer(page_text):
        raw_status = match.group(1).strip()
        if raw_status:
            statuses.append(raw_status)
    return statuses


class GitLabStatusPageCheck(BaseCheck):
    """Represent `GitLabStatusPageCheck`."""

    check_key = "gitlab_status_page"
    endpoint_key = "https://status.gitlab.com/"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.4

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        """Run the entrypoint.
        
        Args:
            client: The client value.
        
        Returns:
            The resulting value.
        """
        response = await client.get(self.endpoint_key)
        status = status_from_http(response)
        metadata: dict[str, Any] = {
            "content_type": response.headers.get("content-type", ""),
            "body_chars": len(response.text),
        }

        if response.is_success:
            page_text = response.text
            page_text_lower = page_text.lower()
            component_statuses = _extract_gitlab_component_statuses(page_text)

            metadata["status_title_present"] = "gitlab system status" in page_text_lower
            metadata["all_systems_operational"] = "all systems operational" in page_text_lower
            metadata["component_statuses_sample"] = component_statuses[:8]
            metadata["component_count"] = len(component_statuses)

            if component_statuses:
                normalized_statuses = [component_status.strip().lower() for component_status in component_statuses]
                major_outage_count = sum(
                    normalized_status in _GITLAB_COMPONENT_DOWN_STATUSES for normalized_status in normalized_statuses
                )
                degraded_component_count = sum(
                    normalized_status in _GITLAB_COMPONENT_DEGRADED_STATUSES
                    for normalized_status in normalized_statuses
                )
                operational_component_count = sum(
                    normalized_status in _GITLAB_COMPONENT_UP_STATUSES for normalized_status in normalized_statuses
                )
                unknown_component_count = len(component_statuses) - (
                    major_outage_count + degraded_component_count + operational_component_count
                )

                metadata["major_outage_component_count"] = major_outage_count
                metadata["degraded_component_count"] = degraded_component_count
                metadata["unknown_component_count"] = unknown_component_count

                if major_outage_count > 0:
                    status = "down"
                elif degraded_component_count > 0 or unknown_component_count > 0:
                    status = "degraded"
                else:
                    status = "up"
            elif metadata["all_systems_operational"]:
                status = "up"
            else:
                status = "degraded"
        add_non_up_debug_metadata(metadata=metadata, status=status, response=response)

        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=response_latency_ms(response),
            http_status=response.status_code,
            metadata=metadata,
        )


class GitLabPublicProjectsCheck(BaseCheck):
    """Represent `GitLabPublicProjectsCheck`."""

    check_key = "gitlab_public_projects"
    endpoint_key = "https://gitlab.com/api/v4/projects?per_page=1&simple=true"
    interval_seconds = 60
    timeout_seconds = 5.0
    weight = 0.35

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        """Run the entrypoint.
        
        Args:
            client: The client value.
        
        Returns:
            The resulting value.
        """
        response = await client.get(self.endpoint_key)
        status = status_from_http(response)
        metadata: dict[str, Any] = {}

        if response.is_success:
            payload = json_list_or_none(response)
            if payload is None:
                status = "degraded"
                metadata["projects_payload_present"] = False
            else:
                metadata["project_count"] = len(payload)
                if payload:
                    first_project = payload[0]
                    if isinstance(first_project, dict):
                        project_id = first_project.get("id")
                        project_path = first_project.get("path_with_namespace")
                        metadata["first_project_id"] = project_id
                        metadata["first_project_path"] = project_path
                        if not isinstance(project_id, int):
                            status = "degraded"
                        if not isinstance(project_path, str) or not project_path:
                            status = "degraded"
                    else:
                        status = "degraded"
                else:
                    status = "degraded"
        add_non_up_debug_metadata(metadata=metadata, status=status, response=response)

        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=response_latency_ms(response),
            http_status=response.status_code,
            metadata=metadata,
        )


class GitLabHelpPageCheck(BaseCheck):
    """Represent `GitLabHelpPageCheck`."""

    check_key = "gitlab_help_page"
    endpoint_key = "https://gitlab.com/help"
    interval_seconds = 60
    timeout_seconds = 5.0

    async def run(self, client: httpx.AsyncClient) -> CheckResult:
        """Run the entrypoint.
        
        Args:
            client: The client value.
        
        Returns:
            The resulting value.
        """
        response = await client.get(self.endpoint_key)
        status = status_from_http(response)

        body = response.text
        metadata: dict[str, Any] = {
            "content_type": response.headers.get("content-type", ""),
            "body_preview": body[:80],
        }

        if response.is_success:
            if not body.strip():
                status = "degraded"
            elif "gitlab" not in body.lower():
                status = "degraded"
        add_non_up_debug_metadata(metadata=metadata, status=status, response=response)

        return CheckResult(
            check_key=self.check_key,
            status=status,
            observed_at=datetime.now(UTC),
            latency_ms=response_latency_ms(response),
            http_status=response.status_code,
            metadata=metadata,
        )


class GitLabServiceChecker(BaseServiceChecker):
    """Represent `GitLabServiceChecker`."""

    service_key = "gitlab"
    logo_url = "https://cdn.simpleicons.org/gitlab"
    official_uptime = "https://status.gitlab.com/"
    dependencies: Sequence[type[BaseServiceChecker]] = (CloudflareServiceChecker,)

    def build_checks(self) -> Sequence[BaseCheck]:
        """Build checks.
        
        Returns:
            The resulting value.
        """
        return [
            GitLabStatusPageCheck(),
            GitLabPublicProjectsCheck(),
            GitLabHelpPageCheck(),
        ]

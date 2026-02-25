"""Provide functionality for `is_it_down.checkers.services.gitlab`."""

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

import httpx

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.checkers.utils import (
    add_non_up_debug_metadata,
    json_list_or_none,
    response_latency_ms,
    status_from_http,
)
from is_it_down.core.models import CheckResult


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
        page_text = response.text.lower()
        metadata: dict[str, Any] = {
            "content_type": response.headers.get("content-type", ""),
            "body_chars": len(response.text),
        }

        if response.is_success:
            has_status_title = "gitlab system status" in page_text
            has_active_incident = "active incident" in page_text
            has_partial_disruption = "partial service disruption" in page_text or "degraded performance" in page_text
            has_major_disruption = "major service disruption" in page_text or "major outage" in page_text

            metadata["status_title_present"] = has_status_title
            metadata["active_incident"] = has_active_incident

            if has_major_disruption:
                status = "down"
                metadata["incident_severity"] = "major"
            elif has_active_incident or has_partial_disruption:
                status = "degraded"
                metadata["incident_severity"] = "partial"
            elif not has_status_title:
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
    dependencies: Sequence[type[BaseServiceChecker]] = ()

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

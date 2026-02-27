from __future__ import annotations

from datetime import UTC, datetime

import pytest
from google.cloud import bigquery

from is_it_down.scripts import find_failing_base_checkers
from is_it_down.settings import Settings


class _FakeQueryJob:
    def __init__(self, rows):  # type: ignore[no-untyped-def]
        self._rows = rows

    def result(self):  # type: ignore[no-untyped-def]
        return self._rows


class _FakeClient:
    def __init__(self, rows, project: str | None = "adc-project"):  # type: ignore[no-untyped-def]
        self.rows = rows
        self.project = project
        self.query_calls: list[tuple[str, bigquery.QueryJobConfig]] = []

    def query(self, query: str, job_config: bigquery.QueryJobConfig) -> _FakeQueryJob:
        self.query_calls.append((query, job_config))
        return _FakeQueryJob(self.rows)


def test_build_parser_uses_expected_defaults() -> None:
    parser = find_failing_base_checkers._build_parser()
    args = parser.parse_args([])

    assert args.lookback_hours == 48
    assert args.sample_limit == 3
    assert args.max_groups == 100
    assert args.service_key == []
    assert args.check_key == []
    assert args.json is False


def test_resolve_table_id_prefers_settings_project() -> None:
    settings = Settings(
        bigquery_project_id="configured-project",
        bigquery_dataset_id="dataset_a",
        bigquery_table_id="table_a",
    )
    client = _FakeClient(rows=[], project="adc-project")

    table_id = find_failing_base_checkers._resolve_table_id(client, settings)

    assert table_id == "configured-project.dataset_a.table_a"


def test_resolve_table_id_uses_adc_project_when_settings_project_missing() -> None:
    settings = Settings(
        bigquery_project_id=None,
        bigquery_dataset_id="dataset_a",
        bigquery_table_id="table_a",
    )
    client = _FakeClient(rows=[], project="adc-project")

    table_id = find_failing_base_checkers._resolve_table_id(client, settings)

    assert table_id == "adc-project.dataset_a.table_a"


def test_resolve_table_id_raises_when_project_missing() -> None:
    settings = Settings(
        bigquery_project_id=None,
        bigquery_dataset_id="dataset_a",
        bigquery_table_id="table_a",
    )
    client = _FakeClient(rows=[], project=None)

    with pytest.raises(RuntimeError):
        find_failing_base_checkers._resolve_table_id(client, settings)


def test_query_failing_base_checks_builds_expected_query_and_parameters() -> None:
    observed_at = datetime(2026, 2, 26, 15, 0, tzinfo=UTC)
    rows = [
        {
            "service_key": "cloudflare",
            "check_key": "cloudflare_status_api",
            "failing_count": 9,
            "degraded_count": 5,
            "down_count": 4,
            "first_seen": datetime(2026, 2, 25, 2, 0, tzinfo=UTC),
            "last_seen": observed_at,
            "samples": [
                {
                    "observed_at": observed_at,
                    "status": "down",
                    "latency_ms": 233,
                    "http_status": 503,
                    "error_code": "http_error",
                    "error_message": "upstream returned 503",
                    "metadata_json": "{\"preview\": \"error\"}",
                    "run_id": "run-1",
                    "execution_id": "exec-1",
                }
            ],
        }
    ]
    client = _FakeClient(rows=rows)

    groups = find_failing_base_checkers._query_failing_base_checks(
        client=client,
        table_id="project.dataset.check_results",
        lookback_hours=48,
        sample_limit=2,
        max_groups=50,
        service_keys=["cloudflare"],
        check_keys=["cloudflare_status_api"],
    )

    assert len(groups) == 1
    group = groups[0]
    assert group.service_key == "cloudflare"
    assert group.check_key == "cloudflare_status_api"
    assert group.failing_count == 9
    assert group.degraded_count == 5
    assert group.down_count == 4
    assert group.samples[0].status == "down"
    assert group.samples[0].http_status == 503
    assert group.samples[0].run_id == "run-1"

    assert len(client.query_calls) == 1
    query, job_config = client.query_calls[0]

    assert "FROM `project.dataset.check_results`" in query
    assert "status IN ('degraded', 'down')" in query

    parameters = {parameter.name: parameter for parameter in job_config.query_parameters}
    assert parameters["lookback_hours"].value == 48
    assert parameters["sample_limit"].value == 2
    assert parameters["max_groups"].value == 50
    assert parameters["has_service_filters"].value is True
    assert parameters["has_check_filters"].value is True
    assert parameters["service_keys"].values == ["cloudflare"]
    assert parameters["check_keys"].values == ["cloudflare_status_api"]


def test_render_human_report_handles_empty_results() -> None:
    report = find_failing_base_checkers._render_human_report(
        groups=[],
        table_id="project.dataset.check_results",
        lookback_hours=48,
        service_keys=[],
        check_keys=[],
        generated_at=datetime(2026, 2, 27, 0, 0, tzinfo=UTC),
    )

    assert "Failing BaseChecks (degraded/down)" in report
    assert "No degraded/down BaseCheck rows found" in report
    assert "Service filter: (all)" in report
    assert "Check filter: (all)" in report


def test_render_human_report_includes_group_and_samples() -> None:
    group = find_failing_base_checkers.FailingGroup(
        service_key="notion",
        check_key="notion_status_page",
        failing_count=3,
        degraded_count=2,
        down_count=1,
        first_seen=datetime(2026, 2, 26, 1, 0, tzinfo=UTC),
        last_seen=datetime(2026, 2, 26, 2, 0, tzinfo=UTC),
        samples=[
            find_failing_base_checkers.FailingSample(
                observed_at=datetime(2026, 2, 26, 2, 0, tzinfo=UTC),
                status="down",
                latency_ms=500,
                http_status=502,
                error_code="http_error",
                error_message="bad gateway",
                metadata_json='{"debug":"sample"}',
                run_id="run-10",
                execution_id="exec-10",
            )
        ],
    )

    report = find_failing_base_checkers._render_human_report(
        groups=[group],
        table_id="project.dataset.check_results",
        lookback_hours=48,
        service_keys=["notion"],
        check_keys=["notion_status_page"],
        generated_at=datetime(2026, 2, 27, 0, 0, tzinfo=UTC),
    )

    assert "1. notion.notion_status_page (failing=3, degraded=2, down=1)" in report
    assert "samples:" in report
    assert "error=http_error | bad gateway" in report
    assert 'metadata={"debug":"sample"}' in report


def test_json_payload_contains_expected_schema() -> None:
    group = find_failing_base_checkers.FailingGroup(
        service_key="stripe",
        check_key="stripe_api_auth",
        failing_count=4,
        degraded_count=1,
        down_count=3,
        first_seen=datetime(2026, 2, 26, 10, 0, tzinfo=UTC),
        last_seen=datetime(2026, 2, 26, 11, 0, tzinfo=UTC),
        samples=[
            find_failing_base_checkers.FailingSample(
                observed_at=datetime(2026, 2, 26, 11, 0, tzinfo=UTC),
                status="down",
                latency_ms=1200,
                http_status=503,
                error_code="timeout",
                error_message="request timed out",
                metadata_json='{"path":"/v1/charges"}',
                run_id="run-22",
                execution_id="exec-22",
            )
        ],
    )

    payload = find_failing_base_checkers._json_payload(
        groups=[group],
        table_id="project.dataset.check_results",
        lookback_hours=48,
        service_keys=["stripe"],
        check_keys=["stripe_api_auth"],
        generated_at=datetime(2026, 2, 27, 0, 0, tzinfo=UTC),
    )

    assert payload["lookback_hours"] == 48
    assert payload["table_id"] == "project.dataset.check_results"
    assert payload["filters"] == {
        "service_keys": ["stripe"],
        "check_keys": ["stripe_api_auth"],
    }

    assert isinstance(payload["groups"], list)
    group_payload = payload["groups"][0]
    assert group_payload["service_key"] == "stripe"
    assert group_payload["check_key"] == "stripe_api_auth"
    assert group_payload["failing_count"] == 4
    assert group_payload["samples"][0]["status"] == "down"
    assert group_payload["samples"][0]["observed_at"] == "2026-02-26T11:00:00+00:00"

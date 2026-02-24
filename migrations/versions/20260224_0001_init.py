"""Initial schema

Revision ID: 20260224_0001
Revises:
Create Date: 2026-02-24 00:00:00
"""

import sqlalchemy as sa
from alembic import op

revision = "20260224_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "services",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=120), nullable=False, unique=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("default_interval_seconds", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "service_dependencies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("service_id", sa.Integer(), sa.ForeignKey("services.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "depends_on_service_id",
            sa.Integer(),
            sa.ForeignKey("services.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("dependency_type", sa.String(length=16), nullable=False, server_default="soft"),
        sa.Column("weight", sa.Float(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("service_id", "depends_on_service_id", name="uq_service_dependency_edge"),
    )

    op.create_table(
        "service_checks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("service_id", sa.Integer(), sa.ForeignKey("services.id", ondelete="CASCADE"), nullable=False),
        sa.Column("check_key", sa.String(length=200), nullable=False),
        sa.Column("class_path", sa.String(length=300), nullable=False),
        sa.Column("interval_seconds", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("timeout_seconds", sa.Float(), nullable=False, server_default="5"),
        sa.Column("weight", sa.Float(), nullable=False, server_default="1"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("next_due_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("service_id", "check_key", name="uq_service_check_key"),
    )

    op.create_table(
        "check_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("service_id", sa.Integer(), sa.ForeignKey("services.id", ondelete="CASCADE"), nullable=False),
        sa.Column("check_id", sa.Integer(), sa.ForeignKey("service_checks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="queued"),
        sa.Column("lease_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("worker_id", sa.String(length=120), nullable=True),
        sa.Column("attempt", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("idempotency_key", name="uq_check_job_idempotency"),
    )
    op.create_index("ix_check_jobs_sched_status", "check_jobs", ["scheduled_for", "status"])

    op.create_table(
        "check_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("check_jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("service_id", sa.Integer(), sa.ForeignKey("services.id", ondelete="CASCADE"), nullable=False),
        sa.Column("check_id", sa.Integer(), sa.ForeignKey("service_checks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("http_status", sa.Integer(), nullable=True),
        sa.Column("error_code", sa.String(length=120), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_check_runs_service_check_observed",
        "check_runs",
        ["service_id", "check_id", "observed_at"],
    )

    op.create_table(
        "service_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("service_id", sa.Integer(), sa.ForeignKey("services.id", ondelete="CASCADE"), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_score", sa.Float(), nullable=False),
        sa.Column("effective_score", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("dependency_impacted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("attribution_confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column(
            "probable_root_service_id",
            sa.Integer(),
            sa.ForeignKey("services.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_service_snapshots_service_observed",
        "service_snapshots",
        ["service_id", "observed_at"],
    )

    op.create_table(
        "incidents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("service_id", sa.Integer(), sa.ForeignKey("services.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="open"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("peak_severity", sa.String(length=20), nullable=False, server_default="degraded"),
        sa.Column(
            "probable_root_service_id",
            sa.Integer(),
            sa.ForeignKey("services.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_incidents_service_status", "incidents", ["service_id", "status"])

    op.create_table(
        "incident_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("incident_id", sa.Integer(), sa.ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(length=40), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_incident_events_incident_created", "incident_events", ["incident_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_incident_events_incident_created", table_name="incident_events")
    op.drop_table("incident_events")

    op.drop_index("ix_incidents_service_status", table_name="incidents")
    op.drop_table("incidents")

    op.drop_index("ix_service_snapshots_service_observed", table_name="service_snapshots")
    op.drop_table("service_snapshots")

    op.drop_index("ix_check_runs_service_check_observed", table_name="check_runs")
    op.drop_table("check_runs")

    op.drop_index("ix_check_jobs_sched_status", table_name="check_jobs")
    op.drop_table("check_jobs")

    op.drop_table("service_checks")
    op.drop_table("service_dependencies")
    op.drop_table("services")

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from is_it_down.db.base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Service(Base, TimestampMixin):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    default_interval_seconds: Mapped[int] = mapped_column(Integer, default=60, nullable=False)

    checks: Mapped[list["ServiceCheck"]] = relationship(back_populates="service")


class ServiceDependency(Base, TimestampMixin):
    __tablename__ = "service_dependencies"
    __table_args__ = (
        UniqueConstraint("service_id", "depends_on_service_id", name="uq_service_dependency_edge"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    depends_on_service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id", ondelete="CASCADE"), nullable=False
    )
    dependency_type: Mapped[str] = mapped_column(String(16), default="soft", nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)


class ServiceCheck(Base, TimestampMixin):
    __tablename__ = "service_checks"
    __table_args__ = (UniqueConstraint("service_id", "check_key", name="uq_service_check_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    check_key: Mapped[str] = mapped_column(String(200), nullable=False)
    class_path: Mapped[str] = mapped_column(String(300), nullable=False)
    interval_seconds: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    timeout_seconds: Mapped[float] = mapped_column(Float, default=5.0, nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    next_due_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    service: Mapped[Service] = relationship(back_populates="checks")


class CheckJob(Base, TimestampMixin):
    __tablename__ = "check_jobs"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_check_job_idempotency"),
        Index("ix_check_jobs_sched_status", "scheduled_for", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    check_id: Mapped[int] = mapped_column(ForeignKey("service_checks.id", ondelete="CASCADE"), nullable=False)
    scheduled_for: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="queued", nullable=False)
    lease_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    worker_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    attempt: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)


class CheckRun(Base):
    __tablename__ = "check_runs"
    __table_args__ = (Index("ix_check_runs_service_check_observed", "service_id", "check_id", "observed_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("check_jobs.id", ondelete="CASCADE"), nullable=False)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    check_id: Mapped[int] = mapped_column(ForeignKey("service_checks.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    http_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(120), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ServiceSnapshot(Base):
    __tablename__ = "service_snapshots"
    __table_args__ = (Index("ix_service_snapshots_service_observed", "service_id", "observed_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    raw_score: Mapped[float] = mapped_column(Float, nullable=False)
    effective_score: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    dependency_impacted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    attribution_confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    probable_root_service_id: Mapped[int | None] = mapped_column(
        ForeignKey("services.id", ondelete="SET NULL"), nullable=True
    )


class Incident(Base, TimestampMixin):
    __tablename__ = "incidents"
    __table_args__ = (Index("ix_incidents_service_status", "service_id", "status"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    peak_severity: Mapped[str] = mapped_column(String(20), default="degraded", nullable=False)
    probable_root_service_id: Mapped[int | None] = mapped_column(
        ForeignKey("services.id", ondelete="SET NULL"), nullable=True
    )
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)


class IncidentEvent(Base):
    __tablename__ = "incident_events"
    __table_args__ = (Index("ix_incident_events_incident_created", "incident_id", "created_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(40), nullable=False)
    payload_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

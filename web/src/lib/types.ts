export type ServiceStatus = "up" | "degraded" | "down";

export type ServiceSummary = {
  service_id: number;
  slug: string;
  name: string;
  logo_url: string;
  status: ServiceStatus;
  raw_score: number;
  effective_score: number;
  observed_at: string;
  dependency_impacted: boolean;
  attribution_confidence: number;
  probable_root_service_id: number | null;
};

export type CheckRunSummary = {
  check_key: string;
  status: ServiceStatus;
  observed_at: string;
  latency_ms: number | null;
  http_status: number | null;
  error_code: string | null;
  error_message: string | null;
  metadata: Record<string, unknown>;
};

export type RelatedServiceSummary = {
  service_id: number;
  slug: string;
  name: string;
  logo_url: string;
  status: ServiceStatus;
};

export type ServiceDetail = {
  service_id: number;
  slug: string;
  name: string;
  logo_url: string;
  official_status_url: string | null;
  description: string | null;
  snapshot: ServiceSummary;
  likely_related_services: RelatedServiceSummary[];
  latest_checks: CheckRunSummary[];
};

export type SnapshotPoint = {
  observed_at: string;
  status: ServiceStatus;
  raw_score: number;
  effective_score: number;
  dependency_impacted: boolean;
};

export type IncidentSummary = {
  incident_id: number;
  service_id: number;
  status: string;
  started_at: string;
  resolved_at: string | null;
  peak_severity: string;
  probable_root_service_id: number | null;
  confidence: number;
  summary: string | null;
};

export type BaseCheckUptimeSummary = {
  check_key: string;
  uptime_percent: number;
  health_score: number;
  total_runs: number;
  up_runs: number;
};

export type ServiceUptimeSummary = {
  service_id: number;
  slug: string;
  name: string;
  logo_url: string;
  uptime_percent: number;
  health_score: number;
  checks: BaseCheckUptimeSummary[];
};

export type CheckerTrendPoint = {
  bucket_start: string;
  check_key: string;
  uptime_percent: number;
  health_score: number;
  total_runs: number;
  up_runs: number;
};

export type ServiceCheckerTrendSummary = {
  service_id: number;
  slug: string;
  name: string;
  logo_url: string;
  points: CheckerTrendPoint[];
};

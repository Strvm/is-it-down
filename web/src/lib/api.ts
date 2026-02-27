import type {
  IncidentSummary,
  ServiceCheckerTrendSummary,
  ServiceDetail,
  ServiceSummary,
  ServiceUptimeSummary,
  SnapshotPoint,
} from "@/lib/types";

class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

const DEFAULT_API_BASE_URL = "http://localhost:8080";

function getApiBaseUrl(): string {
  return (
    process.env.API_BASE_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    DEFAULT_API_BASE_URL
  ).replace(/\/$/, "");
}

async function fetchJson<T>(path: string, revalidate = 20): Promise<T> {
  const response = await fetch(
    `${getApiBaseUrl()}${path}`,
    revalidate <= 0
      ? { cache: "no-store" }
      : {
          next: { revalidate },
        },
  );

  if (!response.ok) {
    throw new ApiError(
      `Failed API request (${response.status}): ${path}`,
      response.status,
    );
  }

  return (await response.json()) as T;
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}

export async function listServices(): Promise<ServiceSummary[]> {
  return fetchJson<ServiceSummary[]>("/v1/services", 15);
}

export async function listIncidents(): Promise<IncidentSummary[]> {
  return fetchJson<IncidentSummary[]>("/v1/incidents?status=all", 20);
}

export async function getServicesUptime(
  window = "24h",
): Promise<ServiceUptimeSummary[]> {
  return fetchJson<ServiceUptimeSummary[]>(
    `/v1/services/uptime?window=${encodeURIComponent(window)}`,
    20,
  );
}

export async function getServiceCheckerTrends(
  window = "24h",
): Promise<ServiceCheckerTrendSummary[]> {
  return fetchJson<ServiceCheckerTrendSummary[]>(
    `/v1/services/checker-trends?window=${encodeURIComponent(window)}`,
    20,
  );
}

export async function getServiceCheckerTrend(
  slug: string,
  window = "24h",
): Promise<ServiceCheckerTrendSummary> {
  return fetchJson<ServiceCheckerTrendSummary>(
    `/v1/services/${slug}/checker-trends?window=${encodeURIComponent(window)}`,
    20,
  );
}

export async function getServiceDetail(slug: string): Promise<ServiceDetail> {
  return fetchJson<ServiceDetail>(`/v1/services/${slug}`, 15);
}

export async function getServiceHistory(
  slug: string,
  window = "24h",
): Promise<SnapshotPoint[]> {
  return fetchJson<SnapshotPoint[]>(
    `/v1/services/${slug}/history?window=${encodeURIComponent(window)}`,
    15,
  );
}

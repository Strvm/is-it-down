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

export function getApiBaseUrl(): string {
  return (
    process.env.API_BASE_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    DEFAULT_API_BASE_URL
  ).replace(/\/$/, "");
}

function buildApiUrl(path: string): string {
  return `${getApiBaseUrl()}${path}`;
}

async function fetchJson<T>(url: string, revalidate = 20): Promise<T> {
  const response = await fetch(
    url,
    revalidate <= 0
      ? { cache: "no-store" }
      : {
          next: { revalidate },
        },
  );

  if (!response.ok) {
    throw new ApiError(
      `Failed API request (${response.status}): ${url}`,
      response.status,
    );
  }

  return (await response.json()) as T;
}

async function fetchApiJson<T>(path: string, revalidate = 20): Promise<T> {
  return fetchJson<T>(buildApiUrl(path), revalidate);
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}

export async function listServices(): Promise<ServiceSummary[]> {
  return fetchApiJson<ServiceSummary[]>("/v1/services", 15);
}

export async function listIncidents(): Promise<IncidentSummary[]> {
  return fetchApiJson<IncidentSummary[]>("/v1/incidents?status=all", 20);
}

export async function getServicesUptime(
  timeWindow = "24h",
): Promise<ServiceUptimeSummary[]> {
  return fetchApiJson<ServiceUptimeSummary[]>(
    `/v1/services/uptime?window=${encodeURIComponent(timeWindow)}`,
    20,
  );
}

export async function getServiceCheckerTrends(
  timeWindow = "24h",
  slugs?: string[],
): Promise<ServiceCheckerTrendSummary[]> {
  const params = new URLSearchParams({ window: timeWindow });
  for (const slug of slugs ?? []) {
    params.append("slugs", slug);
  }
  const path = `/v1/services/checker-trends?${params.toString()}`;
  const url =
    typeof window === "undefined"
      ? buildApiUrl(path)
      : `/api/services/checker-trends?${params.toString()}`;
  return fetchJson<ServiceCheckerTrendSummary[]>(url, 20);
}

export async function getServiceCheckerTrend(
  slug: string,
  timeWindow = "24h",
): Promise<ServiceCheckerTrendSummary> {
  return fetchApiJson<ServiceCheckerTrendSummary>(
    `/v1/services/${slug}/checker-trends?window=${encodeURIComponent(timeWindow)}`,
    20,
  );
}

export async function getServiceDetail(slug: string): Promise<ServiceDetail> {
  return fetchApiJson<ServiceDetail>(`/v1/services/${slug}`, 15);
}

export async function getServiceHistory(
  slug: string,
  timeWindow = "24h",
): Promise<SnapshotPoint[]> {
  return fetchApiJson<SnapshotPoint[]>(
    `/v1/services/${slug}/history?window=${encodeURIComponent(timeWindow)}`,
    15,
  );
}

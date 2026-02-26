import type { ScoreBand, ServiceStatus } from "@/lib/types";

export type BadgeTone = "default" | "success" | "warning" | "danger" | "muted";

export function formatSignalLabel(value: string | null | undefined): string {
  if (!value) {
    return "Unknown";
  }
  return value
    .replace(/_/g, " ")
    .trim()
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

export function statusTone(status: ServiceStatus): BadgeTone {
  if (status === "up") {
    return "success";
  }
  if (status === "degraded") {
    return "warning";
  }
  return "danger";
}

export function severityTone(level: number | null | undefined): BadgeTone {
  if (level === null || level === undefined) {
    return "muted";
  }
  if (level >= 4) {
    return "danger";
  }
  if (level >= 2) {
    return "warning";
  }
  return "success";
}

export function scoreBandTone(scoreBand: ScoreBand | string | null | undefined): BadgeTone {
  if (!scoreBand) {
    return "muted";
  }
  if (scoreBand === "critical" || scoreBand === "major_issues") {
    return "danger";
  }
  if (scoreBand === "degraded" || scoreBand === "minor_issues") {
    return "warning";
  }
  return "success";
}

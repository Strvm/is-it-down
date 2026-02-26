"use client";

import { useMemo } from "react";
import { Activity, AlertTriangle, ChartLine, ShieldCheck, TrendingDown } from "lucide-react";
import { CartesianGrid, Line, LineChart, ReferenceLine, XAxis, YAxis } from "recharts";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartContainer, ChartTooltip, ChartTooltipContent, type ChartConfig } from "@/components/ui/chart";
import { formatSignalLabel } from "@/lib/status-granularity";
import type { ServiceCheckerTrendSummary, SnapshotPoint } from "@/lib/types";

type Props = {
  history: SnapshotPoint[];
  checkerTrend: ServiceCheckerTrendSummary;
};

type ScoreTimelinePoint = {
  observed_at: string;
  label: string;
  score: number;
  status: SnapshotPoint["status"];
  statusDetail: SnapshotPoint["status_detail"];
  severityLevel: SnapshotPoint["severity_level"];
};

type CheckerSeries = {
  checkKey: string;
  dataKey: string;
  color: string;
};

type CheckerTrendChartPoint = {
  bucket_start: string;
  label: string;
  [seriesKey: string]: string | number | null;
};

const SCORE_TIMELINE_CONFIG = {
  score: {
    label: "Health score",
    color: "#1d4ed8",
  },
} satisfies ChartConfig;

const CHECKER_LINE_COLORS = [
  "#0f766e",
  "#1d4ed8",
  "#c2410c",
  "#be123c",
  "#7c3aed",
  "#0891b2",
  "#65a30d",
  "#4f46e5",
];

function formatShortTime(isoDate: string): string {
  return new Date(isoDate).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function formatShortDateTime(isoDate: string): string {
  return new Date(isoDate).toLocaleString([], {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function statusBarColor(status: SnapshotPoint["status"]): string {
  if (status === "up") {
    return "bg-emerald-500";
  }
  if (status === "degraded") {
    return "bg-amber-500";
  }
  return "bg-rose-500";
}

function buildCheckerSeries(checkKeys: string[]): CheckerSeries[] {
  return checkKeys.map((checkKey, index) => ({
    checkKey,
    dataKey: `series_${index}`,
    color: CHECKER_LINE_COLORS[index % CHECKER_LINE_COLORS.length],
  }));
}

function buildCheckerTrendRows(
  points: ServiceCheckerTrendSummary["points"],
  series: CheckerSeries[],
): CheckerTrendChartPoint[] {
  const buckets = Array.from(new Set(points.map((point) => point.bucket_start))).sort();
  const rowsByBucket = new Map<string, CheckerTrendChartPoint>();

  for (const bucket of buckets) {
    const row: CheckerTrendChartPoint = {
      bucket_start: bucket,
      label: formatShortTime(bucket),
    };
    for (const item of series) {
      row[item.dataKey] = null;
    }
    rowsByBucket.set(bucket, row);
  }

  const dataKeyByCheck = new Map(series.map((item) => [item.checkKey, item.dataKey]));
  for (const point of points) {
    const row = rowsByBucket.get(point.bucket_start);
    const dataKey = dataKeyByCheck.get(point.check_key);
    if (row && dataKey) {
      row[dataKey] = point.uptime_percent;
    }
  }

  return buckets
    .map((bucket) => rowsByBucket.get(bucket))
    .filter((row): row is CheckerTrendChartPoint => row !== undefined);
}

function latestCheckerUptime(
  points: ServiceCheckerTrendSummary["points"],
  checkKey: string,
): number | null {
  let latestPoint: { ts: number; uptime: number } | null = null;
  for (const point of points) {
    if (point.check_key !== checkKey) {
      continue;
    }
    const ts = Date.parse(point.bucket_start);
    if (!Number.isFinite(ts)) {
      continue;
    }
    if (latestPoint === null || ts > latestPoint.ts) {
      latestPoint = { ts, uptime: point.uptime_percent };
    }
  }
  return latestPoint?.uptime ?? null;
}

export function ServiceDetailAnalytics({ history, checkerTrend }: Props) {
  const timelinePoints = useMemo<ScoreTimelinePoint[]>(
    () =>
      history.map((point) => ({
        observed_at: point.observed_at,
        label: formatShortTime(point.observed_at),
        score: point.effective_score,
        status: point.status,
        statusDetail: point.status_detail ?? null,
        severityLevel: point.severity_level ?? null,
      })),
    [history],
  );

  const timelineSummary = useMemo(() => {
    if (timelinePoints.length === 0) {
      return {
        sampleCount: 0,
        averageScore: 0,
        upRate: 0,
        lowestScore: null as { score: number; observedAt: string } | null,
        statusCounts: { up: 0, degraded: 0, down: 0 },
        detailCounts: {} as Record<string, number>,
        maxSeverity: null as number | null,
      };
    }

    const statusCounts = { up: 0, degraded: 0, down: 0 };
    const detailCounts: Record<string, number> = {};
    let sum = 0;
    let maxSeverity: number | null = null;
    let lowest = { score: timelinePoints[0].score, observedAt: timelinePoints[0].observed_at };

    for (const point of timelinePoints) {
      sum += point.score;
      statusCounts[point.status] += 1;
      const detailKey = point.statusDetail || point.status;
      detailCounts[detailKey] = (detailCounts[detailKey] ?? 0) + 1;
      if (point.severityLevel !== null && point.severityLevel !== undefined) {
        if (maxSeverity === null || point.severityLevel > maxSeverity) {
          maxSeverity = point.severityLevel;
        }
      }
      if (point.score < lowest.score) {
        lowest = { score: point.score, observedAt: point.observed_at };
      }
    }

    return {
      sampleCount: timelinePoints.length,
      averageScore: sum / timelinePoints.length,
      upRate: (statusCounts.up / timelinePoints.length) * 100,
      lowestScore: lowest,
      statusCounts,
      detailCounts,
      maxSeverity,
    };
  }, [timelinePoints]);
  const topDetailSignals = useMemo(
    () => Object.entries(timelineSummary.detailCounts).sort((left, right) => right[1] - left[1]).slice(0, 5),
    [timelineSummary.detailCounts],
  );

  const checkerKeys = useMemo(
    () => Array.from(new Set(checkerTrend.points.map((point) => point.check_key))).sort(),
    [checkerTrend.points],
  );
  const checkerSeries = useMemo(() => buildCheckerSeries(checkerKeys), [checkerKeys]);
  const checkerChartRows = useMemo(
    () => buildCheckerTrendRows(checkerTrend.points, checkerSeries),
    [checkerSeries, checkerTrend.points],
  );
  const checkerChartConfig = useMemo(
    () =>
      checkerSeries.reduce((acc, item) => {
        acc[item.dataKey] = {
          label: item.checkKey,
          color: item.color,
        };
        return acc;
      }, {} as ChartConfig),
    [checkerSeries],
  );

  return (
    <section className="space-y-6">
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <Card className="fade-in-up">
          <CardHeader>
            <CardDescription className="inline-flex items-center gap-1.5">
              <Activity className="size-4 text-teal-700" />
              24h samples
            </CardDescription>
            <CardTitle className="text-3xl tabular-nums">{timelineSummary.sampleCount}</CardTitle>
          </CardHeader>
        </Card>
        <Card className="fade-in-up">
          <CardHeader>
            <CardDescription className="inline-flex items-center gap-1.5">
              <ChartLine className="size-4 text-blue-700" />
              Avg health score
            </CardDescription>
            <CardTitle className="text-3xl tabular-nums">{timelineSummary.averageScore.toFixed(1)}</CardTitle>
          </CardHeader>
        </Card>
        <Card className="fade-in-up">
          <CardHeader>
            <CardDescription className="inline-flex items-center gap-1.5">
              <ShieldCheck className="size-4 text-emerald-700" />
              Healthy snapshots
            </CardDescription>
            <CardTitle className="text-3xl tabular-nums">{timelineSummary.upRate.toFixed(1)}%</CardTitle>
          </CardHeader>
        </Card>
        <Card className="fade-in-up">
          <CardHeader>
            <CardDescription className="inline-flex items-center gap-1.5">
              <TrendingDown className="size-4 text-rose-700" />
              Lowest score (24h)
            </CardDescription>
            <CardTitle className="text-2xl tabular-nums">
              {timelineSummary.lowestScore ? timelineSummary.lowestScore.score.toFixed(1) : "-"}
            </CardTitle>
            <CardDescription>
              {timelineSummary.lowestScore
                ? formatShortDateTime(timelineSummary.lowestScore.observedAt)
                : "No score samples yet"}
            </CardDescription>
          </CardHeader>
        </Card>
        <Card className="fade-in-up">
          <CardHeader>
            <CardDescription className="inline-flex items-center gap-1.5">
              <AlertTriangle className="size-4 text-orange-700" />
              Peak severity
            </CardDescription>
            <CardTitle className="text-3xl tabular-nums">
              {timelineSummary.maxSeverity !== null ? timelineSummary.maxSeverity : "-"}
            </CardTitle>
          </CardHeader>
        </Card>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.3fr_0.9fr]">
        <Card className="fade-in-up">
          <CardHeader>
            <CardTitle>24h Score Timeline</CardTitle>
            <CardDescription>
              Single health score trend with baseline markers for healthy and degraded ranges.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {timelinePoints.length === 0 ? (
              <p className="text-sm text-slate-600">No history points available yet.</p>
            ) : (
              <div className="h-[300px] w-full">
                <ChartContainer config={SCORE_TIMELINE_CONFIG} className="h-full w-full">
                  <LineChart
                    accessibilityLayer
                    data={timelinePoints}
                    margin={{ top: 12, right: 14, left: 0, bottom: 8 }}
                  >
                    <CartesianGrid vertical={false} strokeDasharray="3 3" />
                    <ReferenceLine y={95} stroke="#10b981" strokeDasharray="4 4" />
                    <ReferenceLine y={70} stroke="#f59e0b" strokeDasharray="4 4" />
                    <XAxis dataKey="label" tickLine={false} axisLine={false} minTickGap={22} />
                    <YAxis
                      domain={[0, 100]}
                      tickLine={false}
                      axisLine={false}
                      tickFormatter={(value) => `${value}%`}
                    />
                    <ChartTooltip cursor={false} content={<ChartTooltipContent />} />
                    <Line
                      type="monotone"
                      dataKey="score"
                      stroke="var(--color-score)"
                      strokeWidth={2}
                      dot={false}
                      activeDot={{ r: 4 }}
                    />
                  </LineChart>
                </ChartContainer>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="fade-in-up">
          <CardHeader>
            <CardTitle>Status Distribution</CardTitle>
            <CardDescription>How snapshots were classified in the last 24h.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {(["up", "degraded", "down"] as const).map((status) => {
              const count = timelineSummary.statusCounts[status];
              const percent = timelineSummary.sampleCount
                ? (count / timelineSummary.sampleCount) * 100
                : 0;
              return (
                <div key={status} className="space-y-1.5">
                  <div className="flex items-center justify-between text-sm">
                    <p className="capitalize">{status}</p>
                    <p className="tabular-nums">
                      {count} ({percent.toFixed(1)}%)
                    </p>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-slate-200">
                    <div
                      className={`h-full rounded-full ${statusBarColor(status)}`}
                      style={{ width: `${Math.max(0, Math.min(100, percent))}%` }}
                    />
                  </div>
                </div>
              );
            })}
            <div className="mt-5 border-t border-slate-200 pt-4">
              <p className="mb-2 text-xs font-semibold tracking-wide text-slate-600 uppercase">
                Top granular signals
              </p>
              {topDetailSignals.length === 0 ? (
                <p className="text-sm text-slate-600">No granular signal points available.</p>
              ) : (
                <div className="space-y-2">
                  {topDetailSignals.map(([detail, count]) => {
                    const percent = timelineSummary.sampleCount
                      ? (count / timelineSummary.sampleCount) * 100
                      : 0;
                    return (
                      <div key={detail} className="flex items-center justify-between text-sm">
                        <p>{formatSignalLabel(detail)}</p>
                        <p className="tabular-nums text-slate-600">
                          {count} ({percent.toFixed(1)}%)
                        </p>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </section>

      <Card className="fade-in-up">
        <CardHeader>
          <CardTitle>Base Checker Uptime Trends (24h)</CardTitle>
          <CardDescription>
            Each line represents one base checker for this service, bucketed hourly.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {checkerKeys.length === 0 || checkerChartRows.length === 0 ? (
            <p className="text-sm text-slate-600">No checker trend points available yet.</p>
          ) : (
            <>
              <div className="mb-4 flex flex-wrap gap-2">
                {checkerSeries.map((item) => {
                  const latest = latestCheckerUptime(checkerTrend.points, item.checkKey);
                  return (
                    <span
                      key={`${checkerTrend.slug}-${item.dataKey}`}
                      className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-2.5 py-1 text-xs"
                    >
                      <span
                        className="h-2.5 w-2.5 rounded-full"
                        style={{ backgroundColor: item.color }}
                      />
                      <span className="font-medium">{item.checkKey}</span>
                      <span className="tabular-nums text-slate-600">
                        {latest !== null ? `${latest.toFixed(1)}%` : "n/a"}
                      </span>
                    </span>
                  );
                })}
              </div>
              <div className="h-[310px] w-full">
                <ChartContainer config={checkerChartConfig} className="h-full w-full">
                  <LineChart
                    accessibilityLayer
                    data={checkerChartRows}
                    margin={{ top: 10, right: 14, left: 0, bottom: 8 }}
                  >
                    <CartesianGrid vertical={false} strokeDasharray="3 3" />
                    <XAxis dataKey="label" tickLine={false} axisLine={false} minTickGap={22} />
                    <YAxis
                      domain={[0, 100]}
                      tickLine={false}
                      axisLine={false}
                      tickFormatter={(value) => `${value}%`}
                    />
                    <ChartTooltip cursor={false} content={<ChartTooltipContent />} />
                    {checkerSeries.map((item) => (
                      <Line
                        key={`${checkerTrend.slug}-${item.dataKey}-line`}
                        type="monotone"
                        dataKey={item.dataKey}
                        stroke={item.color}
                        strokeWidth={2}
                        dot={false}
                        activeDot={{ r: 4 }}
                        connectNulls
                      />
                    ))}
                  </LineChart>
                </ChartContainer>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </section>
  );
}

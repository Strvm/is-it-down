"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Activity, AlertTriangle, Search } from "lucide-react";
import { CartesianGrid, Line, LineChart, XAxis, YAxis } from "recharts";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartContainer, ChartTooltip, ChartTooltipContent, type ChartConfig } from "@/components/ui/chart";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { formatSignalLabel, scoreBandTone } from "@/lib/status-granularity";
import type {
  IncidentSummary,
  ServiceCheckerTrendSummary,
  ServiceSummary,
  ServiceUptimeSummary,
} from "@/lib/types";

type Props = {
  services: ServiceSummary[];
  incidents: IncidentSummary[];
  uptimes: ServiceUptimeSummary[];
  checkerTrends: ServiceCheckerTrendSummary[];
};

type CheckerSeries = {
  checkKey: string;
  dataKey: string;
  color: string;
};

type TrendChartRow = {
  bucket_start: string;
  label: string;
  [seriesKey: string]: string | number | null;
};

const PREFETCH_REFRESH_MS = 5_000;

function formatRelative(isoDate: string) {
  return new Date(isoDate).toLocaleString();
}

function formatBucketLabel(isoDate: string) {
  return new Date(isoDate).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function scoreColor(score: number): string {
  if (score >= 95) {
    return "#059669";
  }
  if (score >= 70) {
    return "#d97706";
  }
  return "#dc2626";
}

function serviceCounters(services: ServiceSummary[]) {
  return services.reduce(
    (acc, service) => {
      acc.total += 1;
      if (service.status === "up") {
        acc.up += 1;
      } else if (service.status === "degraded") {
        acc.degraded += 1;
      } else {
        acc.down += 1;
      }
      return acc;
    },
    { total: 0, up: 0, degraded: 0, down: 0 },
  );
}

function buildSeries(checkKeys: string[], scoreByCheck: Map<string, number>): CheckerSeries[] {
  return checkKeys.map((checkKey, index) => ({
    checkKey,
    dataKey: `series_${index}`,
    color: scoreColor(scoreByCheck.get(checkKey) ?? 100),
  }));
}

function buildTrendChartRows(
  points: ServiceCheckerTrendSummary["points"],
  series: CheckerSeries[],
): TrendChartRow[] {
  const buckets = Array.from(new Set(points.map((point) => point.bucket_start))).sort();
  const rowsByBucket = new Map<string, TrendChartRow>();

  for (const bucket of buckets) {
    const row: TrendChartRow = {
      bucket_start: bucket,
      label: formatBucketLabel(bucket),
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
    .filter((row): row is TrendChartRow => row !== undefined);
}

export function DashboardClient({ services, incidents, uptimes, checkerTrends }: Props) {
  const router = useRouter();
  const [search, setSearch] = useState("");
  const prefetchedAtBySlugRef = useRef(new Map<string, number>());
  const normalizedSearch = search.trim().toLowerCase();

  const filteredServices = useMemo(() => {
    if (!normalizedSearch) {
      return services;
    }
    return services.filter((service) => {
      const haystack = `${service.name} ${service.slug}`.toLowerCase();
      return haystack.includes(normalizedSearch);
    });
  }, [normalizedSearch, services]);

  const visibleServiceIds = useMemo(
    () => new Set(filteredServices.map((service) => service.service_id)),
    [filteredServices],
  );

  const filteredIncidents = useMemo(() => {
    if (!normalizedSearch) {
      return incidents;
    }
    return incidents.filter((incident) => visibleServiceIds.has(incident.service_id));
  }, [incidents, normalizedSearch, visibleServiceIds]);

  const filteredUptimes = useMemo(() => {
    if (!normalizedSearch) {
      return uptimes;
    }
    const visibleSlugs = new Set(filteredServices.map((service) => service.slug));
    return uptimes.filter((service) => visibleSlugs.has(service.slug));
  }, [filteredServices, normalizedSearch, uptimes]);

  const serviceRankBySlug = useMemo(
    () => new Map(filteredServices.map((service, index) => [service.slug, index])),
    [filteredServices],
  );

  const filteredCheckerTrends = useMemo(() => {
    const visibleSlugs = normalizedSearch
      ? new Set(filteredServices.map((service) => service.slug))
      : null;

    return checkerTrends
      .filter((service) => (visibleSlugs ? visibleSlugs.has(service.slug) : true))
      .sort((left, right) => {
        const leftRank = serviceRankBySlug.get(left.slug) ?? Number.MAX_SAFE_INTEGER;
        const rightRank = serviceRankBySlug.get(right.slug) ?? Number.MAX_SAFE_INTEGER;
        if (leftRank !== rightRank) {
          return leftRank - rightRank;
        }
        return left.slug.localeCompare(right.slug);
      });
  }, [checkerTrends, filteredServices, normalizedSearch, serviceRankBySlug]);

  const serviceBySlug = useMemo(
    () => new Map(filteredServices.map((service) => [service.slug, service])),
    [filteredServices],
  );
  const uptimeBySlug = useMemo(
    () => new Map(filteredUptimes.map((service) => [service.slug, service])),
    [filteredUptimes],
  );

  const counters = serviceCounters(filteredServices);
  const openIncidents = filteredIncidents.filter((incident) => incident.status === "open").length;
  const criticalSignals = filteredServices.filter((service) => (service.severity_level ?? 0) >= 4).length;
  const dependencySignals = filteredServices.filter((service) => service.dependency_impacted).length;

  useEffect(() => {
    // Prefetch visible service detail routes immediately on mount to minimise click latency.
    // Using requestIdleCallback previously caused a race: after back-navigation the component
    // re-mounts but the user can click a card before the idle callback fires. router.prefetch()
    // is async and non-blocking, so calling it directly has no UI impact.
    const now = Date.now();
    for (const { slug } of filteredCheckerTrends) {
      const lastPrefetchedAt = prefetchedAtBySlugRef.current.get(slug);
      if (!lastPrefetchedAt || now - lastPrefetchedAt >= PREFETCH_REFRESH_MS) {
        prefetchedAtBySlugRef.current.set(slug, Date.now());
        router.prefetch(`/services/${slug}`);
      }
    }
  }, [filteredCheckerTrends, router]);

  function prefetchService(slug: string, force = false) {
    const lastPrefetchedAt = prefetchedAtBySlugRef.current.get(slug);
    if (!force && lastPrefetchedAt && Date.now() - lastPrefetchedAt < PREFETCH_REFRESH_MS) {
      return;
    }
    prefetchedAtBySlugRef.current.set(slug, Date.now());
    router.prefetch(`/services/${slug}`);
  }

  return (
    <main className="grid-glow relative mx-auto flex w-full max-w-[96rem] flex-col gap-6 px-4 py-8 sm:px-6 lg:px-8">
      <header className="fade-in-up space-y-3">
        <p className="inline-flex items-center gap-2 rounded-full border border-slate-300 bg-white/70 px-3 py-1 text-xs tracking-widest text-slate-700 uppercase [font-family:var(--font-ibm-plex-mono)]">
          <Activity className="size-3.5" />
          Live telemetry
        </p>
        <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
          Service Status Control Room
        </h1>
        <p className="max-w-3xl text-slate-600">
          Search services, inspect checker uptime, and review incident activity from the
          API backend.
        </p>
      </header>

      <Card className="fade-in-up">
        <CardHeader>
          <CardTitle className="text-base">Search services</CardTitle>
          <CardDescription>Filter by service name or slug.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="relative">
            <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-slate-500" />
            <Input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search by name or slug..."
              className="pl-9"
            />
          </div>
        </CardContent>
      </Card>

      <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-6">
        <Card className="fade-in-up">
          <CardHeader>
            <CardDescription>Visible services</CardDescription>
            <CardTitle className="text-3xl">{counters.total}</CardTitle>
          </CardHeader>
        </Card>
        <Card className="fade-in-up">
          <CardHeader>
            <CardDescription>Healthy</CardDescription>
            <CardTitle className="text-3xl text-emerald-700">{counters.up}</CardTitle>
          </CardHeader>
        </Card>
        <Card className="fade-in-up">
          <CardHeader>
            <CardDescription>Degraded</CardDescription>
            <CardTitle className="text-3xl text-amber-700">{counters.degraded}</CardTitle>
          </CardHeader>
        </Card>
        <Card className="fade-in-up">
          <CardHeader>
            <CardDescription>Open incidents</CardDescription>
            <CardTitle className="text-3xl">{openIncidents}</CardTitle>
          </CardHeader>
        </Card>
        <Card className="fade-in-up">
          <CardHeader>
            <CardDescription>Critical signals</CardDescription>
            <CardTitle className="text-3xl text-rose-700">{criticalSignals}</CardTitle>
          </CardHeader>
        </Card>
        <Card className="fade-in-up">
          <CardHeader>
            <CardDescription>Dependency-impacted</CardDescription>
            <CardTitle className="text-3xl text-sky-700">{dependencySignals}</CardTitle>
          </CardHeader>
        </Card>
      </section>

      <section className="grid items-stretch gap-6 md:grid-cols-2 lg:grid-cols-3">
        {filteredCheckerTrends.length === 0 ? (
          <Card className="fade-in-up md:col-span-2 lg:col-span-3">
            <CardHeader>
              <CardTitle>Checker uptime trends</CardTitle>
              <CardDescription>No services match the current filter.</CardDescription>
            </CardHeader>
          </Card>
        ) : (
          filteredCheckerTrends.map((serviceTrend) => {
            const summary = serviceBySlug.get(serviceTrend.slug);
            const serviceUptime = uptimeBySlug.get(serviceTrend.slug);
            const checkKeys = Array.from(
              new Set([
                ...(serviceUptime?.checks.map((check) => check.check_key) ?? []),
                ...serviceTrend.points.map((point) => point.check_key),
              ]),
            ).sort();

            const scoreByCheck = new Map(
              (serviceUptime?.checks ?? []).map((check) => [check.check_key, check.health_score]),
            );
            const series = buildSeries(checkKeys, scoreByCheck);
            const chartConfig = series.reduce((acc, item) => {
              acc[item.dataKey] = {
                label: item.checkKey,
                color: item.color,
              };
              return acc;
            }, {} as ChartConfig);
            const chartRows = buildTrendChartRows(serviceTrend.points, series);

            return (
              <Link
                key={serviceTrend.slug}
                href={`/services/${serviceTrend.slug}`}
                prefetch
                onMouseEnter={() => prefetchService(serviceTrend.slug)}
                onFocus={() => prefetchService(serviceTrend.slug)}
                onTouchStart={() => prefetchService(serviceTrend.slug)}
                onPointerDown={() => prefetchService(serviceTrend.slug, true)}
                className="block h-full rounded-xl focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-500"
              >
                <Card className="fade-in-up flex h-full flex-col transition-all hover:-translate-y-0.5 hover:border-teal-400/70 hover:shadow-md">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-3 text-base">
                      <img
                        src={serviceTrend.logo_url}
                        alt={`${serviceTrend.name} logo`}
                        className="h-8 w-8 rounded-md border border-slate-200 bg-white p-1"
                        loading="lazy"
                      />
                      <span className="truncate">{serviceTrend.name}</span>
                      {summary ? (
                        <Badge variant={scoreBandTone(summary.score_band)}>
                          {formatSignalLabel(summary.score_band || summary.status)}
                        </Badge>
                      ) : null}
                    </CardTitle>
                    <CardDescription>
                      24h checker uptime lines ({serviceTrend.slug}).
                    </CardDescription>
                    {summary ? (
                      <CardDescription>
                        Severity {summary.severity_level ?? "-"} • {formatSignalLabel(summary.status_detail)}
                      </CardDescription>
                    ) : null}
                  </CardHeader>
                  <CardContent className="flex flex-1 flex-col">
                    {checkKeys.length === 0 || chartRows.length === 0 ? (
                      <p className="text-sm text-slate-600">No checker trend points available yet.</p>
                    ) : (
                      <>
                        <div className="mb-3 overflow-x-auto pb-1">
                          <div className="flex min-w-max gap-2">
                            {series.map((item) => (
                              <span
                                key={`${serviceTrend.slug}-${item.dataKey}`}
                                className="inline-flex shrink-0 items-center gap-2 rounded-full border border-slate-200 bg-white px-2 py-0.5 text-[11px]"
                              >
                                <span
                                  className="h-2 w-2 rounded-full"
                                  style={{ backgroundColor: item.color }}
                                />
                                <span className="font-medium">{item.checkKey}</span>
                              </span>
                            ))}
                          </div>
                        </div>
                        <div className="h-[240px] w-full flex-none">
                          <ChartContainer config={chartConfig} className="h-full w-full">
                            <LineChart
                              accessibilityLayer
                              data={chartRows}
                              margin={{ top: 10, right: 12, left: 0, bottom: 10 }}
                            >
                              <CartesianGrid vertical={false} strokeDasharray="3 3" />
                              <XAxis
                                dataKey="label"
                                tickLine={false}
                                axisLine={false}
                                minTickGap={18}
                              />
                              <YAxis
                                domain={[0, 100]}
                                tickLine={false}
                                axisLine={false}
                                tickFormatter={(value) => `${value}%`}
                              />
                              <ChartTooltip cursor={false} content={<ChartTooltipContent />} />
                              {series.map((item) => (
                                <Line
                                  key={`${serviceTrend.slug}-${item.dataKey}-line`}
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
              </Link>
            );
          })
        )}
      </section>

      <Card className="fade-in-up">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="size-4 text-amber-600" />
            Recent Incidents
          </CardTitle>
          <CardDescription>Most recent open/resolved incident windows.</CardDescription>
        </CardHeader>
        <CardContent>
          {filteredIncidents.length === 0 ? (
            <p className="text-sm text-slate-600">No incidents found for the current filter.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Status</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead>Started</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredIncidents.slice(0, 8).map((incident) => (
                  <TableRow key={incident.incident_id}>
                    <TableCell className="capitalize">{incident.status}</TableCell>
                    <TableCell className="capitalize">{incident.peak_severity}</TableCell>
                    <TableCell className="text-xs">{formatRelative(incident.started_at)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

    </main>
  );
}

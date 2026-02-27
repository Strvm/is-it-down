"use client";

import Link from "next/link";
import { memo, useCallback, useDeferredValue, useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import LoadingServiceDetail from "@/app/services/[slug]/loading";
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
const INITIAL_VISIBLE_CARDS = 18;
const VISIBLE_CARDS_STEP = 12;
const PREFETCH_LOOKAHEAD = 6;

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

type ServiceTrendCardProps = {
  serviceTrend: ServiceCheckerTrendSummary;
  summary?: ServiceSummary;
  serviceUptime?: ServiceUptimeSummary;
  onCardClick: (event: React.MouseEvent, slug: string) => void;
  onWarmPrefetch: (slug: string) => void;
  onForcePrefetch: (slug: string) => void;
};

const ServiceTrendCard = memo(function ServiceTrendCard({
  serviceTrend,
  summary,
  serviceUptime,
  onCardClick,
  onWarmPrefetch,
  onForcePrefetch,
}: ServiceTrendCardProps) {
  const { checkKeys, series, chartConfig, chartRows } = useMemo(() => {
    const uptimeChecks = serviceUptime?.checks ?? [];
    const checkKeys = Array.from(
      new Set([
        ...uptimeChecks.map((check) => check.check_key),
        ...serviceTrend.points.map((point) => point.check_key),
      ]),
    ).sort();
    const scoreByCheck = new Map(uptimeChecks.map((check) => [check.check_key, check.health_score]));
    const series = buildSeries(checkKeys, scoreByCheck);
    const chartConfig = series.reduce((acc, item) => {
      acc[item.dataKey] = {
        label: item.checkKey,
        color: item.color,
      };
      return acc;
    }, {} as ChartConfig);
    const chartRows = buildTrendChartRows(serviceTrend.points, series);
    return { checkKeys, series, chartConfig, chartRows };
  }, [serviceTrend.points, serviceUptime?.checks]);

  return (
    <Link
      href={`/services/${serviceTrend.slug}`}
      prefetch
      onClick={(event) => onCardClick(event, serviceTrend.slug)}
      onMouseEnter={() => onWarmPrefetch(serviceTrend.slug)}
      onFocus={() => onWarmPrefetch(serviceTrend.slug)}
      onTouchStart={() => onWarmPrefetch(serviceTrend.slug)}
      onPointerDown={() => onForcePrefetch(serviceTrend.slug)}
      className="block h-full min-w-0 rounded-xl focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-500"
    >
      <Card className="fade-in-up flex h-full min-w-0 flex-col transition-all hover:-translate-y-0.5 hover:border-teal-400/70 hover:shadow-md">
        <CardHeader>
          <CardTitle className="flex flex-wrap items-center gap-2.5 text-base sm:flex-nowrap sm:gap-3">
            <img
              src={serviceTrend.logo_url}
              alt={`${serviceTrend.name} logo`}
              className="h-8 w-8 shrink-0 rounded-md border border-slate-200 bg-white p-1"
              loading="lazy"
              decoding="async"
            />
            <span className="min-w-0 flex-1 truncate">{serviceTrend.name}</span>
            {summary ? (
              <Badge variant={scoreBandTone(summary.score_band)} className="shrink-0">
                {formatSignalLabel(summary.score_band || summary.status)}
              </Badge>
            ) : null}
          </CardTitle>
          <CardDescription>24h checker uptime lines ({serviceTrend.slug}).</CardDescription>
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
              <div className="mb-3 max-w-full overflow-x-auto pb-1">
                <div className="flex min-w-max gap-2">
                  {series.map((item) => (
                    <span
                      key={`${serviceTrend.slug}-${item.dataKey}`}
                      className="inline-flex shrink-0 items-center gap-2 rounded-full border border-slate-200 bg-white px-2 py-0.5 text-[11px]"
                    >
                      <span className="h-2 w-2 rounded-full" style={{ backgroundColor: item.color }} />
                      <span className="font-medium">{item.checkKey}</span>
                    </span>
                  ))}
                </div>
              </div>
              <div className="h-[220px] w-full flex-none sm:h-[240px]">
                <ChartContainer config={chartConfig} className="h-full w-full">
                  <LineChart
                    accessibilityLayer
                    data={chartRows}
                    margin={{ top: 10, right: 12, left: 0, bottom: 10 }}
                  >
                    <CartesianGrid vertical={false} strokeDasharray="3 3" />
                    <XAxis dataKey="label" tickLine={false} axisLine={false} minTickGap={18} />
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
});

export function DashboardClient({ services, incidents, uptimes, checkerTrends }: Props) {
  const router = useRouter();
  const [search, setSearch] = useState("");
  const deferredSearch = useDeferredValue(search);
  const [navigatingTo, setNavigatingTo] = useState<string | null>(null);
  const [visibleCount, setVisibleCount] = useState(INITIAL_VISIBLE_CARDS);
  const prefetchedAtBySlugRef = useRef(new Map<string, number>());
  const loadMoreRef = useRef<HTMLDivElement | null>(null);
  const normalizedSearch = deferredSearch.trim().toLowerCase();

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
  const visibleCheckerTrends = useMemo(
    () => filteredCheckerTrends.slice(0, visibleCount),
    [filteredCheckerTrends, visibleCount],
  );
  const hasMoreServices = visibleCheckerTrends.length < filteredCheckerTrends.length;
  const prefetchCandidates = useMemo(() => {
    const prefetchLimit = Math.min(
      filteredCheckerTrends.length,
      visibleCheckerTrends.length + PREFETCH_LOOKAHEAD,
    );
    return filteredCheckerTrends.slice(0, prefetchLimit);
  }, [filteredCheckerTrends, visibleCheckerTrends.length]);

  const serviceBySlug = useMemo(
    () => new Map(filteredServices.map((service) => [service.slug, service])),
    [filteredServices],
  );
  const uptimeBySlug = useMemo(
    () => new Map(filteredUptimes.map((service) => [service.slug, service])),
    [filteredUptimes],
  );
  const counters = useMemo(() => serviceCounters(filteredServices), [filteredServices]);
  const openIncidents = useMemo(
    () => filteredIncidents.filter((incident) => incident.status === "open").length,
    [filteredIncidents],
  );
  const criticalSignals = useMemo(
    () => filteredServices.filter((service) => (service.severity_level ?? 0) >= 4).length,
    [filteredServices],
  );
  const dependencySignals = useMemo(
    () => filteredServices.filter((service) => service.dependency_impacted).length,
    [filteredServices],
  );

  useEffect(() => {
    if (!hasMoreServices) {
      return;
    }
    const target = loadMoreRef.current;
    if (!target) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) {
            continue;
          }
          setVisibleCount((current) =>
            Math.min(current + VISIBLE_CARDS_STEP, filteredCheckerTrends.length),
          );
        }
      },
      {
        rootMargin: "900px 0px 300px 0px",
      },
    );

    observer.observe(target);
    return () => observer.disconnect();
  }, [filteredCheckerTrends.length, hasMoreServices]);

  useEffect(() => {
    // Prefetch visible service detail routes immediately on mount to minimise click latency.
    // Using requestIdleCallback previously caused a race: after back-navigation the component
    // re-mounts but the user can click a card before the idle callback fires. router.prefetch()
    // is async and non-blocking, so calling it directly has no UI impact.
    const now = Date.now();
    for (const { slug } of prefetchCandidates) {
      const lastPrefetchedAt = prefetchedAtBySlugRef.current.get(slug);
      if (!lastPrefetchedAt || now - lastPrefetchedAt >= PREFETCH_REFRESH_MS) {
        prefetchedAtBySlugRef.current.set(slug, Date.now());
        router.prefetch(`/services/${slug}`);
      }
    }
  }, [prefetchCandidates, router]);

  // Safety: if navigation errors out and this component stays mounted, clear the skeleton.
  useEffect(() => {
    if (navigatingTo === null) return;
    const id = window.setTimeout(() => setNavigatingTo(null), 8_000);
    return () => window.clearTimeout(id);
  }, [navigatingTo]);

  const prefetchService = useCallback((slug: string, force = false) => {
    const lastPrefetchedAt = prefetchedAtBySlugRef.current.get(slug);
    if (!force && lastPrefetchedAt && Date.now() - lastPrefetchedAt < PREFETCH_REFRESH_MS) {
      return;
    }
    prefetchedAtBySlugRef.current.set(slug, Date.now());
    router.prefetch(`/services/${slug}`);
  }, [router]);

  const warmPrefetchService = useCallback((slug: string) => {
    prefetchService(slug);
  }, [prefetchService]);
  const forcePrefetchService = useCallback((slug: string) => {
    prefetchService(slug, true);
  }, [prefetchService]);

  const handleCardClick = useCallback((event: React.MouseEvent, slug: string) => {
    event.preventDefault();
    setNavigatingTo(slug);
    router.push(`/services/${slug}`);
  }, [router]);

  // Show the service-detail skeleton immediately on click — before any network round-trip.
  // React 19 + Next.js uses startTransition internally which holds the old UI until the
  // new route is ready, so loading.tsx never shows during the wait. By rendering the
  // skeleton here (pure client-side state, zero latency) we give instant visual feedback
  // regardless of whether the route is in the router cache or not.
  if (navigatingTo !== null) {
    return <LoadingServiceDetail />;
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
              onChange={(event) => {
                setSearch(event.target.value);
                setVisibleCount(INITIAL_VISIBLE_CARDS);
              }}
              placeholder="Search by name or slug..."
              className="pl-9"
            />
          </div>
          <p className="mt-3 text-xs text-slate-500">
            Loaded {visibleCheckerTrends.length} of {filteredCheckerTrends.length} service charts.
          </p>
        </CardContent>
      </Card>

      <section className="grid grid-cols-3 gap-3 sm:grid-cols-2 lg:grid-cols-6">
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
          visibleCheckerTrends.map((serviceTrend) => {
            const summary = serviceBySlug.get(serviceTrend.slug);
            const serviceUptime = uptimeBySlug.get(serviceTrend.slug);
            return (
              <ServiceTrendCard
                key={serviceTrend.slug}
                serviceTrend={serviceTrend}
                summary={summary}
                serviceUptime={serviceUptime}
                onCardClick={handleCardClick}
                onWarmPrefetch={warmPrefetchService}
                onForcePrefetch={forcePrefetchService}
              />
            );
          })
        )}
        {hasMoreServices ? (
          <div ref={loadMoreRef} className="col-span-full py-2 text-center">
            <p className="text-xs text-slate-500">
              Loading more services... ({visibleCheckerTrends.length}/{filteredCheckerTrends.length})
            </p>
          </div>
        ) : null}
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
            <Table className="min-w-[28rem]">
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

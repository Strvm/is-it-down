import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft } from "lucide-react";

import { ServiceDetailAnalytics } from "@/components/service-detail-analytics";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { getServiceCheckerTrend, getServiceDetail, getServiceHistory, isApiError } from "@/lib/api";

type Props = {
  params: Promise<{
    slug: string;
  }>;
};

function formatDateTime(value: string) {
  return new Date(value).toLocaleString();
}

export default async function ServiceDetailPage({ params }: Props) {
  const { slug } = await params;

  let detail;
  try {
    detail = await getServiceDetail(slug);
  } catch (error) {
    if (isApiError(error) && error.status === 404) {
      notFound();
    }
    throw error;
  }

  const [history, checkerTrend] = await Promise.all([
    getServiceHistory(slug, "24h"),
    getServiceCheckerTrend(slug, "24h"),
  ]);
  const likelyRelatedServices = detail.likely_related_services ?? [];
  const hasLikelyRelatedServices = likelyRelatedServices.length > 0;

  return (
    <main className="grid-glow mx-auto flex w-full max-w-[96rem] flex-col gap-6 px-4 py-8 sm:px-6 lg:px-8">
      <div className="fade-in-up flex items-center justify-between">
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <img
              src={detail.logo_url}
              alt={`${detail.name} logo`}
              className="h-10 w-10 rounded-md border border-slate-200 bg-white p-1"
              loading="lazy"
            />
            <h1 className="text-3xl font-bold tracking-tight">{detail.name}</h1>
            <StatusBadge status={detail.snapshot.status} />
          </div>
          {detail.description ? (
            <p className="text-sm text-slate-600">{detail.description}</p>
          ) : null}
          {detail.official_status_url ? (
            <p className="text-sm text-slate-600">
              Official status page:{" "}
              <a
                href={detail.official_status_url}
                target="_blank"
                rel="noreferrer"
                className="font-medium text-teal-700 underline decoration-teal-400 underline-offset-2 hover:text-teal-800"
              >
                {detail.official_status_url}
              </a>
            </p>
          ) : null}
          {!detail.description && !detail.official_status_url ? (
            <p className="text-sm text-slate-600">No extra service description available.</p>
          ) : null}
        </div>
        <Button asChild variant="secondary">
          <Link href="/">
            <ArrowLeft />
            Back
          </Link>
        </Button>
      </div>

      <section className="grid gap-4 sm:grid-cols-3">
        <Card className="fade-in-up">
          <CardHeader>
            <CardDescription>Health score</CardDescription>
            <CardTitle className="text-3xl tabular-nums">
              {detail.snapshot.effective_score.toFixed(1)}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card className="fade-in-up">
          <CardHeader>
            <CardDescription>Likely cause</CardDescription>
            <CardTitle className="text-base">
              {hasLikelyRelatedServices ? "Potential dependency impact detected" : "No dependency signal detected"}
            </CardTitle>
            {hasLikelyRelatedServices ? (
              <div className="mt-2 flex flex-wrap gap-2">
                {likelyRelatedServices.map((relatedService) => (
                  <Link
                    key={relatedService.slug}
                    href={`/services/${relatedService.slug}`}
                    className="inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-2.5 py-1.5 transition-colors hover:border-teal-500 hover:bg-teal-50/40"
                  >
                    <img
                      src={relatedService.logo_url}
                      alt={`${relatedService.name} logo`}
                      className="h-5 w-5 rounded border border-slate-200 bg-white p-0.5"
                      loading="lazy"
                    />
                    <span className="text-sm font-medium">{relatedService.name}</span>
                    <StatusBadge status={relatedService.status} />
                  </Link>
                ))}
              </div>
            ) : detail.snapshot.dependency_impacted ? (
              <CardDescription>
                Dependency impact is possible, but no specific related service could be confirmed.
              </CardDescription>
            ) : null}
            {hasLikelyRelatedServices ? (
              <CardDescription>
                These services were degraded/down around the same time.
              </CardDescription>
            ) : null}
          </CardHeader>
        </Card>
        <Card className="fade-in-up">
          <CardHeader>
            <CardDescription>Last observed</CardDescription>
            <CardTitle className="text-sm font-semibold">
              {formatDateTime(detail.snapshot.observed_at)}
            </CardTitle>
          </CardHeader>
        </Card>
      </section>

      <ServiceDetailAnalytics history={history} checkerTrend={checkerTrend} />

      <Card className="fade-in-up">
        <CardHeader>
          <CardTitle>Latest Checks</CardTitle>
          <CardDescription>Latest result per check key from the backend.</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Check</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Observed</TableHead>
                <TableHead>Latency</TableHead>
                <TableHead>HTTP</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {detail.latest_checks.map((check) => (
                <TableRow key={check.check_key}>
                  <TableCell className="font-medium">{check.check_key}</TableCell>
                  <TableCell className="capitalize">{check.status}</TableCell>
                  <TableCell className="text-xs">{formatDateTime(check.observed_at)}</TableCell>
                  <TableCell>{check.latency_ms ? `${check.latency_ms}ms` : "-"}</TableCell>
                  <TableCell>{check.http_status ?? "-"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </main>
  );
}

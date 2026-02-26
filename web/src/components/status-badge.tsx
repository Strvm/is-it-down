import { Badge } from "@/components/ui/badge";
import {
  formatSignalLabel,
  scoreBandTone,
  severityTone,
  statusTone,
} from "@/lib/status-granularity";
import type { ScoreBand, ServiceStatus } from "@/lib/types";

type Props = {
  status: ServiceStatus;
  statusDetail?: string | null;
  severityLevel?: number | null;
  scoreBand?: ScoreBand | string | null;
  showGranular?: boolean;
};

export function StatusBadge({
  status,
  statusDetail = null,
  severityLevel = null,
  scoreBand = null,
  showGranular = false,
}: Props) {
  return (
    <span className="inline-flex flex-wrap items-center gap-1.5">
      <Badge variant={statusTone(status)}>{formatSignalLabel(status)}</Badge>
      {showGranular && statusDetail ? (
        <Badge variant={severityTone(severityLevel)}>{formatSignalLabel(statusDetail)}</Badge>
      ) : null}
      {showGranular && scoreBand ? (
        <Badge variant={scoreBandTone(scoreBand)}>{formatSignalLabel(scoreBand)}</Badge>
      ) : null}
    </span>
  );
}

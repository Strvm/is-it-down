import { Badge } from "@/components/ui/badge";
import type { ServiceStatus } from "@/lib/types";

type Props = {
  status: ServiceStatus;
};

export function StatusBadge({ status }: Props) {
  if (status === "up") {
    return <Badge variant="success">Up</Badge>;
  }

  if (status === "degraded") {
    return <Badge variant="warning">Degraded</Badge>;
  }

  return <Badge variant="danger">Down</Badge>;
}

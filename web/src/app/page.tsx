import { DashboardClient } from "@/components/dashboard-client";
import {
  getServiceCheckerTrends,
  getServicesUptime,
  listIncidents,
  listServices,
} from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const [services, incidents, uptimes, checkerTrends] = await Promise.all([
    listServices(),
    listIncidents(),
    getServicesUptime("24h"),
    getServiceCheckerTrends("24h"),
  ]);

  return (
    <DashboardClient
      services={services}
      incidents={incidents}
      uptimes={uptimes}
      checkerTrends={checkerTrends}
    />
  );
}

import { DashboardView } from "@/components/dashboard-view";
import { RealtimeRefresh } from "@/components/realtime-refresh";
import { loadDashboardData } from "@/lib/dashboard";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const data = await loadDashboardData();

  return (
    <>
      <RealtimeRefresh />
      <DashboardView data={data} />
    </>
  );
}

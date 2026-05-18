import { DashboardView } from "@/components/dashboard-view";
import { loadDashboardData } from "@/lib/dashboard";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const data = await loadDashboardData();

  return <DashboardView data={data} />;
}

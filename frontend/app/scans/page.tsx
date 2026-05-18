import { EmptyState } from "@/components/empty-state";
import { ScansTable } from "@/components/scans-table";
import { listScans } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function ScansPage() {
  const scans = await listScans({ limit: 100 });

  return (
    <section className="page-stack">
      <header className="page-header">
        <p className="eyebrow">Scan inventory</p>
        <h1>Scans</h1>
      </header>
      {scans.length === 0 ? (
        <EmptyState title="No scans yet" detail="Create a scan from the backend API to populate this view." />
      ) : (
        <ScansTable scans={scans} />
      )}
    </section>
  );
}

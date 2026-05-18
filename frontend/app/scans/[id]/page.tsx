import { notFound } from "next/navigation";

import { EmptyState } from "@/components/empty-state";
import { EventsTable } from "@/components/events-table";
import { SeverityBadge } from "@/components/severity-badge";
import { formatDateTime } from "@/lib/format";
import { getScan, listScanAlerts, listScanEvents } from "@/lib/api";
import type { Alert, PacketEvent, Scan } from "@/lib/types";

export const dynamic = "force-dynamic";

type ScanDetailPageProps = {
  params: Promise<{ id: string }>;
};

export default async function ScanDetailPage({ params }: ScanDetailPageProps) {
  const { id } = await params;
  const data = await loadScanDetail(id);

  if (!data) {
    notFound();
  }

  const { scan, events, alerts } = data;

  return (
    <section className="page-stack">
      <header className="page-header">
        <p className="eyebrow">Scan detail</p>
        <h1>{scan.target_name}</h1>
        <div className="meta-row">
          <span>{scan.status}</span>
          <span>{formatDateTime(scan.started_at)}</span>
        </div>
      </header>

      <section className="split-grid">
        <div className="panel">
          <div className="panel-heading">
            <h2>Events</h2>
            <span>{events.length}</span>
          </div>
          {events.length === 0 ? (
            <EmptyState title="No events" detail="This scan has not received packet metadata yet." />
          ) : (
            <EventsTable events={events} />
          )}
        </div>

        <div className="panel">
          <div className="panel-heading">
            <h2>Alerts</h2>
            <span>{alerts.length}</span>
          </div>
          {alerts.length === 0 ? (
            <EmptyState title="No alerts" detail="No suspicious pattern has been detected for this scan." />
          ) : (
            <div className="alert-list">
              {alerts.map((alert) => (
                <article className="alert-row" key={alert.id}>
                  <SeverityBadge severity={alert.severity} />
                  <div>
                    <h3>{alert.title}</h3>
                    <p>{alert.description}</p>
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>
      </section>
    </section>
  );
}

async function loadScanDetail(
  id: string,
): Promise<{ scan: Scan; events: PacketEvent[]; alerts: Alert[] } | null> {
  try {
    const [scan, events, alerts] = await Promise.all([
      getScan(id),
      listScanEvents(id, { limit: 100 }),
      listScanAlerts(id, { limit: 100 }),
    ]);

    return { scan, events, alerts };
  } catch (error) {
    if (error instanceof Error && error.message.includes("404")) {
      return null;
    }
    throw error;
  }
}

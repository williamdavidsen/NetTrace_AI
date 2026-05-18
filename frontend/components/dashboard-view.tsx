import Link from "next/link";

import { EmptyState } from "@/components/empty-state";
import { EventsTable } from "@/components/events-table";
import { SeverityBadge } from "@/components/severity-badge";
import { StatTile } from "@/components/stat-tile";
import type { DashboardData } from "@/lib/dashboard";
import { formatDateTime } from "@/lib/format";

export function DashboardView({ data }: { data: DashboardData }) {
  const highRiskAlerts = data.alerts.filter((alert) => ["high", "critical"].includes(alert.severity));

  return (
    <section className="page-stack">
      <header className="page-header">
        <p className="eyebrow">Live overview</p>
        <h1>Dashboard</h1>
      </header>

      <section className="stats-grid" aria-label="Dashboard totals">
        <StatTile label="Total scans" value={data.scans.length} />
        <StatTile label="Total events" value={data.metrics.processed_events_total} />
        <StatTile label="Total alerts" value={data.metrics.generated_alerts_total} />
        <StatTile label="High risk alerts" value={highRiskAlerts.length} tone={highRiskAlerts.length > 0 ? "danger" : "neutral"} />
      </section>

      <section className="dashboard-grid">
        <div className="panel">
          <div className="panel-heading">
            <h2>Recent network activity</h2>
            <span>{data.recentEvents.length}</span>
          </div>
          {data.recentEvents.length === 0 ? (
            <EmptyState title="No activity yet" detail="Once events are ingested, recent packet metadata appears here." />
          ) : (
            <EventsTable events={data.recentEvents} />
          )}
        </div>

        <div className="panel">
          <div className="panel-heading">
            <h2>Alert severity</h2>
            <span>{data.alerts.length}</span>
          </div>
          {data.alerts.length === 0 ? (
            <EmptyState title="No alerts" detail="Detection has not produced alerts for the current data." />
          ) : (
            <div className="alert-list">
              {data.alerts.slice(0, 6).map((alert) => (
                <article className="alert-row" key={alert.id}>
                  <SeverityBadge severity={alert.severity} />
                  <div>
                    <h3>{alert.title}</h3>
                    <p>{alert.source_ip ?? "Unknown source"} · {formatDateTime(alert.created_at)}</p>
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>

        <div className="panel">
          <div className="panel-heading">
            <h2>Protocol distribution</h2>
            <span>{data.protocolDistribution.length}</span>
          </div>
          {data.protocolDistribution.length === 0 ? (
            <EmptyState title="No protocol data" detail="Protocol counts are calculated from recent scan events." />
          ) : (
            <div className="bar-list">
              {data.protocolDistribution.map((item) => (
                <div className="bar-row" key={item.protocol}>
                  <span>{item.protocol}</span>
                  <div className="bar-track">
                    <div className="bar-fill" style={{ width: `${item.percentage}%` }} />
                  </div>
                  <strong>{item.count}</strong>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="panel">
          <div className="panel-heading">
            <h2>Most active sources</h2>
            <span>{data.activeSources.length}</span>
          </div>
          {data.activeSources.length === 0 ? (
            <EmptyState title="No source data" detail="Source IP activity appears after event ingestion." />
          ) : (
            <div className="source-list">
              {data.activeSources.map((source) => (
                <div className="source-row" key={source.sourceIp}>
                  <span>{source.sourceIp}</span>
                  <strong>{source.count}</strong>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>Latest scans</h2>
          <Link href="/scans">View scans</Link>
        </div>
        {data.scans.length === 0 ? (
          <EmptyState title="No scans yet" detail="Start a scan through the API to begin collecting dashboard data." />
        ) : (
          <div className="scan-strip">
            {data.scans.slice(0, 4).map((scan) => (
              <Link className="scan-link" href={`/scans/${scan.id}`} key={scan.id}>
                <strong>{scan.target_name}</strong>
                <span>{scan.status} · {formatDateTime(scan.started_at)}</span>
              </Link>
            ))}
          </div>
        )}
      </section>
    </section>
  );
}

import { getMetrics, listAlerts, listScans, listScanEvents } from "@/lib/api";
import type { Alert, Metrics, PacketEvent, Scan } from "@/lib/types";

export type DashboardData = {
  metrics: Metrics;
  scans: Scan[];
  alerts: Alert[];
  recentEvents: PacketEvent[];
  protocolDistribution: Array<{ protocol: string; count: number; percentage: number }>;
  activeSources: Array<{ sourceIp: string; count: number }>;
};

export async function loadDashboardData(): Promise<DashboardData> {
  const [metrics, scans, alerts] = await Promise.all([
    getMetrics(),
    listScans({ limit: 20 }),
    listAlerts({ limit: 20 }),
  ]);

  const recentEvents =
    scans.length > 0 ? await listScanEvents(scans[0].id, { limit: 20 }) : [];

  return {
    metrics,
    scans,
    alerts,
    recentEvents,
    protocolDistribution: buildProtocolDistribution(recentEvents),
    activeSources: buildActiveSources(recentEvents),
  };
}

export function buildProtocolDistribution(events: PacketEvent[]) {
  const counts = events.reduce<Record<string, number>>((accumulator, event) => {
    const protocol = event.protocol.toUpperCase();
    accumulator[protocol] = (accumulator[protocol] ?? 0) + 1;
    return accumulator;
  }, {});
  const total = events.length || 1;

  return Object.entries(counts)
    .map(([protocol, count]) => ({
      protocol,
      count,
      percentage: Math.round((count / total) * 100),
    }))
    .sort((left, right) => right.count - left.count);
}

export function buildActiveSources(events: PacketEvent[]) {
  const counts = events.reduce<Record<string, number>>((accumulator, event) => {
    accumulator[event.source_ip] = (accumulator[event.source_ip] ?? 0) + 1;
    return accumulator;
  }, {});

  return Object.entries(counts)
    .map(([sourceIp, count]) => ({ sourceIp, count }))
    .sort((left, right) => right.count - left.count)
    .slice(0, 5);
}

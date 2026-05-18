import { describe, expect, it } from "vitest";

import { buildActiveSources, buildProtocolDistribution } from "@/lib/dashboard";
import type { PacketEvent } from "@/lib/types";

const baseEvent: PacketEvent = {
  id: "event-1",
  scan_id: "scan-1",
  timestamp: "2026-05-18T10:00:00Z",
  source_ip: "10.0.0.10",
  destination_ip: "10.0.0.20",
  protocol: "TCP",
  source_port: 1234,
  destination_port: 443,
  packet_size: 1200,
  created_at: "2026-05-18T10:00:01Z",
};

describe("dashboard derivations", () => {
  it("builds protocol distribution from recent events", () => {
    const result = buildProtocolDistribution([
      baseEvent,
      { ...baseEvent, id: "event-2", protocol: "udp" },
      { ...baseEvent, id: "event-3", protocol: "UDP" },
    ]);

    expect(result).toEqual([
      { protocol: "UDP", count: 2, percentage: 67 },
      { protocol: "TCP", count: 1, percentage: 33 },
    ]);
  });

  it("finds the most active source IPs", () => {
    const result = buildActiveSources([
      baseEvent,
      { ...baseEvent, id: "event-2", source_ip: "10.0.0.11" },
      { ...baseEvent, id: "event-3", source_ip: "10.0.0.10" },
    ]);

    expect(result).toEqual([
      { sourceIp: "10.0.0.10", count: 2 },
      { sourceIp: "10.0.0.11", count: 1 },
    ]);
  });
});

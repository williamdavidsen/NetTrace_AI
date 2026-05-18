import { afterEach, describe, expect, it, vi } from "vitest";

import { getMetrics, listAlerts, listScanEvents, listScans } from "@/lib/api";

afterEach(() => {
  vi.restoreAllMocks();
});

function mockFetch(payload: unknown, ok = true, status = 200) {
  vi.spyOn(globalThis, "fetch").mockResolvedValue({
    ok,
    status,
    json: async () => payload,
  } as Response);
}

describe("api client", () => {
  it("loads backend metrics", async () => {
    mockFetch({
      processed_events_total: 12,
      generated_alerts_total: 3,
      active_scans_total: 1,
    });

    await expect(getMetrics()).resolves.toEqual({
      processed_events_total: 12,
      generated_alerts_total: 3,
      active_scans_total: 1,
    });
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8000/metrics",
      expect.objectContaining({ next: { revalidate: 5 } }),
    );
  });

  it("adds pagination to list endpoints", async () => {
    mockFetch([]);

    await listScans({ limit: 10, offset: 20 });
    await listAlerts({ limit: 5, scanId: "scan-1" });
    await listScanEvents("scan-1", { limit: 15 });

    expect(fetch).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8000/api/v1/scans?limit=10&offset=20",
      expect.any(Object),
    );
    expect(fetch).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8000/api/v1/alerts?limit=5&offset=0&scan_id=scan-1",
      expect.any(Object),
    );
    expect(fetch).toHaveBeenNthCalledWith(
      3,
      "http://localhost:8000/api/v1/scans/scan-1/events?limit=15&offset=0",
      expect.any(Object),
    );
  });

  it("throws a useful error for failed responses", async () => {
    mockFetch({ detail: "not found" }, false, 404);

    await expect(listScans()).rejects.toThrow("API request failed with 404");
  });
});

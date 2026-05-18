import type { Alert, Metrics, PacketEvent, Scan } from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type ListOptions = {
  limit?: number;
  offset?: number;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    cache: "no-store",
    headers: {
      Accept: "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API request failed with ${response.status}: ${path}`);
  }

  return response.json() as Promise<T>;
}

function listParams(options: ListOptions = {}): string {
  const params = new URLSearchParams();
  params.set("limit", String(options.limit ?? 100));
  params.set("offset", String(options.offset ?? 0));
  return params.toString();
}

export async function getMetrics(): Promise<Metrics> {
  return request<Metrics>("/metrics");
}

export async function listScans(options?: ListOptions): Promise<Scan[]> {
  return request<Scan[]>(`/api/v1/scans?${listParams(options)}`);
}

export async function getScan(scanId: string): Promise<Scan> {
  return request<Scan>(`/api/v1/scans/${scanId}`);
}

export async function listAlerts(options?: ListOptions & { scanId?: string }): Promise<Alert[]> {
  const params = new URLSearchParams(listParams(options));
  if (options?.scanId) {
    params.set("scan_id", options.scanId);
  }
  return request<Alert[]>(`/api/v1/alerts?${params.toString()}`);
}

export async function listScanEvents(scanId: string, options?: ListOptions): Promise<PacketEvent[]> {
  return request<PacketEvent[]>(`/api/v1/scans/${scanId}/events?${listParams(options)}`);
}

export async function listScanAlerts(scanId: string, options?: ListOptions): Promise<Alert[]> {
  return request<Alert[]>(`/api/v1/scans/${scanId}/alerts?${listParams(options)}`);
}

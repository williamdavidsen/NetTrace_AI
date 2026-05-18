export type Scan = {
  id: string;
  target_name: string;
  started_at: string;
  finished_at: string | null;
  status: string;
  created_at: string;
};

export type PacketEvent = {
  id: string;
  scan_id: string;
  timestamp: string;
  source_ip: string;
  destination_ip: string;
  protocol: string;
  source_port: number | null;
  destination_port: number | null;
  packet_size: number;
  created_at: string;
};

export type Alert = {
  id: string;
  scan_id: string;
  severity: string;
  title: string;
  description: string;
  rule_name: string;
  source_ip: string | null;
  created_at: string;
};

export type Metrics = {
  processed_events_total: number;
  generated_alerts_total: number;
  active_scans_total: number;
};

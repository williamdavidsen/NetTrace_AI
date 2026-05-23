# NetTrace AI API

The backend API is versioned under `/api/v1` except for root-level health and metrics endpoints.

## System

```text
GET /health
GET /metrics
GET /api/v1/status
```

`/metrics` returns:

```json
{
  "processed_events_total": 20,
  "generated_alerts_total": 6,
  "active_scans_total": 1
}
```

## Scans

```text
POST  /api/v1/scans
GET   /api/v1/scans?limit=100&offset=0
GET   /api/v1/scans/{scan_id}
PATCH /api/v1/scans/{scan_id}/complete
```

Create scan request:

```json
{
  "target_name": "docker-compose-agent"
}
```

## Events

```text
POST /api/v1/events
GET  /api/v1/scans/{scan_id}/events?limit=100&offset=0
```

Event request:

```json
{
  "scan_id": "11111111-1111-1111-1111-111111111111",
  "timestamp": "2026-01-01T00:00:00Z",
  "source_ip": "192.168.1.10",
  "destination_ip": "8.8.8.8",
  "protocol": "TCP",
  "source_port": 49152,
  "destination_port": 443,
  "packet_size": 512
}
```

## Alerts

```text
GET /api/v1/alerts?limit=100&offset=0
GET /api/v1/alerts?scan_id={scan_id}
GET /api/v1/scans/{scan_id}/alerts
GET /api/v1/alerts/{alert_id}
GET /api/v1/alerts/{alert_id}/explanation
```

## Error Shape

Validation and HTTP errors use a consistent response shape:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed."
  }
}
```

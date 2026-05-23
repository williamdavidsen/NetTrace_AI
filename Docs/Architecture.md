# NetTrace AI Architecture

NetTrace AI is a local, end-to-end network intelligence system built around a simple metadata pipeline. The V1 architecture focuses on clarity, testability, and portfolio readability rather than distributed production complexity.

```text
Python Agent
  -> FastAPI Backend
  -> PostgreSQL + Redis Streams
  -> Rule-Based Detection
  -> Alert and Explanation APIs
  -> Next.js Dashboard
```

## Components

- **Agent:** produces deterministic sample events for repeatable demos and can parse live packet metadata with Scapy.
- **Backend API:** validates requests, stores scans/events/alerts, publishes events to Redis, and exposes query endpoints.
- **PostgreSQL:** persists the durable system state: scans, packet events, and generated alerts.
- **Redis Streams:** carries packet metadata through the event pipeline as `network_events`.
- **Detection service:** evaluates event patterns for port scans, DNS spikes, sensitive ports, large packets, and unknown protocols.
- **Explanation service:** turns alert rule names into readable summaries, patterns, and recommended actions.
- **Dashboard:** presents metrics, recent network activity, scan history, alert severity, protocol distribution, and active sources.

## Runtime Flow

1. The agent creates or reuses a scan.
2. The agent sends packet metadata to `POST /api/v1/events`.
3. The backend validates the payload and writes it to PostgreSQL.
4. The backend publishes the same event to Redis Stream.
5. The detection service evaluates the event and stores matching alerts.
6. The dashboard reads metrics, scans, events, and alerts from the backend.
7. The explanation endpoint provides human-readable context for individual alerts.

## Design Boundaries

The system stores metadata only. Packet payloads and encrypted content are outside the V1 scope. Authentication, multi-tenancy, Kubernetes, and real LLM integration are intentionally left as future improvements so the first release remains complete and demonstrable.

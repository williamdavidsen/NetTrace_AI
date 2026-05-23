# Changelog

## v1.0.0

NetTrace AI V1 is a complete local network intelligence platform:

- Packet metadata agent with deterministic sample mode and Scapy capture mode.
- FastAPI backend with validation, PostgreSQL persistence, Redis Stream publishing, and alert APIs.
- Rule-based detection for port scans, DNS spikes, sensitive ports, large packets, and unknown protocols.
- Rule-based alert explanations with recommended actions.
- Next.js dashboard with scan, event, alert, severity, protocol, and active-source views.
- Docker Compose stack for backend, frontend, PostgreSQL, Redis, and agent.
- Backend, agent, frontend, E2E, security, and observability tests.
- GitHub Actions workflows for quality checks, Docker build, and E2E validation.
- CORS, rate limiting, safe API errors, request IDs, structured logs, metrics, and secret scanning.

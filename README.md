# NetTrace AI

NetTrace AI is a real-time network intelligence platform that collects packet metadata, processes events through a backend pipeline, detects suspicious traffic patterns, and presents alerts in a dashboard.

The first version focuses on a complete local system:

```text
Agent -> Backend API -> PostgreSQL + Redis Stream -> Detection Engine -> Alert API -> Dashboard
```

## Project Structure

Backend, agent, frontend, infrastructure, and CI folders are intentionally separated so each part of the system has a clear responsibility.

## Planned Tech Stack

- Backend: Python, FastAPI, Pydantic, SQLAlchemy/SQLModel, Alembic, Pytest
- Agent: Python
- Data layer: PostgreSQL, Redis Streams
- Frontend: Next.js, TypeScript, React
- Testing: Pytest, Vitest, Playwright
- DevOps: Docker, Docker Compose, GitHub Actions

## Backend Quick Start

```bash
cd backend
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m uvicorn app.main:app --reload
```

Health check:

```text
GET http://localhost:8000/health
```

Run backend tests:

```bash
cd backend
.venv\Scripts\python -m pytest
```

Run database migrations:

```bash
cd backend
.venv\Scripts\python -m alembic upgrade head
```

## Agent Quick Start

Generate deterministic sample packet metadata events:

```bash
cd agent
..\backend\.venv\Scripts\python src\main.py --count 5
```

Send generated events to the configured backend endpoint:

```bash
cd agent
..\backend\.venv\Scripts\python src\main.py --count 5 --send
```

Agent environment variables are listed in `.env.example`. The generated JSON contract matches the backend `PacketEvent` model fields.

## Detection and Alerts

The backend evaluates packet metadata as it is ingested and stores alerts for early suspicious patterns:

- `sensitive_port`: traffic to SSH, Telnet, or RDP.
- `port_scan`: one source IP touching five or more distinct destination ports in a scan.

Read alerts with:

```text
GET http://localhost:8000/api/v1/alerts
GET http://localhost:8000/api/v1/alerts?scan_id=<scan-id>
```

## Repository Layout

```text
backend/      FastAPI backend, database models, services, workers, tests
agent/        Network metadata collector and event sender
frontend/     Next.js dashboard
infra/        Docker Compose and infrastructure files
.github/      GitHub Actions workflows
```

## Development Workflow

Branch strategy:

- `main`: stable release branch
- `develop`: integration branch for active development
- `feature/*`: isolated feature or phase branches

Commit message standard:

- `feat:` new feature
- `fix:` bug fix
- `test:` tests
- `refactor:` code cleanup without behavior changes
- `chore:` maintenance/configuration
- `ci:` CI/CD changes

## Privacy Note

NetTrace AI is designed to collect metadata only. Full packet payloads, encrypted content, and sensitive secrets are outside the first version scope.

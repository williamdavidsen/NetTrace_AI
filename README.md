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

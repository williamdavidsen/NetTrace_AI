# NetTrace AI Testing

The project uses layered tests so each part of the system is verified at the right level.

## Backend

```bash
cd backend
python -m pytest
```

Coverage includes health/status endpoints, database models, Alembic migrations, event ingestion, Redis stream publishing, detection rules, query APIs, alert explanations, security controls, and observability.

## Agent

```bash
cd agent
python -m pytest
```

Coverage includes config loading, deterministic event generation, sender behavior, capture config, packet metadata parsing, payload exclusion, and permission error handling.

## Frontend

```bash
cd frontend
npm test
npm run lint
```

Coverage includes API client behavior, dashboard data shaping, and realtime polling cleanup.

## End-to-End

```bash
cd e2e
python -m pytest
```

The E2E suite starts the Docker Compose stack, verifies the empty dashboard, rejects invalid events, runs the agent happy path, checks alert creation, and validates the explanation endpoint.

## Security Scan

```bash
python scripts/scan_secrets.py
```

The same scan runs in CI before backend tests.

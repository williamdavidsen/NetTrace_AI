# NetTrace AI Release Notes

## v1.0.0

This release completes the V1 portfolio target: a working local system that collects packet metadata, streams events, detects suspicious traffic, explains alerts, and displays the results in a dashboard.

## Demo Scenario

1. Run `docker compose up --build`.
2. PostgreSQL and Redis become healthy.
3. The backend runs migrations and starts the FastAPI app.
4. The frontend starts the Next.js dashboard.
5. The one-shot agent creates a scan and sends sample packet metadata.
6. The backend stores events, publishes them to Redis, generates alerts, and exposes the data through APIs.
7. The dashboard shows real scan, event, alert, severity, protocol, and source activity data.

## Final Verification Checklist

- `docker compose up --build` works.
- Backend tests pass.
- Agent tests pass.
- Frontend tests and lint pass.
- E2E tests pass.
- Dashboard shows real data.
- At least three anomaly types are implemented and tested.
- Explanation endpoint works.
- README includes demo media, screenshots, run commands, test commands, API examples, and security notes.
- Technical documentation is available in English.
- `v1.0.0` release tag is created.

# NetTrace AI Security And Privacy

NetTrace AI is designed as a metadata-only network intelligence platform. The project deliberately avoids packet payload collection and encrypted-content inspection.

## Privacy Rules

- Store timestamps, IP addresses, ports, protocol, packet size, and scan IDs only.
- Do not store packet payload bytes.
- Do not inspect encrypted content.
- Keep local demo data separate from real sensitive traffic.
- Use `.env.example` for configuration examples.
- Never commit real secrets.

## API Hardening

- Pydantic validates IP addresses, ports, protocol values, packet size, and scan payloads.
- Invalid payloads are rejected before database writes.
- HTTP and validation errors use a safe `error.code` and `error.message` shape.
- CORS is restricted through `BACKEND_CORS_ORIGINS`.
- In-memory rate limiting protects the local V1 backend from accidental or abusive request bursts.
- `x-request-id` is returned on requests and included in structured logs.

## Secret Scanning

Tracked files are scanned for common secret patterns:

```bash
python scripts/scan_secrets.py
```

This runs in the backend GitHub Actions workflow before tests.

## Production Notes

The V1 rate limiter is process-local, which is correct for the portfolio stack. A multi-instance deployment should move counters to Redis or an edge gateway. Authentication and role-based authorization are intentionally left for a later version after the local V1 system is complete.

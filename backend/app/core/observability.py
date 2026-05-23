import json
import logging
import sys
import time
from collections.abc import Callable, Awaitable
from uuid import uuid4

from fastapi import Request, Response


REQUEST_ID_HEADER = "x-request-id"
logger = logging.getLogger("nettrace")


class JsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname.lower(),
            "message": record.getMessage(),
            "logger": record.name,
        }
        for key in (
            "request_id",
            "method",
            "path",
            "status_code",
            "duration_ms",
            "client",
            "error_type",
        ):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, sort_keys=True)


def configure_logging(level: str) -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    if not root_logger.handlers:
        root_logger.addHandler(logging.StreamHandler(sys.stdout))
    for handler in root_logger.handlers:
        if handler.__class__.__module__.startswith("_pytest."):
            continue
        handler.setFormatter(JsonLogFormatter())


async def request_observability_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid4())
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception as exc:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.exception(
            "request.failed",
            extra=_log_context(request, request_id, 500, duration_ms, exc),
        )
        raise

    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers[REQUEST_ID_HEADER] = request_id
    logger.info(
        "request.completed",
        extra=_log_context(request, request_id, response.status_code, duration_ms),
    )
    return response


def _log_context(
    request: Request,
    request_id: str,
    status_code: int,
    duration_ms: float,
    exc: Exception | None = None,
) -> dict[str, object]:
    context: dict[str, object] = {
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status_code": status_code,
        "duration_ms": duration_ms,
    }
    if request.client:
        context["client"] = request.client.host
    if exc is not None:
        context["error_type"] = exc.__class__.__name__
    return context

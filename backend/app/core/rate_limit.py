from collections import defaultdict, deque
from time import monotonic
from typing import Deque

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send


class InMemoryRateLimiter:
    def __init__(self, app: ASGIApp, requests: int, window_seconds: int) -> None:
        self.app = app
        self.requests = requests
        self.window_seconds = window_seconds
        self._hits: dict[str, Deque[float]] = defaultdict(deque)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        if request.method == "OPTIONS" or self._is_allowed(request):
            await self.app(scope, receive, send)
            return

        response = JSONResponse(
            status_code=429,
            content={
                "error": {
                    "code": "rate_limit_exceeded",
                    "message": "Too many requests. Please retry later.",
                }
            },
            headers={"Retry-After": str(self.window_seconds)},
        )
        await response(scope, receive, send)

    def _is_allowed(self, request: Request) -> bool:
        now = monotonic()
        key = _client_key(request)
        hits = self._hits[key]
        while hits and now - hits[0] >= self.window_seconds:
            hits.popleft()

        if len(hits) >= self.requests:
            return False

        hits.append(now)
        return True


def _client_key(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",", maxsplit=1)[0].strip()
    if request.client:
        return request.client.host
    return "unknown"

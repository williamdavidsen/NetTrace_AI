import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from events import PacketEventPayload


class EventSenderError(RuntimeError):
    pass


class EventSender:
    def __init__(self, event_url: str, timeout_seconds: float = 5.0) -> None:
        self.event_url = event_url
        self.timeout_seconds = timeout_seconds

    def send(self, event: PacketEventPayload) -> dict[str, object]:
        payload = json.dumps(event.to_dict()).encode("utf-8")
        request = Request(
            self.event_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                body = response.read().decode("utf-8")
                if not body:
                    return {"status_code": response.status}
                return json.loads(body)
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise EventSenderError(f"Backend rejected event with HTTP {exc.code}: {detail}") from exc
        except URLError as exc:
            raise EventSenderError(f"Could not reach backend at {self.event_url}: {exc.reason}") from exc

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from events import PacketEventPayload


class EventSenderError(RuntimeError):
    pass


class EventSender:
    def __init__(
        self,
        event_url: str,
        timeout_seconds: float = 5.0,
        scan_url: str | None = None,
    ) -> None:
        self.event_url = event_url
        self.timeout_seconds = timeout_seconds
        self.scan_url = scan_url

    def send(self, event: PacketEventPayload) -> dict[str, object]:
        return self._post_json(self.event_url, event.to_dict(), "event")

    def create_scan(self, target_name: str) -> dict[str, object]:
        if self.scan_url is None:
            raise EventSenderError("Scan URL is required to create scans.")
        return self._post_json(self.scan_url, {"target_name": target_name}, "scan")

    def _post_json(
        self,
        url: str,
        payload_dict: dict[str, object],
        resource_name: str,
    ) -> dict[str, object]:
        payload = json.dumps(payload_dict).encode("utf-8")
        request = Request(
            url,
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
            raise EventSenderError(
                f"Backend rejected {resource_name} with HTTP {exc.code}: {detail}"
            ) from exc
        except URLError as exc:
            raise EventSenderError(f"Could not reach backend at {url}: {exc.reason}") from exc

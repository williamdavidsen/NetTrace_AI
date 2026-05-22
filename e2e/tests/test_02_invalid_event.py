from datetime import datetime, timezone
from urllib.error import HTTPError

import pytest

from support import post_json


def test_invalid_event_is_rejected() -> None:
    scan = post_json("/api/v1/scans", {"target_name": "invalid-event-e2e"})
    invalid_event = {
        "scan_id": scan["id"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_ip": "not-an-ip",
        "destination_ip": "8.8.8.8",
        "protocol": "TCP",
        "source_port": 12000,
        "destination_port": 443,
        "packet_size": 128,
    }

    with pytest.raises(HTTPError) as exc_info:
        post_json("/api/v1/events", invalid_event)

    assert exc_info.value.code == 422

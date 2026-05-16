from collections.abc import Generator

from redis import Redis
from redis.exceptions import RedisError

from app.core.config import settings
from app.models import PacketEvent


class EventStreamPublishError(RuntimeError):
    pass


class RedisEventStream:
    def __init__(self, client: Redis, stream_name: str) -> None:
        self._client = client
        self._stream_name = stream_name

    def publish_packet_event(self, event: PacketEvent) -> str:
        payload = {
            "event_id": event.id,
            "scan_id": event.scan_id,
            "timestamp": event.timestamp.isoformat(),
            "source_ip": event.source_ip,
            "destination_ip": event.destination_ip,
            "protocol": event.protocol,
            "source_port": _optional_int(event.source_port),
            "destination_port": _optional_int(event.destination_port),
            "packet_size": str(event.packet_size),
        }
        try:
            stream_id = self._client.xadd(self._stream_name, payload)
        except RedisError as exc:
            raise EventStreamPublishError("Could not publish packet event to Redis stream.") from exc

        if isinstance(stream_id, bytes):
            return stream_id.decode("utf-8")
        return str(stream_id)


def get_redis_client() -> Generator[Redis, None, None]:
    client = Redis.from_url(settings.redis_url, decode_responses=True)
    try:
        yield client
    finally:
        client.close()


def get_event_stream() -> Generator[RedisEventStream, None, None]:
    for client in get_redis_client():
        yield RedisEventStream(client=client, stream_name=settings.redis_stream_name)


def _optional_int(value: int | None) -> str:
    if value is None:
        return ""
    return str(value)

import argparse
import json

from capture import (
    PacketCaptureConfig,
    PacketCaptureDependencyError,
    PacketCapturePermissionError,
    capture_packet_metadata,
)
from config import load_config
from events import SampleEventGenerator
from sender import EventSender


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect NetTrace AI packet metadata events.")
    parser.add_argument(
        "--mode",
        choices=("sample", "capture"),
        help="Use deterministic sample events or live packet metadata capture.",
    )
    parser.add_argument("--count", type=int, help="Number of metadata events to emit.")
    parser.add_argument("--send", action="store_true", help="POST generated events to the backend.")
    parser.add_argument(
        "--create-scan",
        action="store_true",
        help="Create a backend scan first and use its id for emitted events.",
    )
    parser.add_argument("--scan-target", help="Target name used with --create-scan.")
    parser.add_argument("--interface", help="Network interface for capture mode.")
    parser.add_argument("--filter", help="BPF capture filter for capture mode.")
    parser.add_argument("--timeout", type=int, help="Capture timeout in seconds.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config()
    count = args.count or config.default_event_count
    mode = args.mode or config.capture_mode
    if mode not in {"sample", "capture"}:
        raise SystemExit("Capture mode must be either 'sample' or 'capture'.")
    sender = EventSender(
        config.event_url,
        timeout_seconds=config.request_timeout_seconds,
        scan_url=config.scan_url,
    )
    scan_id = config.scan_id

    if args.create_scan:
        scan = sender.create_scan(args.scan_target or config.scan_target_name)
        scan_id = str(scan["id"])

    if mode == "capture":
        capture_config = PacketCaptureConfig(
            scan_id=scan_id,
            interface=args.interface or config.capture_interface,
            packet_filter=args.filter or config.capture_filter,
            count=count,
            timeout_seconds=args.timeout or config.capture_timeout_seconds,
        )
        try:
            events = capture_packet_metadata(capture_config)
        except (PacketCaptureDependencyError, PacketCapturePermissionError) as exc:
            raise SystemExit(str(exc)) from exc
    else:
        generator = SampleEventGenerator(scan_id=scan_id, seed=config.random_seed)
        events = generator.generate(count)

    if args.send:
        for event in events:
            print(json.dumps(sender.send(event), sort_keys=True))
        return

    for event in events:
        print(json.dumps(event.to_dict(), sort_keys=True))


if __name__ == "__main__":
    main()

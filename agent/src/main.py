import argparse
import json

from config import load_config
from events import SampleEventGenerator
from sender import EventSender


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate NetTrace AI sample packet events.")
    parser.add_argument("--count", type=int, help="Number of events to generate.")
    parser.add_argument("--send", action="store_true", help="POST generated events to the backend.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config()
    count = args.count or config.default_event_count
    generator = SampleEventGenerator(scan_id=config.scan_id, seed=config.random_seed)
    events = generator.generate(count)

    if args.send:
        sender = EventSender(config.event_url, timeout_seconds=config.request_timeout_seconds)
        for event in events:
            print(json.dumps(sender.send(event), sort_keys=True))
        return

    for event in events:
        print(json.dumps(event.to_dict(), sort_keys=True))


if __name__ == "__main__":
    main()

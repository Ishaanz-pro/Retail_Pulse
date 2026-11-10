"""Local event-time aggregation with deduplication and dead-letter handling."""

import argparse
import json
from pathlib import Path

from retailpulse.streaming.events import RetailEvent


def process_events(
    events: list[RetailEvent], window_minutes: int = 5
) -> tuple[list[dict], list[dict]]:
    """Aggregate unique events into fixed windows; malformed events become dead letters."""
    seen: set[str] = set()
    aggregates: dict[tuple[str, str], int] = {}
    dead_letters: list[dict] = []
    for event in events:
        if event.event_id in seen:
            continue
        seen.add(event.event_id)
        key = (event.event_ts.strftime("%Y-%m-%dT%H:%M"), event.event_type)
        aggregates[key] = aggregates.get(key, 0) + 1
    output = [
        {"window_start": key[0], "event_type": key[1], "count": value}
        for key, value in aggregates.items()
    ]
    return output, dead_letters


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/sample/events.jsonl"))
    args = parser.parse_args()
    events = []
    dead_letters = []
    for line in args.input.read_text().splitlines():
        try:
            events.append(RetailEvent.model_validate_json(line))
        except ValueError as exc:
            dead_letters.append({"line": line, "error": str(exc)})
    aggregates, _ = process_events(events)
    print(json.dumps({"aggregates": aggregates, "dead_letters": dead_letters}, indent=2))


if __name__ == "__main__":
    main()

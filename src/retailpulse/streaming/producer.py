"""Local event generator and optional Pub/Sub publisher."""

import argparse
import random
from pathlib import Path

from retailpulse.streaming.events import RetailEvent


def generate_events(count: int = 100, seed: int = 42) -> list[RetailEvent]:
    random.seed(seed)
    kinds = [
        "ORDER_CREATED",
        "ORDER_CONFIRMED",
        "ORDER_SHIPPED",
        "ORDER_DELIVERED",
        "INVENTORY_UPDATED",
        "PAYMENT_COMPLETED",
    ]
    return [
        RetailEvent(
            event_type=random.choice(kinds),
            entity_id=f"O{random.randint(1, count // 2 + 1)}",
            payload={"source": "synthetic"},
        )
        for _ in range(count)
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", type=int, default=100)
    parser.add_argument("--output", type=Path, default=Path("data/sample/events.jsonl"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "\n".join(event.model_dump_json() for event in generate_events(args.events)) + "\n"
    )


if __name__ == "__main__":
    main()

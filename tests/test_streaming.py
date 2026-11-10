from datetime import datetime, timezone

from retailpulse.streaming.events import RetailEvent
from retailpulse.streaming.pipeline import process_events


def test_streaming_deduplicates_event_ids():
    event = RetailEvent(
        event_id="same",
        event_type="ORDER_CREATED",
        entity_id="O1",
        event_ts=datetime.now(timezone.utc),
        payload={},
    )
    aggregate, dead_letters = process_events([event, event])
    assert sum(item["count"] for item in aggregate) == 1
    assert dead_letters == []

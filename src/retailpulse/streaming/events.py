"""Validated retail event contracts."""

import uuid
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

EventType = Literal[
    "ORDER_CREATED",
    "ORDER_CONFIRMED",
    "ORDER_SHIPPED",
    "ORDER_DELIVERED",
    "INVENTORY_UPDATED",
    "PAYMENT_COMPLETED",
]


class RetailEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    entity_id: str
    event_ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, str | int | float]

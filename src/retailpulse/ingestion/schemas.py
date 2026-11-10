"""Pydantic schemas used at ingestion boundaries."""

from datetime import datetime

from pydantic import BaseModel, Field


class Product(BaseModel):
    product_id: str
    name: str
    category: str
    unit_price: float = Field(gt=0)


class Warehouse(BaseModel):
    warehouse_id: str
    region: str
    capacity: int = Field(gt=0)


class SalesRecord(BaseModel):
    transaction_id: str
    order_id: str
    product_id: str
    warehouse_id: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    transaction_ts: datetime

    @property
    def revenue(self) -> float:
        return self.quantity * self.unit_price

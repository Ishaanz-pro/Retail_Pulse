"""Data quality checks with explicit accepted/rejected counts."""

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class QualityReport:
    accepted: int
    rejected: int
    duplicate_count: int
    errors: list[str] = field(default_factory=list)


def validate_sales(
    sales: pd.DataFrame, products: pd.DataFrame, warehouses: pd.DataFrame
) -> tuple[pd.DataFrame, QualityReport]:
    """Validate sales facts and return only records safe for analytical use."""
    errors: list[str] = []
    required = {
        "transaction_id",
        "product_id",
        "warehouse_id",
        "quantity",
        "unit_price",
        "transaction_ts",
    }
    missing = required - set(sales.columns)
    if missing:
        raise ValueError(f"sales schema missing columns: {sorted(missing)}")
    duplicate_count = int(sales.transaction_id.duplicated().sum())
    valid = (
        ~sales.transaction_id.duplicated()
        & sales.quantity.gt(0)
        & sales.unit_price.gt(0)
        & sales.product_id.isin(products.product_id)
        & sales.warehouse_id.isin(warehouses.warehouse_id)
        & sales.transaction_ts.notna()
    )
    rejected = int((~valid).sum())
    if rejected:
        errors.append("records failed positive-value, timestamp, or referential-integrity checks")
    clean = sales.loc[valid].copy()
    return clean, QualityReport(len(clean), rejected, duplicate_count, errors)

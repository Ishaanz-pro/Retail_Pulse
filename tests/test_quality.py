import pandas as pd

from retailpulse.governance.quality import validate_sales


def test_quality_rejects_duplicates_and_invalid_references():
    products = pd.DataFrame({"product_id": ["P1"]})
    warehouses = pd.DataFrame({"warehouse_id": ["W1"]})
    sales = pd.DataFrame(
        [
            {
                "transaction_id": "T1",
                "product_id": "P1",
                "warehouse_id": "W1",
                "quantity": 1,
                "unit_price": 2,
                "transaction_ts": "2026-01-01",
            },
            {
                "transaction_id": "T1",
                "product_id": "P1",
                "warehouse_id": "W1",
                "quantity": 1,
                "unit_price": 2,
                "transaction_ts": "2026-01-01",
            },
            {
                "transaction_id": "T2",
                "product_id": "P9",
                "warehouse_id": "W1",
                "quantity": 1,
                "unit_price": 2,
                "transaction_ts": "2026-01-01",
            },
        ]
    )
    clean, report = validate_sales(sales, products, warehouses)
    assert len(clean) == 1
    assert report.duplicate_count == 1
    assert report.rejected == 2

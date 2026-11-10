"""Generate deterministic synthetic retail datasets."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


def generate_datasets(records: int = 50_000, seed: int = 42) -> dict[str, pd.DataFrame]:
    """Create related synthetic dimensions and sales facts without personal data."""
    rng = np.random.default_rng(seed)
    products = pd.DataFrame(
        {
            "product_id": [f"P{i:04d}" for i in range(1, 101)],
            "name": [f"Product {i:04d}" for i in range(1, 101)],
            "category": rng.choice(["Grocery", "Electronics", "Home", "Apparel"], 100),
            "unit_price": np.round(rng.uniform(5, 250, 100), 2),
        }
    )
    warehouses = pd.DataFrame(
        {
            "warehouse_id": [f"W{i:02d}" for i in range(1, 11)],
            "region": rng.choice(["North", "South", "East", "West"], 10),
            "capacity": rng.integers(10_000, 50_000, 10),
        }
    )
    product_ids = rng.choice(products.product_id, records)
    quantities = rng.integers(1, 8, records)
    dates = pd.date_range(end=datetime.now(timezone.utc), periods=365, freq="D")
    day = rng.choice(dates, records)
    price_map = products.set_index("product_id").unit_price
    sales = pd.DataFrame(
        {
            "transaction_id": [f"T{i:08d}" for i in range(records)],
            "order_id": [f"O{i:08d}" for i in rng.integers(1, records // 2 + 1, records)],
            "product_id": product_ids,
            "warehouse_id": rng.choice(warehouses.warehouse_id, records),
            "quantity": quantities,
            "unit_price": np.round(
                [price_map[p] for p in product_ids] * rng.uniform(0.9, 1.1, records), 2
            ),
            "transaction_ts": day,
        }
    )
    inventory = pd.DataFrame(
        {
            "product_id": rng.choice(products.product_id, 500),
            "warehouse_id": rng.choice(warehouses.warehouse_id, 500),
            "quantity_on_hand": rng.integers(0, 1000, 500),
            "reorder_point": rng.integers(50, 300, 500),
        }
    ).drop_duplicates(["product_id", "warehouse_id"])
    return {
        "products": products,
        "warehouses": warehouses,
        "sales_transactions": sales,
        "inventory": inventory,
    }


def write_datasets(datasets: dict[str, pd.DataFrame], output: Path) -> None:
    """Write CSV inputs and a manifest."""
    output.mkdir(parents=True, exist_ok=True)
    for name, frame in datasets.items():
        frame.to_csv(output / f"{name}.csv", index=False)
    (output / "manifest.json").write_text(
        json.dumps({"records": len(datasets["sales_transactions"])}, indent=2)
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=int, default=50_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("data/raw"))
    args = parser.parse_args()
    write_datasets(generate_datasets(args.records, args.seed), args.output)


if __name__ == "__main__":
    main()

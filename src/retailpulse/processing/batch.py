"""Local batch ETL; cloud runners can consume the same validated tables."""

import argparse
import json
from pathlib import Path

import pandas as pd

from retailpulse.governance.quality import validate_sales


def run_batch(input_dir: Path, output_dir: Path) -> dict:
    """Validate, enrich, and persist analytical tables."""
    products = pd.read_csv(input_dir / "products.csv")
    warehouses = pd.read_csv(input_dir / "warehouses.csv")
    sales = pd.read_csv(input_dir / "sales_transactions.csv", parse_dates=["transaction_ts"])
    clean, report = validate_sales(sales, products, warehouses)
    clean["revenue"] = clean["quantity"] * clean["unit_price"]
    clean = clean.merge(products[["product_id", "name", "category"]], on="product_id", how="left")
    clean = clean.merge(warehouses[["warehouse_id", "region"]], on="warehouse_id", how="left")
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, frame in {
        "sales_fact": clean,
        "products_dim": products,
        "warehouses_dim": warehouses,
    }.items():
        try:
            frame.to_parquet(output_dir / f"{name}.parquet", index=False)
        except ImportError:
            frame.to_csv(output_dir / f"{name}.csv", index=False)
    (output_dir / "quality_report.json").write_text(json.dumps(report.__dict__, indent=2))
    return report.__dict__


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/raw"))
    parser.add_argument("--output", type=Path, default=Path("data/processed"))
    args = parser.parse_args()
    print(json.dumps(run_batch(args.input, args.output), indent=2))


if __name__ == "__main__":
    main()

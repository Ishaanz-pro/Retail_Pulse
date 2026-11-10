"""Train and persist the local demand and anomaly artifacts."""

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd

from retailpulse.ml.models import detect_anomalies, forecast_daily


def train(input_dir: Path, output_dir: Path) -> dict:
    """Persist measured forecast metrics and anomaly outputs."""
    file = input_dir / "sales_fact.parquet"
    sales = pd.read_parquet(file) if file.exists() else pd.read_csv(input_dir / "sales_fact.csv")
    forecast, metrics = forecast_daily(sales)
    anomalies = detect_anomalies(sales)
    output_dir.mkdir(parents=True, exist_ok=True)
    forecast.to_csv(output_dir / "forecast.csv", index=False)
    anomalies.to_csv(output_dir / "anomalies.csv", index=False)
    joblib.dump({"model": "seasonal-naive", "window": 7}, output_dir / "forecast_model.joblib")
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/processed"))
    parser.add_argument("--output", type=Path, default=Path("models"))
    args = parser.parse_args()
    print(json.dumps(train(args.input, args.output), indent=2))


if __name__ == "__main__":
    main()

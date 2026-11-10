"""Forecast and anomaly models."""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import mean_absolute_error, mean_squared_error


def mape(actual: np.ndarray, predicted: np.ndarray) -> float:
    mask = actual != 0
    return (
        float(np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100)
        if mask.any()
        else 0.0
    )


def forecast_daily(sales: pd.DataFrame, horizon: int = 7) -> tuple[pd.DataFrame, dict[str, float]]:
    """Use a seasonal-naive baseline and report measured holdout metrics."""
    daily = (
        sales.assign(day=pd.to_datetime(sales.transaction_ts).dt.date)
        .groupby("day", as_index=False)
        .quantity.sum()
    )
    values = daily.quantity.to_numpy(dtype=float)
    split = max(1, len(values) - horizon)
    actual = values[split:]
    baseline = np.repeat(values[max(0, split - 7) : split].mean(), len(actual))
    metrics = {
        "mae": float(mean_absolute_error(actual, baseline)),
        "rmse": float(mean_squared_error(actual, baseline) ** 0.5),
        "mape": mape(actual, baseline),
    }
    future = pd.DataFrame(
        {
            "day": pd.date_range(
                pd.Timestamp(daily.day.iloc[-1]) + pd.Timedelta(days=1, unit="D"), periods=horizon
            ),
            "forecast_quantity": np.repeat(values[-7:].mean(), horizon),
        }
    )
    return future, metrics


def detect_anomalies(sales: pd.DataFrame) -> pd.DataFrame:
    """Detect unusual daily quantity using a measurable Isolation Forest score."""
    daily = (
        sales.assign(day=pd.to_datetime(sales.transaction_ts).dt.date)
        .groupby("day", as_index=False)
        .quantity.sum()
    )
    model = IsolationForest(random_state=42, contamination="auto")
    daily["anomaly"] = model.fit_predict(daily[["quantity"]]) == -1
    daily["anomaly_score"] = model.decision_function(daily[["quantity"]])
    return daily

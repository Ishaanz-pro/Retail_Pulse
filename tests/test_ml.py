import pandas as pd

from retailpulse.ml.models import detect_anomalies, forecast_daily


def test_ml_outputs_metrics_and_anomaly_flags():
    frame = pd.DataFrame(
        {
            "transaction_ts": pd.date_range("2026-01-01", periods=20),
            "quantity": range(1, 21),
            "revenue": range(1, 21),
        }
    )
    _, metrics = forecast_daily(frame, horizon=3)
    assert set(metrics) == {"mae", "rmse", "mape"}
    assert len(detect_anomalies(frame)) == 20

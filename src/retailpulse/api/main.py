"""FastAPI application."""

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from retailpulse.common.config import settings
from retailpulse.ml.models import detect_anomalies, forecast_daily
from retailpulse.warehouse.repository import AnalyticsRepository

app = FastAPI(title="RetailPulse API", version="0.1.0")
repo = AnalyticsRepository(settings.retailpulse_db_path)


def _sales_frame() -> pd.DataFrame:
    processed = settings.retailpulse_data_dir / "processed"
    file = processed / "sales_fact.parquet"
    if file.exists():
        return pd.read_parquet(file)
    csv = processed / "sales_fact.csv"
    if csv.exists():
        return pd.read_csv(csv)
    raise HTTPException(status_code=503, detail="Run the batch pipeline before querying analytics")


class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.retailpulse_env}


@app.get("/api/v1/analytics/overview")
def overview() -> dict:
    frame = _sales_frame()
    return {
        "transactions": len(frame),
        "revenue": round(float(frame.revenue.sum()), 2),
        "products": int(frame.product_id.nunique()),
    }


@app.get("/api/v1/analytics/sales")
def sales(limit: int = Query(30, ge=1, le=365)) -> list[dict]:
    frame = _sales_frame()
    frame["day"] = pd.to_datetime(frame.transaction_ts).dt.date.astype(str)
    return (
        frame.groupby("day", as_index=False)
        .agg(revenue=("revenue", "sum"), units=("quantity", "sum"))
        .tail(limit)
        .to_dict("records")
    )


@app.get("/api/v1/analytics/products")
def products(limit: int = Query(20, ge=1, le=100)) -> list[dict]:
    frame = _sales_frame()
    return (
        frame.groupby(["product_id", "name", "category"], as_index=False)
        .agg(revenue=("revenue", "sum"), units=("quantity", "sum"))
        .nlargest(limit, "revenue")
        .to_dict("records")
    )


@app.get("/api/v1/inventory")
def inventory() -> list[dict]:
    file = settings.retailpulse_data_dir / "raw" / "inventory.csv"
    if not file.exists():
        return []
    frame = pd.read_csv(file)
    frame["risk"] = frame.quantity_on_hand <= frame.reorder_point
    return frame.to_dict("records")


@app.get("/api/v1/forecast")
def forecast() -> dict:
    future, metrics = forecast_daily(_sales_frame())
    return {
        "metrics": metrics,
        "forecast": future.assign(day=future.day.astype(str)).to_dict("records"),
    }


@app.get("/api/v1/anomalies")
def anomalies() -> list[dict]:
    return detect_anomalies(_sales_frame()).to_dict("records")


@app.get("/api/v1/pipelines")
def pipelines() -> list[dict]:
    report = settings.retailpulse_data_dir / "processed" / "quality_report.json"
    return [
        {
            "name": "batch_etl",
            "status": "succeeded" if report.exists() else "not_run",
            "report": str(report),
        }
    ]


@app.get("/api/v1/streaming/metrics")
def streaming_metrics() -> dict:
    return {"events_processed": 0, "duplicates_dropped": 0, "dead_letters": 0, "mode": "local"}


@app.post("/api/v1/agent/chat")
def agent_chat(request: ChatRequest) -> dict:
    from retailpulse.agents.tools import answer_question

    return answer_question(request.question, _sales_frame())

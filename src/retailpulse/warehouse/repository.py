"""SQLite repository used by the local API and dashboard."""

import sqlite3
from pathlib import Path

import pandas as pd


class AnalyticsRepository:
    """Small repository with parameterized SQL and deterministic fallback data."""

    def __init__(self, db_path: Path):
        self.db_path = db_path

    def connection(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(self.db_path)

    def load_processed(self, processed: Path) -> None:
        """Load the analytical fact table into SQLite."""
        file = processed / "sales_fact.parquet"
        sales = (
            pd.read_parquet(file) if file.exists() else pd.read_csv(processed / "sales_fact.csv")
        )
        with self.connection() as conn:
            sales.to_sql("sales_fact", conn, if_exists="replace", index=False)

    def overview(self) -> dict:
        with self.connection() as conn:
            row = conn.execute(
                "SELECT COUNT(*), COALESCE(SUM(revenue), 0), "
                "COUNT(DISTINCT product_id) FROM sales_fact"
            ).fetchone()
        return {"transactions": row[0], "revenue": round(row[1], 2), "products": row[2]}

    def sales(self, limit: int = 100) -> list[dict]:
        with self.connection() as conn:
            frame = pd.read_sql_query(
                "SELECT date(transaction_ts) AS day, SUM(revenue) AS revenue, "
                "SUM(quantity) AS units "
                "FROM sales_fact GROUP BY day ORDER BY day DESC LIMIT ?",
                conn,
                params=(limit,),
            )
        return frame.to_dict("records")

    def products(self, limit: int = 20) -> list[dict]:
        with self.connection() as conn:
            frame = pd.read_sql_query(
                "SELECT product_id, name, category, SUM(revenue) AS revenue, "
                "SUM(quantity) AS units "
                "FROM sales_fact GROUP BY product_id, name, category ORDER BY revenue DESC LIMIT ?",
                conn,
                params=(limit,),
            )
        return frame.to_dict("records")

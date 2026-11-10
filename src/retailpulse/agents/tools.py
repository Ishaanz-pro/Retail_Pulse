"""Allowlisted analytics tools and deterministic agent mode."""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def get_sales_summary(frame: pd.DataFrame) -> dict:
    return {
        "revenue": round(float(frame.revenue.sum()), 2),
        "units": int(frame.quantity.sum()),
        "transactions": len(frame),
    }


def get_product_performance(frame: pd.DataFrame, limit: int = 5) -> list[dict]:
    return (
        frame.groupby(["product_id", "name"], as_index=False)
        .revenue.sum()
        .nlargest(limit, "revenue")
        .to_dict("records")
    )


def answer_question(question: str, frame: pd.DataFrame) -> dict:
    """Return data-backed findings; Gemini integration can be added behind this interface."""
    lowered = question.lower()
    if "product" in lowered or "revenue" in lowered:
        result = get_product_performance(frame)
        summary = "Top products by revenue are " + ", ".join(item["name"] for item in result)
    else:
        result = get_sales_summary(frame)
        summary = (
            f"Sales total {result['revenue']:.2f} across {result['transactions']} transactions."
        )
    logger.info(
        "agent_tool_call question_category=%s",
        "products" if isinstance(result, list) else "summary",
    )
    return {
        "mode": "mock",
        "answer": summary,
        "data": result,
        "sources": ["sales_fact"],
        "recommendation": (
            "Validate this finding against current operational context before acting."
        ),
    }

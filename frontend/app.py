"""Recruiter-facing Streamlit portfolio dashboard for RetailPulse."""

# CSS and Streamlit layout declarations are intentionally readable in place.
# ruff: noqa: E501

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from retailpulse.api.main import _sales_frame
from retailpulse.ml.models import detect_anomalies, forecast_daily

st.set_page_config(
    page_title="RetailPulse | Data Intelligence Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    :root { --ink:#172033; --muted:#667085; --navy:#101828; --blue:#1570EF; --mint:#12B76A; --line:#EAECF0; }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: var(--ink); }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; letter-spacing: -0.02em; }
    h1 { font-size: 2.45rem !important; color: var(--navy); }
    h2 { font-size: 1.45rem !important; margin-top: 1.5rem; }
    .hero { background: linear-gradient(120deg,#101828 0%,#1D2939 62%,#175CD3 100%);
            color:white; padding:2.2rem 2.4rem; border-radius:20px; margin-bottom:1.4rem;
            box-shadow:0 12px 30px rgba(16,24,40,.16); }
    .hero h1 { color:white !important; margin:0 0 .45rem 0; font-size:2.8rem !important; }
    .hero p { color:#D0D5DD; font-size:1.06rem; max-width:790px; margin:0; line-height:1.6; }
    .eyebrow { color:#84CAFF; text-transform:uppercase; font-weight:700; font-size:.75rem; letter-spacing:.12em; }
    .pill { display:inline-block; padding:.32rem .68rem; border-radius:999px; margin:.8rem .35rem 0 0;
            background:rgba(255,255,255,.12); color:#F2F4F7; font-size:.78rem; }
    .card { border:1px solid var(--line); border-radius:14px; padding:1.1rem 1.15rem; background:#fff;
            min-height:128px; box-shadow:0 2px 6px rgba(16,24,40,.03); }
    .card h3 { font-size:1rem; margin:.25rem 0 .55rem; }
    .card p { color:var(--muted); font-size:.88rem; line-height:1.45; margin:0; }
    .status { color:#067647; background:#ECFDF3; border-radius:999px; padding:.25rem .55rem;
              font-size:.75rem; font-weight:700; }
    .section-note { color:var(--muted); margin-top:-.6rem; }
    [data-testid="stMetric"] { border:1px solid var(--line); padding:1rem; border-radius:14px;
                                background:#fff; box-shadow:0 2px 6px rgba(16,24,40,.03); }
    [data-testid="stSidebar"] { border-right:1px solid var(--line); }
    </style>
    """,
    unsafe_allow_html=True,
)

try:
    frame = _sales_frame()
except Exception as exc:
    st.error("Analytics data is not available yet. Run the data and batch commands from the README.")
    st.exception(exc)
    st.stop()

frame["transaction_ts"] = pd.to_datetime(frame["transaction_ts"])
frame["day"] = frame["transaction_ts"].dt.date
daily = frame.groupby("day", as_index=False).agg(revenue=("revenue", "sum"), units=("quantity", "sum"))
product_summary = (
    frame.groupby(["product_id", "name", "category"], as_index=False)
    .agg(revenue=("revenue", "sum"), units=("quantity", "sum"))
    .sort_values("revenue", ascending=False)
)
anomalies = detect_anomalies(frame)
future, metrics = forecast_daily(frame)

with st.sidebar:
    st.markdown("## RetailPulse")
    st.caption("Enterprise retail intelligence portfolio")
    st.markdown("---")
    page = st.radio(
        "Explore the platform",
        ["Executive overview", "Sales & products", "Forecasting & anomalies", "Platform story"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown("**Demo status**")
    st.markdown('<span class="status">● Local data pipeline ready</span>', unsafe_allow_html=True)
    st.caption("Synthetic data only · No customer PII")
    st.markdown("---")
    st.caption("Built with Python · FastAPI · Pandas · scikit-learn · Streamlit · GCP-ready")

st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">RetailPulse · Data intelligence platform</div>
      <h1>From retail events to confident decisions.</h1>
      <p>A production-minded portfolio project for ingesting, validating, analyzing, and
      forecasting retail operations — with a local-first path and an opt-in Google Cloud architecture.</p>
      <span class="pill">50K synthetic transactions</span>
      <span class="pill">Measured ML evaluation</span>
      <span class="pill">Controlled analytics agent</span>
      <span class="pill">Cloud-ready architecture</span>
    </div>
    """,
    unsafe_allow_html=True,
)

if page == "Executive overview":
    st.header("Executive overview")
    st.markdown('<p class="section-note">A live view of the generated analytical dataset and model outputs.</p>', unsafe_allow_html=True)
    cols = st.columns(4)
    cols[0].metric("Revenue", f"${frame.revenue.sum():,.0f}", "Synthetic sales fact")
    cols[1].metric("Transactions", f"{len(frame):,}", "Validated records")
    cols[2].metric("Units sold", f"{frame.quantity.sum():,}", "Across 100 products")
    cols[3].metric("Flagged days", f"{int(anomalies.anomaly.sum())}", "Isolation Forest")

    left, right = st.columns([1.55, 1])
    with left:
        st.subheader("Revenue trend")
        chart = px.area(daily, x="day", y="revenue", color_discrete_sequence=["#1570EF"])
        chart.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), yaxis_title="Revenue", xaxis_title=None)
        st.plotly_chart(chart, use_container_width=True)
    with right:
        st.subheader("Top products")
        chart = px.bar(
            product_summary.head(7).sort_values("revenue"),
            x="revenue",
            y="name",
            orientation="h",
            color="revenue",
            color_continuous_scale=["#B2DDFF", "#1570EF"],
        )
        chart.update_layout(height=350, showlegend=False, coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(chart, use_container_width=True)

    st.subheader("What this demonstrates")
    cards = st.columns(4)
    for column, title, copy in zip(
        cards,
        ["Reliable ingestion", "Decision-ready analytics", "Measured ML", "Responsible AI"],
        [
            "Schema validation, duplicate detection, referential integrity, and quality reports.",
            "Fact and dimension tables, parameterized SQL, API contracts, and dashboard views.",
            "Time-based evaluation with MAE, RMSE, MAPE, plus explainable anomaly scores.",
            "Allowlisted tools, source references, mock mode, and no arbitrary SQL exposure.",
        ],
        strict=True,
    ):
        column.markdown(f'<div class="card"><h3>{title}</h3><p>{copy}</p></div>', unsafe_allow_html=True)

elif page == "Sales & products":
    st.header("Sales & product intelligence")
    st.markdown('<p class="section-note">Explore performance by product category and sales volume.</p>', unsafe_allow_html=True)
    category = frame.groupby("category", as_index=False).agg(revenue=("revenue", "sum"), units=("quantity", "sum"))
    left, right = st.columns(2)
    with left:
        fig = px.pie(category, values="revenue", names="category", hole=.55, color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(height=350, margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        fig = px.scatter(product_summary, x="units", y="revenue", color="category", hover_name="name", size="units")
        fig.update_layout(height=350, margin=dict(l=0, r=0, t=20, b=0), xaxis_title="Units sold", yaxis_title="Revenue")
        st.plotly_chart(fig, use_container_width=True)
    st.subheader("Product ranking")
    st.dataframe(
        product_summary.head(20).style.format({"revenue": "${:,.2f}", "units": "{:,.0f}"}),
        use_container_width=True,
        hide_index=True,
    )

elif page == "Forecasting & anomalies":
    st.header("Forecasting & anomaly detection")
    st.markdown('<p class="section-note">Model results are computed from the current local dataset — not fabricated benchmarks.</p>', unsafe_allow_html=True)
    metric_cols = st.columns(3)
    metric_cols[0].metric("MAE", f"{metrics['mae']:.2f}", "Holdout error")
    metric_cols[1].metric("RMSE", f"{metrics['rmse']:.2f}", "Holdout error")
    metric_cols[2].metric("MAPE", f"{metrics['mape']:.2f}%", "Holdout error")
    left, right = st.columns([1.4, 1])
    with left:
        st.subheader("Next 7-day demand forecast")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily.day.tail(30), y=daily.quantity.tail(30), name="Actual units", line=dict(color="#667085")))
        fig.add_trace(go.Scatter(x=future.day, y=future.forecast_quantity, name="Forecast", line=dict(color="#1570EF", width=3, dash="dash")))
        fig.update_layout(height=360, margin=dict(l=0, r=0, t=10, b=0), yaxis_title="Units")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("Detected unusual activity")
        flagged = anomalies.query("anomaly").sort_values("anomaly_score")
        st.dataframe(flagged[["day", "quantity", "anomaly_score"]], use_container_width=True, hide_index=True)
        st.caption("Isolation Forest flags observations that differ from the learned daily sales distribution.")

else:
    st.header("How RetailPulse is engineered")
    st.markdown('<p class="section-note">The project is designed to be easy to review, run locally, and extend to Google Cloud.</p>', unsafe_allow_html=True)
    columns = st.columns(3)
    for column, title, copy in zip(
        columns,
        ["1 · Ingest & govern", "2 · Transform & learn", "3 · Serve & explain"],
        [
            "Synthetic CSV sources and event streams enter through typed schemas. Quality checks report accepted, rejected, duplicate, and referential-integrity counts.",
            "Batch ETL produces analytical facts. Forecasting uses time-based holdouts; anomaly detection emits measurable scores and flags.",
            "FastAPI serves validated views. Streamlit visualizes the same data. The agent uses controlled tools and includes source references.",
        ],
        strict=True,
    ):
        column.markdown(f'<div class="card"><h3>{title}</h3><p>{copy}</p></div>', unsafe_allow_html=True)
    st.subheader("Technology map")
    tech = pd.DataFrame(
        [
            ["Ingestion", "Python, Pydantic, Pandas", "Implemented"],
            ["Processing", "Batch ETL, Parquet, SQLite", "Implemented"],
            ["Streaming", "Event contracts, local windowing, Beam-ready", "Implemented locally"],
            ["ML", "scikit-learn, seasonal baseline", "Measured locally"],
            ["Serving", "FastAPI, OpenAPI, Streamlit", "Implemented"],
            ["Cloud path", "GCS, BigQuery, Pub/Sub, Dataflow, Cloud Run", "Opt-in configuration"],
        ],
        columns=["Layer", "Technology", "Status"],
    )
    st.dataframe(tech, use_container_width=True, hide_index=True)
    st.info("Recruiter note: every metric shown above is derived from reproducible synthetic data. Cloud resources are intentionally not provisioned automatically.")

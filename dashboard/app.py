import streamlit as st
import duckdb
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="CTV Fraud Analytics",
    page_icon="🛡️",
    layout="wide"
)

# =========================
# DATA LOAD
# =========================

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
APP_DATA_DIR = PROJECT_ROOT / "app_data"


@st.cache_data
def load_parquet(filename: str):
    path = APP_DATA_DIR / filename
    return duckdb.sql(f"""
        SELECT *
        FROM read_parquet('{path.as_posix()}')
    """).df()


overall_df = load_parquet("overall.parquet")
detector_summary_df = load_parquet("detector_summary.parquet")
sankey_df = load_parquet("sankey.parquet")
examples_df = load_parquet("examples.parquet")

overall = overall_df.iloc[0]

total_auctions = overall["total_auctions"]
flagged_auctions = overall["flagged_auctions"]
flagged_auctions = overall["flagged_auctions"]
active_detectors = len(detector_summary_df)
flag_rate = overall["pct_flagged"]

# Rendering rules
HIDDEN_DETECTORS = ["Deal Anomalies"]

detector_summary_render_df = detector_summary_df[
    ~detector_summary_df["detector"].isin(HIDDEN_DETECTORS)
].copy()

examples_render_df = examples_df[
    ~examples_df["detector"].isin(HIDDEN_DETECTORS)
].copy()

# =========================
# STYLE
# =========================

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

.metric-card {
    background: #ffffff;
    border: 1px solid #e6e8ec;
    border-radius: 16px;
    padding: 20px 22px;
    box-shadow: 0 1px 3px rgba(16,24,40,.06);
}

.metric-label {
    color: #667085;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 6px;
}

.metric-value {
    color: #101828;
    font-size: 30px;
    font-weight: 700;
    line-height: 1.1;
}

.metric-help {
    color: #98a2b3;
    font-size: 12px;
    margin-top: 8px;
}

.section-title {
    font-size: 22px;
    font-weight: 700;
    color: #101828;
    margin-top: 24px;
}

.section-subtitle {
    color: #667085;
    font-size: 14px;
    margin-bottom: 18px;
}
</style>
""", unsafe_allow_html=True)


# =========================
# SECTION 1 — EXEC SUMMARY
# =========================

st.markdown("# Peer 39 - CTV Fraud Analytics")
st.markdown(
    "Suspicious CTV auction patterns across detector outputs."
)

st.markdown("<hr>", unsafe_allow_html=True)

st.markdown(
    '<div class="section-title">Executive Summary</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-subtitle">High-level fraud signal concentration and investigation scope.</div>',
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Auctions Analyzed</div>
        <div class="metric-value">{total_auctions/1_000_000:.0f}M</div>
        <div class="metric-help">Full CTV auction sample</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Flagged Auctions</div>
<div class="metric-value">{flagged_auctions:,}</div>
<div class="metric-help">Distinct auctions requiring investigation</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Active Detectors</div>
        <div class="metric-value">{active_detectors}</div>
        <div class="metric-help">Fraud signals represented</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Observed Flag Rate</div>
        <div class="metric-value">{flag_rate:.2f}%</div>
        <div class="metric-help">Flagged Auctions / auctions analyzed</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# SECTION 2 — DETECTOR BREAKDOWN
# =========================

left, right = st.columns([2.4, 1])

with left:
    st.markdown('<div class="section-title">Detector Breakdown</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Core fraud signals ranked by suspicious auction volume.</div>',
        unsafe_allow_html=True
    )

    detector_summary_viz_df = detector_summary_render_df.copy()
    detector_summary_viz_df["category"] = detector_summary_viz_df["category"].replace({
        "Both": "SIVT"
    })

    detector_chart_df = detector_summary_viz_df[
        ~detector_summary_viz_df["detector"].isin(["App Integrity", "Deal Integrity"])
    ].sort_values("flagged_auctions", ascending=True)

    category_colors = {
        "GIVT": "#87A96B",
        "SIVT": "#FFA500",
    }

    fig = px.bar(
        detector_chart_df,
        x="flagged_auctions",
        y="detector",
        orientation="h",
        color="category",
        color_discrete_map=category_colors,
        text="pct_total_auctions",
        labels={
            "flagged_auctions": "Flagged Auctions",
            "detector": "",
            "pct_total_auctions": "% of Auctions",
            "category": "Category",
        },
    )

    fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside",
        cliponaxis=False,
    )

    fig.update_layout(
        height=430,
        margin=dict(l=10, r=40, t=10, b=10),
        xaxis_title=None,
        yaxis_title=None,
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend_title_text="",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
    )

    fig.update_xaxes(
        showticklabels=False,
        showgrid=False,
        zeroline=False,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False},
    )

with right:
    st.markdown('<div class="section-title">Investigations & Prioritization Detectors</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Inventory-level signals used to prioritize follow-up.</div>',
        unsafe_allow_html=True
    )

    priority_df = detector_summary_render_df[
        detector_summary_render_df["detector"].isin(["App Integrity", "Deal Integrity"])
    ].copy()

    for _, row in priority_df.iterrows():
        st.markdown(f"""
        <div class="metric-card" style="margin-bottom: 14px;">
            <div class="metric-label">{row["detector"]}</div>
            <div class="metric-value">{int(row["flagged_auctions"]):,}</div>
            <div class="metric-help">{row["pct_total_auctions"]:.2f}% of analyzed auctions</div>
        </div>
        """, unsafe_allow_html=True)

# =========================
# SECTION 3 — DETECTOR DRILLDOWN
# =========================

st.markdown('<div class="section-title">Detector Drilldown</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">Select a detector to inspect affected auctions and supporting evidence.</div>',
    unsafe_allow_html=True
)

detector_options = (
    detector_summary_render_df
    .sort_values("flagged_auctions", ascending=False)["detector"]
    .tolist()
)

selected_detector = st.selectbox(
    "Detector",
    detector_options,
    label_visibility="collapsed"
)

selected_summary = detector_summary_render_df[
    detector_summary_render_df["detector"] == selected_detector
].iloc[0]

drilldown_df = examples_render_df[
    examples_render_df["detector"] == selected_detector
].copy()

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Flagged Auctions</div>
        <div class="metric-value">{int(selected_summary["flagged_auctions"]):,}</div>
        <div class="metric-help">Distinct auctions triggered</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Share of Traffic</div>
        <div class="metric-value">{selected_summary["pct_total_auctions"]:.2f}%</div>
        <div class="metric-help">Of all analyzed auctions</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    category = selected_summary["category"]
    if category == "Both":
        category = "SIVT"

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Category</div>
        <div class="metric-value">{category}</div>
        <div class="metric-help">Business fraud taxonomy</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("### Evidence Sample")

st.dataframe(
    drilldown_df.head(100),
    use_container_width=True,
    hide_index=True
)
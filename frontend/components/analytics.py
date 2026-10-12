import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from utils.helpers import calculate_risk_score, get_risk_label
from utils.pdf_generator import generate_pdf_report, REPORTLAB_AVAILABLE

def render_analytics():
    st.title("Advanced Analytics")
    st.caption("Aggregated risk statistics, category analysis, and trend visualizations.")

    if st.session_state.results is None:
        st.info("No contract data analyzed yet. Please submit a document on the Dashboard first.")
        return

    df = pd.DataFrame(st.session_state.results)

    col1, col2 = st.columns(2)

    with col1:
        fig_donut = go.Figure(go.Pie(
            labels=df["risk"].value_counts().index,
            values=df["risk"].value_counts().values,
            hole=0.5,
            marker_colors=["#dc2626", "#d97706", "#16a34a"]
        ))
        fig_donut.update_layout(title="Risk Severity Distribution", margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_donut, use_container_width=True)

    with col2:
        grouped = df.groupby(["type", "risk"]).size().reset_index(name="count")
        fig_bar = go.Figure()
        for r_level in ["HIGH", "MEDIUM", "LOW"]:
            sub = grouped[grouped["risk"] == r_level]
            if not sub.empty:
                fig_bar.add_trace(go.Bar(name=r_level, x=sub["type"], y=sub["count"]))

        fig_bar.update_layout(barmode="stack", title="Category Distribution vs Severity", margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("Executive Report Export")
    if REPORTLAB_AVAILABLE:
        pdf_file = generate_pdf_report(df, calculate_risk_score(df), get_risk_label(calculate_risk_score(df)))
        st.download_button("Download Executive PDF Report", pdf_file, "contract_risk_report.pdf", "application/pdf")
    else:
        st.warning("Install `reportlab` package to enable PDF exports.")
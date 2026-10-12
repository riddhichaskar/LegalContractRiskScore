import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from utils.helpers import calculate_risk_score, get_risk_label

def render_header_summary():
    has_results = st.session_state.results is not None
    results = st.session_state.results if has_results else []
    df = pd.DataFrame(results)

    score = calculate_risk_score(df) if has_results else 0
    label = get_risk_label(score) if has_results else "NO DATA"

    high_c = len(df[df["risk"] == "HIGH"]) if has_results else 0
    med_c = len(df[df["risk"] == "MEDIUM"]) if has_results else 0
    low_c = len(df[df["risk"] == "LOW"]) if has_results else 0
    total_c = len(df) if has_results else 0

    with st.container():
        head_col1, head_col2 = st.columns([1, 2])

        with head_col1:
            st.markdown(
                f"""
                <div class="executive-summary-card">
                    <span style="font-size: 13px; font-weight: 600; color: var(--text-muted);">OVERALL CONTRACT RISK INDEX</span>
                    <div style="display: flex; align-items: baseline; gap: 12px; margin-top: 4px;">
                        <span style="font-size: 36px; font-weight: 800; color: var(--text-main);">{score} <span style="font-size: 20px; color: var(--text-muted);">/ 100</span></span>
                        <span class="badge badge-{'high' if score >= 70 else ('medium' if score >= 45 else 'low')}">{label}</span>
                    </div>
                    <div style="margin-top: 8px; font-size: 13px; font-weight: 600; color: {'var(--risk-high)' if high_c > 0 else 'var(--text-muted)'};">
                        {'🚨 ' + str(high_c) + ' High Risk Clauses require immediate attention' if high_c > 0 else 'No critical high-risk clauses detected'}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with head_col2:
            st.markdown("##### Severity Distribution")
            if total_c > 0:
                # Stacked Horizontal Distribution Bar
                fig = go.Figure()
                fig.add_trace(go.Bar(y=["Risk"], x=[high_c], name="High", orientation="h", marker_color="#dc2626"))
                fig.add_trace(go.Bar(y=["Risk"], x=[med_c], name="Medium", orientation="h", marker_color="#d97706"))
                fig.add_trace(go.Bar(y=["Risk"], x=[low_c], name="Low", orientation="h", marker_color="#16a34a"))

                fig.update_layout(
                    barmode="stack",
                    height=60,
                    margin=dict(l=0, r=0, t=0, b=0),
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    xaxis=dict(showgrid=False, visible=False),
                    yaxis=dict(showgrid=False, visible=False),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})
                st.caption(f"Metadata: **{st.session_state.uploaded_filename or 'Direct Text Input'}** | Total Clauses Analyzed: **{total_c}**")
            else:
                st.info("Submit or upload a contract below to generate risk distribution analytics.")
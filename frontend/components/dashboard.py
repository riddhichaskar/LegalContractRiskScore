import requests
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from utils.helpers import (
    clean_text,
    calculate_risk_score,
    get_risk_label,
    extract_text_from_file
)

API_URL = "http://127.0.0.1:8000/predict"

def render_dashboard():
    st.title("Contract Risk Intelligence")
    st.caption("Executive overview of contract risk assessment, critical findings, and priority actions.")

    has_results = st.session_state.results is not None
    results = st.session_state.results if has_results else []
    df = pd.DataFrame(results)

    score = calculate_risk_score(df) if has_results else 0
    label = get_risk_label(score) if has_results else "NO DATA"

    high_c = len(df[df["risk"] == "HIGH"]) if has_results else 0
    med_c = len(df[df["risk"] == "MEDIUM"]) if has_results else 0
    low_c = len(df[df["risk"] == "LOW"]) if has_results else 0
    total_c = len(df) if has_results else 0

    # Executive Summary Card
    with st.container():
        summary_col1, summary_col2 = st.columns([1, 2])

        with summary_col1:
            st.markdown(
                f"""
                <div class="executive-summary-card">
                    <span style="font-size: 13px; font-weight: 600; color: var(--text-muted);">OVERALL RISK SCORE</span>
                    <div style="display: flex; align-items: baseline; gap: 12px; margin-top: 4px;">
                        <span style="font-size: 38px; font-weight: 800; color: var(--text-main);">{score} <span style="font-size: 18px; color: var(--text-muted);">/ 100</span></span>
                        <span class="badge badge-{'high' if score >= 70 else ('medium' if score >= 45 else 'low')}">{label}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with summary_col2:
            st.markdown("##### Severity Distribution Context")
            if total_c > 0:
                fig = go.Figure()
                fig.add_trace(go.Bar(y=["Severity"], x=[high_c], name=f"High ({high_c})", orientation="h", marker_color="#dc2626"))
                fig.add_trace(go.Bar(y=["Severity"], x=[med_c], name=f"Medium ({med_c})", orientation="h", marker_color="#d97706"))
                fig.add_trace(go.Bar(y=["Severity"], x=[low_c], name=f"Low ({low_c})", orientation="h", marker_color="#16a34a"))

                fig.update_layout(
                    barmode="stack",
                    height=55,
                    margin=dict(l=0, r=0, t=0, b=0),
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    xaxis=dict(showgrid=False, visible=False),
                    yaxis=dict(showgrid=False, visible=False),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})
                st.caption(f"Contract: **{st.session_state.uploaded_filename or 'Text Submission'}** | Total Clauses: **{total_c}**")
            else:
                st.info("No active contract analyzed yet. Ingest a document below to populate metrics.")

    st.write("")

    # High Risk Attention Alert Banner
    if high_c > 0:
        st.markdown(
            f"""
            <div class="alert-card-high">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="font-size: 16px; color: var(--risk-high);">🚨 {high_c} High-Risk Clauses Require Immediate Attention</strong>
                        <div style="font-size: 14px; color: var(--text-main); margin-top: 2px;">Review identified exposure points before granting contract approval.</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.write("")

    col_left, col_right = st.columns([1, 1])

    # Left Column: Document Ingestion Control
    with col_left:
        st.subheader("Document Ingestion")
        
        if has_results:
            st.success(f"Active Document: {st.session_state.uploaded_filename or 'Text Submission'}")
            st.caption(f"{total_c} clauses parsed and stored in active session.")
            
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("Open Document Viewer", width='stretch'):
                    st.session_state.selected_nav = "Document Viewer"
                    st.rerun()
            with btn_col2:
                if st.button("Inspect All Clauses", type="primary", width='stretch'):
                    st.session_state.selected_nav = "Clause Inspector"
                    st.rerun()
                    
            st.write("---")
            st.caption("Upload a new file to overwrite current analysis:")

        uploaded_file = st.file_uploader("Upload Contract", type=["pdf", "docx", "txt"], label_visibility="collapsed")
        if uploaded_file is not None and uploaded_file.name != st.session_state.uploaded_filename:
            try:
                st.session_state.contract_text = extract_text_from_file(uploaded_file)
                st.session_state.uploaded_filename = uploaded_file.name
                st.session_state.results = None
                st.rerun()
            except Exception as e:
                st.error(f"File extraction error: {str(e)}")

        if not has_results:
            st.session_state.contract_text = st.text_area(
                "Paste Contract Text",
                value=st.session_state.contract_text,
                height=180,
                placeholder="Or paste full contract text here...",
                label_visibility="collapsed"
            )

            if st.button("Analyze Contract", type="primary", width='stretch'):
                if not st.session_state.contract_text.strip():
                    st.warning("Please upload a file or enter contract text before analyzing.")
                else:
                    with st.spinner("Analyzing document..."):
                        try:
                            resp = requests.post(API_URL, json={"text": st.session_state.contract_text}, timeout=120)
                            if resp.status_code == 200:
                                st.session_state.results = resp.json()["results"]
                                st.success("Analysis complete!")
                                st.rerun()
                            else:
                                st.error(f"Backend API Error: {resp.status_code}")
                        except requests.exceptions.ConnectionError:
                            st.error("Could not reach FastAPI server on port 8000.")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

    # Right Column: Key Findings Briefing
    with col_right:
        st.subheader("Key Findings Summary")
        if has_results:
            high_df = df[df["risk"] == "HIGH"]
            med_df = df[df["risk"] == "MEDIUM"]

            if not high_df.empty:
                st.markdown("##### 🚨 Critical Exposure Items")
                for idx, row in high_df.iterrows():
                    with st.container():
                        st.markdown(f"<span class='badge badge-high'>HIGH</span> <b>{row['type']}</b>", unsafe_allow_html=True)
                        st.write(clean_text(row['clause'])[:140] + "...")
                        if st.button(f"Inspect Clause #{idx+1}", key=f"dash_inspect_{idx}"):
                            st.session_state.target_clause_idx = idx
                            st.session_state.selected_nav = "Clause Inspector"
                            st.rerun()
                        st.write("---")
            elif not med_df.empty:
                st.markdown("##### ⚠️ Moderate Risk Items")
                for idx, row in med_df.head(2).iterrows():
                    with st.container():
                        st.markdown(f"<span class='badge badge-medium'>MEDIUM</span> <b>{row['type']}</b>", unsafe_allow_html=True)
                        st.write(clean_text(row['clause'])[:140] + "...")
                        st.write("---")
            else:
                st.success("No high or moderate risk items detected in this document.")
        else:
            st.info("Key findings will populate here once a contract is analyzed.")
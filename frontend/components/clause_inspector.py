import pandas as pd
import streamlit as st
from utils.helpers import clean_text, highlight_keywords

def render_clause_inspector():
    st.title("Clause Inspector")
    st.caption("Deep-dive clause analysis, AI risk classification reasoning, and remediation workflow.")

    if st.session_state.results is None:
        st.info("No contract data analyzed yet. Submit a document on the Dashboard first.")
        return

    df = pd.DataFrame(st.session_state.results)
    total_contract_clauses = len(df)

    # Search & Filter Deck
    f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
    with f_col1:
        search_q = st.text_input("Search Clauses", placeholder="Search clause text, keywords, liabilities...")
    with f_col2:
        risk_f = st.selectbox("Risk Level", ["All", "HIGH", "MEDIUM", "LOW"])
    with f_col3:
        type_f = st.selectbox("Category", ["All"] + sorted(df["type"].dropna().unique().tolist()))

    filtered_df = df.copy()
    if search_q:
        query = search_q.lower()
        filtered_df = filtered_df[
            filtered_df["clause"].astype(str).str.lower().str.contains(query, na=False) |
            filtered_df["type"].astype(str).str.lower().str.contains(query, na=False) |
            filtered_df["explanation"].astype(str).str.lower().str.contains(query, na=False)
        ]
    if risk_f != "All":
        filtered_df = filtered_df[filtered_df["risk"] == risk_f]
    if type_f != "All":
        filtered_df = filtered_df[filtered_df["type"] == type_f]

    if filtered_df.empty:
        st.warning("No clauses match the specified search or filter criteria.")
        return

    total_filtered = len(filtered_df)

    # Clause Index Synchronization
    if "target_clause_idx" in st.session_state and st.session_state.target_clause_idx < total_filtered:
        current_idx = st.session_state.target_clause_idx
        del st.session_state.target_clause_idx
    else:
        current_idx = st.session_state.get("inspector_clause_idx", 0)

    if current_idx >= total_filtered:
        current_idx = 0

    # Top Control Deck: Quick-Jump Selector & Pagination Controls
    st.write("")
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1, 2, 1])
    
    with ctrl_col1:
        if st.button("← Previous Clause", disabled=(current_idx == 0), use_container_width=True):
            st.session_state.inspector_clause_idx = current_idx - 1
            st.rerun()

    with ctrl_col2:
        # Quick-Jump Selector
        clause_options = [
            f"Clause {i+1} of {total_filtered}: [{filtered_df.iloc[i]['risk']}] {filtered_df.iloc[i]['type']}"
            for i in range(total_filtered)
        ]
        selected_option = st.selectbox(
            "Quick Jump",
            options=clause_options,
            index=current_idx,
            label_visibility="collapsed"
        )
        new_idx = clause_options.index(selected_option)
        if new_idx != current_idx:
            st.session_state.inspector_clause_idx = new_idx
            st.rerun()

    with ctrl_col3:
        if st.button("Next Clause →", disabled=(current_idx == total_filtered - 1), use_container_width=True):
            st.session_state.inspector_clause_idx = current_idx + 1
            st.rerun()

    row = filtered_df.iloc[current_idx]
    original_clause_num = df[df["clause"] == row["clause"]].index[0] + 1 if "clause" in df else current_idx + 1
    
    # Review Status Tracking
    if "review_status" not in st.session_state:
        st.session_state.review_status = {}
    current_status = st.session_state.review_status.get(original_clause_num, "Pending Review")

    st.write("")

    # Card 1: Clause Header & Source Excerpt
    conf_pct = float(row.get("confidence", 0.0)) * 100
    badge_cls = f"badge-{row['risk'].lower()}"
    status_badge = "badge-high" if current_status == "Flagged for Legal Review" else ("badge-low" if current_status == "Marked as Reviewed" else "badge-medium")

    with st.container():
        st.markdown(
            f"""
            <div class="clause-card-container">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <span class="badge {badge_cls}">{row['risk']} RISK</span>
                        <span class="badge badge-neutral">{row['type']}</span>
                        <span style="font-size: 13px; color: var(--text-muted);" title="Classification confidence indicates how certain the AI model is about this clause's risk score.">
                            <b>{conf_pct:.0f}%</b> CONFIDENCE ℹ️
                        </span>
                    </div>
                    <div>
                        <span style="font-size: 12px; color: var(--text-muted); font-weight: 600;">STATUS:</span>
                        <span class="badge {status_badge}">{current_status}</span>
                    </div>
                </div>
                <div style="font-weight: 700; font-size: 16px; margin-bottom: 8px; color: var(--text-main);">
                    Clause {original_clause_num} of {total_contract_clauses}
                </div>
                <div class="excerpt-quote-box">
                    "{highlight_keywords(clean_text(row['clause']))}"
                </div>
                <div style="font-size: 12px; color: var(--text-muted); margin-top: 8px;">
                    💡 <i>Highlighted terms indicate key legal language contributing to this clause's risk classification.</i>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")

    # Card 2: AI Risk Assessment Reasoning & Recommended Action Workflows
    col_reasoning, col_action = st.columns(2)

    with col_reasoning:
        st.markdown("##### AI Risk Classification Reasoning")
        
        # Deep AI Explanation Components
        explanation = row.get("explanation", "This clause contains standard contractual terms requiring verification.")
        
        st.markdown(f"**Why {row['risk']} RISK?**")
        st.write(explanation)

        st.markdown("**Key Concern:**")
        if row["risk"] == "HIGH":
            st.write("Potential exposure to uncapped liabilities, strict penalties, or unilateral cancellation rights.")
        elif row["risk"] == "MEDIUM":
            st.write("Contains terms that may create operational or continuity risk without material breach.")
        else:
            st.write("Standard commercial language with low risk exposure.")

        st.markdown("**Business Impact:**")
        if row["risk"] == "HIGH":
            st.write("High financial exposure or potential loss of legal remedies during disputes.")
        elif row["risk"] == "MEDIUM":
            st.write("May require operational adjustments or notice period monitoring during service execution.")
        else:
            st.write("Minimal impact on day-to-day operations and legal standing.")

    with col_action:
        st.markdown("##### Recommended Action")

        # Specific Action Recommendation
        if row["risk"] == "HIGH":
            st.error("🚨 **Escalate to Legal Counsel:** Renegotiate terms or add liability caps prior to contract execution.")
        elif row["risk"] == "MEDIUM":
            st.warning("⚠️ **Standard Review Required:** Confirm operational feasibility with business stakeholders.")
        else:
            st.success("✅ **Acceptable As-Is:** Clause aligns with standard commercial practices.")

        recs = row.get("recommendations", [])
        if isinstance(recs, list) and recs:
            st.markdown("**Specific Recommendations:**")
            for r in recs:
                st.write(f"- {r}")

        st.write("---")
        st.markdown("**Take Remediation Action:**")
        
        act_btn1, act_btn2 = st.columns(2)
        with act_btn1:
            if st.button("🚩 Flag for Review", key=f"flag_btn_{original_clause_num}", type="primary" if row["risk"] == "HIGH" else "secondary", use_container_width=True):
                st.session_state.review_status[original_clause_num] = "Flagged for Legal Review"
                st.toast(f"Clause {original_clause_num} flagged for legal review!", icon="🚩")
                st.rerun()

        with act_btn2:
            if st.button("✓ Mark as Reviewed", key=f"rev_btn_{original_clause_num}", use_container_width=True):
                st.session_state.review_status[original_clause_num] = "Marked as Reviewed"
                st.toast(f"Clause {original_clause_num} marked as reviewed.", icon="✅")
                st.rerun()

    st.write("---")

    # Bottom Actions: Deep-Link Bridge & Related Context
    b_col1, b_col2 = st.columns([1, 1])
    with b_col1:
        if st.button("📄 Open in Document Viewer", use_container_width=True):
            st.session_state.active_clause_text = row["clause"]
            st.session_state.selected_nav = "Document Viewer"
            st.rerun()

    with b_col2:
        # Related Clause Categories
        related = df[(df["type"] == row["type"]) & (df["clause"] != row["clause"])]
        if not related.empty:
            st.caption(f"Related {row['type']} Clauses in Document: **{len(related)} other clause(s)** found.")
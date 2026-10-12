import pandas as pd
import streamlit as st
from utils.helpers import highlight_keywords

# Render detailed clause analysis view
def render_clause_view():
    st.title("Clause Analysis")
    st.caption("In-depth breakdown of flagged clauses and mitigation recommendations.")

    if st.session_state.results is None:
        st.info("No contract data analyzed yet. Please submit a contract on the Dashboard first.")
        return

    df = pd.DataFrame(st.session_state.results)

    high_risks = df[df["risk"] == "HIGH"]
    if high_risks.empty:
        st.info("No high-risk clauses found in the analyzed contract.")
        return

    idx = st.selectbox("Select Flagged Clause", range(len(high_risks)), format_func=lambda i: f"Clause {i+1}: {high_risks.iloc[i]['type']}")
    item = high_risks.iloc[idx]

    st.markdown(f"<span class='badge badge-high'>HIGH RISK</span> &nbsp; <b>Type: {item['type']}</b> &nbsp; (Confidence: {float(item['confidence']) * 100:.1f}%)", unsafe_allow_html=True)

    with st.container():
        st.markdown(f"### Text Content\n{highlight_keywords(item['clause'])}", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Risk Explanation")
        st.write(item.get("explanation", "No analysis provided."))

    with c2:
        st.subheader("Recommendations")
        recs = item.get("recommendations", [])
        if recs:
            for r in recs:
                st.write(f"- {r}")
        else:
            st.write("No specific recommendations generated for this clause.")
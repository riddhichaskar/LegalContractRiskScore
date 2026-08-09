import streamlit as st
import requests
import re
import pandas as pd
import plotly.express as px

API_URL = "http://127.0.0.1:8000/predict"

st.set_page_config(page_title="Contract Risk Analyzer", layout="wide")

# =========================
# SESSION STATE (CRITICAL FIX)
# =========================
if "results" not in st.session_state:
    st.session_state.results = None

if "show_chart" not in st.session_state:
    st.session_state.show_chart = False


# =========================
# CLEAN TEXT
# =========================
def clean_text(text):
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# =========================
# HIGHLIGHT
# =========================
def highlight(text):
    keywords = ["penalty", "liable", "terminate", "fee", "interest", "warranty"]

    for word in keywords:
        text = re.sub(
            f"({word})",
            r"<span style='color:#ff4b4b; font-weight:bold;'>\1</span>",
            text,
            flags=re.IGNORECASE
        )
    return text


# =========================
# MAIN LAYOUT
# =========================
left, right = st.columns([1, 2])

# =========================
# LEFT SIDE (INPUT)
# =========================
with left:
    st.title("📄 Contract")

    contract_text = st.text_area(
        "Paste or Upload Contract",
        height=500,
        placeholder="Paste full contract here..."
    )

    analyze_btn = st.button("🚀 Analyze", use_container_width=True)

    if analyze_btn:
        if not contract_text.strip():
            st.warning("Please enter contract text")
        else:
            response = requests.post(API_URL, json={"text": contract_text})

            if response.status_code == 200:
                st.session_state.results = response.json()["results"]
                st.session_state.show_chart = False
            else:
                st.error("API Error")


# =========================
# RIGHT SIDE (DASHBOARD)
# =========================
with right:
    st.title("📊 Dashboard")

    if st.session_state.results:
        df = pd.DataFrame(st.session_state.results)

        high_df = df[df["risk"] == "HIGH"]
        med_df = df[df["risk"] == "MEDIUM"]
        low_df = df[df["risk"] == "LOW"]

        # =========================
        # ROW 1: CARDS
        # =========================
        c1, c2, c3 = st.columns(3)

        c1.markdown(
            f"""
            <div style="background:#ff4b4b20; padding:20px; border-radius:10px;">
            <h3>🔴 High Risk</h3>
            <h2>{len(high_df)}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        c2.markdown(
            f"""
            <div style="background:#ffa50020; padding:20px; border-radius:10px;">
            <h3>🟡 Medium Risk</h3>
            <h2>{len(med_df)}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        c3.markdown(
            f"""
            <div style="background:#2ecc7120; padding:20px; border-radius:10px;">
            <h3>🟢 Low Risk</h3>
            <h2>{len(low_df)}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        # =========================
        # ROW 2
        # =========================
        st.markdown("## 📑 Analysis of Risk")

        # =========================
        # GROUP FUNCTION
        # =========================
        def show_group(title, df_group, color, expanded=False):
            with st.expander(f"{title} ({len(df_group)})", expanded=expanded):
                for _, r in df_group.iterrows():
                    clause = highlight(clean_text(r["clause"]))

                    st.markdown(
                        f"""
                        <div style="border-left:4px solid {color};
                                    padding:10px;
                                    margin-bottom:10px;
                                    background:#f9f9f9;
                                    border-radius:6px;">
                        {clause}
                        <br><br>
                        <b>{r['type']}</b> — {r['explanation']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.progress(r["confidence"])

        # =========================
        # ROW 3–5
        # =========================
        show_group("🔴 HIGH RISK", high_df, "#ff4b4b", True)
        show_group("🟡 MEDIUM RISK", med_df, "#ffa500")
        show_group("🟢 LOW RISK", low_df, "#2ecc71")

        # =========================
        # ROW 6: BUTTONS
        # =========================
        st.markdown("---")

        b1, b2, b3 = st.columns(3)

        # DOWNLOAD CSV (NO RESET NOW)
        csv = df.to_csv(index=False).encode("utf-8")
        b1.download_button(
            "📥 Download CSV",
            csv,
            "contract_analysis.csv",
            "text/csv",
            use_container_width=True
        )

        # VISUALIZATION BUTTON
        if b2.button("📊 Visualization", use_container_width=True):
            st.session_state.show_chart = True

        # ADVANCED PLACEHOLDER
        if b3.button("🧠 Advanced Analysis", use_container_width=True):
            st.info("Coming soon...")


# =========================
# FULL-WIDTH VISUALIZATION 
# =========================
if st.session_state.show_chart and st.session_state.results:
    st.markdown("---")
    st.title("📊 Advanced Risk Analytics")

    df = pd.DataFrame(st.session_state.results)

    # =========================
    # ROW 1: DISTRIBUTION + COMPOSITION
    # =========================
    col1, col2 = st.columns(2)

    # -------------------------
    # PIE CHART (RISK SHARE)
    # -------------------------
    with col1:
        fig1 = px.pie(
            df,
            names="risk",
            title="Overall Risk Distribution",
            color="risk",
            hole=0.5,  # donut style
            color_discrete_map={
                "HIGH": "#ff4b4b",
                "MEDIUM": "#ffa500",
                "LOW": "#2ecc71"
            }
        )

        fig1.update_traces(textinfo='percent+label')
        st.plotly_chart(fig1, use_container_width=True)

    # -------------------------
    # STACKED BAR (TYPE vs RISK)
    # -------------------------
    with col2:
        type_risk = df.groupby(["type", "risk"]).size().reset_index(name="count")

        fig2 = px.bar(
            type_risk,
            x="type",
            y="count",
            color="risk",
            title="Clause Type vs Risk Distribution",
            barmode="stack",
            text="count",
            color_discrete_map={
                "HIGH": "#ff4b4b",
                "MEDIUM": "#ffa500",
                "LOW": "#2ecc71"
            }
        )

        fig2.update_layout(
            xaxis_title="Clause Type",
            yaxis_title="Number of Clauses",
            legend_title="Risk Level"
        )

        st.plotly_chart(fig2, use_container_width=True)

    
    # =========================
    # ROW 3: INSIGHTS (AUTO SUMMARY)
    # =========================
    st.markdown("### 🧠 Key Insights")

    high_count = len(df[df["risk"] == "HIGH"])
    total = len(df)

    top_risky_types = (
        df[df["risk"] == "HIGH"]["type"]
        .value_counts()
        .head(3)
        .index.tolist()
    )

    st.markdown(
        f"""
        - 🔴 **{high_count} out of {total} clauses are HIGH RISK**
        - ⚠️ Most risky clause types: **{", ".join(top_risky_types)}**
        - 📊 Risk is concentrated in specific clause categories
        - 🎯 Model confidence is higher for structured clauses (penalty/liability)
        """
    )
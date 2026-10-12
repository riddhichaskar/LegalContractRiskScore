import streamlit as st
import requests
import re
import pandas as pd
import plotly.express as px
from io import BytesIO
from textwrap import dedent

# Optional PDF Dependency
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Configuration
API_URL = "http://127.0.0.1:8000/predict"

st.set_page_config(
    page_title="Contract Risk Analyzer",
    layout="wide"
)

# Session State
if "results" not in st.session_state:
    st.session_state.results = None

if "show_chart" not in st.session_state:
    st.session_state.show_chart = False

# Clean Text
def clean_text(text):
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# HTML Escape
def escape_html(text):
    text = str(text)
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text

# Highlight Important Keywords
def highlight(text):
    keywords = [
        "penalty", "liable", "liability", "terminate", "termination",
        "fee", "interest", "warranty", "breach", "damages", "payment",
        "confidential", "confidentiality", "indemnity", "default",
        "intellectual property",
    ]
    text = escape_html(text)
    for word in keywords:
        pattern = re.escape(word)
        text = re.sub(
            f"({pattern})",
            r"<span style='color:#d62828; font-weight:700;'>\1</span>",
            text,
            flags=re.IGNORECASE
        )
    return text

# Risk Score Calculation
def calculate_risk_score(df):
    if df.empty:
        return 0
    weights = {"HIGH": 100, "MEDIUM": 60, "LOW": 20}
    score = df["risk"].map(weights).fillna(0).mean()
    return round(score)

def get_risk_label(score):
    if score >= 70:
        return "HIGH RISK"
    elif score >= 45:
        return "MODERATE RISK"
    else:
        return "LOW RISK"

def get_risk_color(score):
    if score >= 70:
        return "#d62828"
    elif score >= 45:
        return "#e09f00"
    else:
        return "#2a9d62"

# PDF Report Generation
def create_pdf(df, risk_score, risk_label):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleCustom", parent=styles["Title"], alignment=TA_CENTER, fontSize=20, spaceAfter=20
    )
    heading_style = ParagraphStyle(
        "HeadingCustom", parent=styles["Heading2"], fontSize=14, spaceBefore=12, spaceAfter=8
    )
    normal_style = ParagraphStyle(
        "NormalCustom", parent=styles["Normal"], fontSize=9, leading=13
    )

    story = []
    story.append(Paragraph("Legal Contract Risk Analysis Report", title_style))
    story.append(Paragraph(f"<b>Overall Risk Score:</b> {risk_score}/100", normal_style))
    story.append(Paragraph(f"<b>Risk Level:</b> {risk_label}", normal_style))
    story.append(Spacer(1, 15))

    high_count = len(df[df["risk"] == "HIGH"])
    medium_count = len(df[df["risk"] == "MEDIUM"])
    low_count = len(df[df["risk"] == "LOW"])
    total = len(df)

    story.append(Paragraph("Risk Summary", heading_style))
    summary_data = [
        ["Risk Level", "Number of Clauses"],
        ["HIGH", str(high_count)],
        ["MEDIUM", str(medium_count)],
        ["LOW", str(low_count)],
        ["TOTAL", str(total)]
    ]

    table = Table(summary_data, colWidths=[200, 150])
    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 7)
        ])
    )
    story.append(table)
    story.append(Spacer(1, 15))

    story.append(Paragraph("Clause Analysis", heading_style))

    for index, row in df.iterrows():
        clause = escape_html(clean_text(row["clause"]))
        explanation = escape_html(row.get("explanation", "No explanation available."))
        confidence = float(row["confidence"]) * 100

        text = (
            f"<b>Clause {index + 1}</b><br/>"
            f"<b>Risk:</b> {escape_html(row['risk'])}<br/>"
            f"<b>Type:</b> {escape_html(row['type'])}<br/>"
            f"<b>Confidence:</b> {confidence:.1f}%<br/>"
            f"<b>Clause:</b> {clause}<br/>"
            f"<b>Why is this risky?</b> {explanation}"
        )
        story.append(Paragraph(text, normal_style))
        story.append(Spacer(1, 10))

    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>Disclaimer:</b> This report provides AI-generated contract analysis and is not legal advice.", normal_style))

    doc.build(story)
    buffer.seek(0)
    return buffer

# Main Layout
left, right = st.columns([1, 2])

# Left Side — Contract Input
with left:
    st.title("Contract")
    contract_text = st.text_area(
        "Paste or Upload Contract",
        height=500,
        placeholder="Paste full contract here..."
    )
    analyze_btn = st.button("Analyze", use_container_width=True)

    if analyze_btn:
        if not contract_text.strip():
            st.warning("Please enter contract text.")
        else:
            try:
                response = requests.post(
                    API_URL,
                    json={"text": contract_text},
                    timeout=120
                )
                if response.status_code == 200:
                    st.session_state.results = response.json()["results"]
                    st.session_state.show_chart = False
                    st.success("Contract analyzed successfully.")
                else:
                    st.error(f"API Error: {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the FastAPI backend. Make sure the API is running on port 8000.")
            except requests.exceptions.Timeout:
                st.error("The analysis took too long. Please try again.")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")

# Right Side — Dashboard
with right:
    st.title("Dashboard")

    if st.session_state.results:
        df = pd.DataFrame(st.session_state.results)

        # Risk Counts
        high_df = df[df["risk"] == "HIGH"]
        medium_df = df[df["risk"] == "MEDIUM"]
        low_df = df[df["risk"] == "LOW"]

        high_count = len(high_df)
        medium_count = len(medium_df)
        low_count = len(low_df)
        total = len(df)

        # Overall Risk Score
        risk_score = calculate_risk_score(df)
        risk_label = get_risk_label(risk_score)
        risk_color = get_risk_color(risk_score)

        # HTML strings aligned to left margin to prevent Markdown code block triggering
        risk_card = dedent(f"""<div style="background: linear-gradient(135deg, #f7f9fc, #eef2f7); padding: 25px; border-radius: 14px; border: 1px solid #e1e5ea; margin-bottom: 20px; text-align: center;">
<div style="font-size: 18px; font-weight: 600; color: #555;">Overall Contract Risk</div>
<div style="font-size: 48px; font-weight: 800; margin: 5px; color: {risk_color};">{risk_score}/100</div>
<div style="font-size: 18px; font-weight: 700; color: {risk_color};">{risk_label}</div>
<div style="margin-top: 15px; color: #555; font-size: 14px;">{high_count} High &nbsp;&nbsp;|&nbsp;&nbsp; {medium_count} Medium &nbsp;&nbsp;|&nbsp;&nbsp; {low_count} Low</div>
</div>""")

        st.markdown(risk_card, unsafe_allow_html=True)

        # Risk Cards
        c1, c2, c3 = st.columns(3)

        high_card = dedent(f"""<div style="background: #ff4b4b20; padding: 20px; border-radius: 10px; border-left: 4px solid #ff4b4b;">
<div style="font-size: 16px; font-weight: 600;">High Risk</div>
<div style="font-size: 28px; font-weight: 700; margin-top: 5px;">{high_count}</div>
</div>""")

        medium_card = dedent(f"""<div style="background: #ffa50020; padding: 20px; border-radius: 10px; border-left: 4px solid #ffa500;">
<div style="font-size: 16px; font-weight: 600;">Medium Risk</div>
<div style="font-size: 28px; font-weight: 700; margin-top: 5px;">{medium_count}</div>
</div>""")

        low_card = dedent(f"""<div style="background: #2ecc7120; padding: 20px; border-radius: 10px; border-left: 4px solid #2ecc71;">
<div style="font-size: 16px; font-weight: 600;">Low Risk</div>
<div style="font-size: 28px; font-weight: 700; margin-top: 5px;">{low_count}</div>
</div>""")

        c1.markdown(high_card, unsafe_allow_html=True)
        c2.markdown(medium_card, unsafe_allow_html=True)
        c3.markdown(low_card, unsafe_allow_html=True)

        # Risk Summary
        st.markdown("## Risk Summary")

        if total > 0:
            high_types = high_df["type"].value_counts().index.tolist()
            primary_risk = high_types[0] if high_types else "No high-risk category detected"

            summary_card = dedent(f"""<div style="background: #f7f9fc; padding: 18px; border-radius: 10px; border: 1px solid #e5e7eb; margin-bottom: 20px; line-height: 1.7;">
<b>{total} clauses</b> were analyzed.<br/><br/>
<b>{high_count} high-risk</b> clauses require additional attention.<br/><br/>
Primary high-risk category: <b>{escape_html(primary_risk)}</b>
</div>""")

            st.markdown(summary_card, unsafe_allow_html=True)

        # Search & Filters
        st.markdown("## Search & Filters")
        search_col, risk_col, type_col, confidence_col = st.columns([2, 1, 1, 1])

        with search_col:
            search_query = st.text_input("Search clauses", placeholder="Search liability, payment...")

        with risk_col:
            risk_filter = st.selectbox("Risk", ["All", "HIGH", "MEDIUM", "LOW"])

        with type_col:
            type_options = ["All"] + sorted(df["type"].dropna().unique().tolist())
            type_filter = st.selectbox("Clause Type", type_options)

        with confidence_col:
            confidence_filter = st.selectbox("Confidence", ["All", "90%+", "70–90%", "Below 70%"])

        # Filter Execution
        filtered_df = df.copy()

        if search_query:
            query = search_query.lower()
            clause_match = filtered_df["clause"].astype(str).str.lower().str.contains(query, na=False)
            type_match = filtered_df["type"].astype(str).str.lower().str.contains(query, na=False)
            filtered_df = filtered_df[clause_match | type_match]

        if risk_filter != "All":
            filtered_df = filtered_df[filtered_df["risk"] == risk_filter]

        if type_filter != "All":
            filtered_df = filtered_df[filtered_df["type"] == type_filter]

        if confidence_filter == "90%+":
            filtered_df = filtered_df[filtered_df["confidence"] >= 0.90]
        elif confidence_filter == "70–90%":
            filtered_df = filtered_df[(filtered_df["confidence"] >= 0.70) & (filtered_df["confidence"] < 0.90)]
        elif confidence_filter == "Below 70%":
            filtered_df = filtered_df[filtered_df["confidence"] < 0.70]

        st.caption(f"Showing {len(filtered_df)} of {len(df)} clauses")

        # Analysis of Risk
        st.markdown("## Analysis of Risk")

        def show_group(title, df_group, color, expanded=False):
            if df_group.empty:
                return

            with st.expander(f"{title} ({len(df_group)})", expanded=expanded):
                for _, row in df_group.iterrows():
                    clause = highlight(clean_text(row["clause"]))
                    confidence = float(row["confidence"])
                    confidence_percent = confidence * 100
                    explanation = escape_html(row.get("explanation", "No explanation available."))

                    clause_card = dedent(f"""<div style="border-left: 4px solid {color}; padding: 15px; margin-bottom: 12px; background: #f9f9f9; border-radius: 8px;">
<div style="font-size: 15px; line-height: 1.6;">{clause}</div><br/>
<b>Type:</b> {escape_html(row["type"])}<br/><br/>
<b>Why is this risky?</b>
<div style="margin-top: 6px; color: #555; line-height: 1.5;">{explanation}</div><br/>
<b>Confidence:</b> {confidence_percent:.1f}%
</div>""")

                    st.markdown(clause_card, unsafe_allow_html=True)
                    st.progress(min(max(confidence, 0.0), 1.0))

        filtered_high = filtered_df[filtered_df["risk"] == "HIGH"]
        filtered_medium = filtered_df[filtered_df["risk"] == "MEDIUM"]
        filtered_low = filtered_df[filtered_df["risk"] == "LOW"]

        show_group("HIGH RISK", filtered_high, "#ff4b4b", True)
        show_group("MEDIUM RISK", filtered_medium, "#ffa500")
        show_group("LOW RISK", filtered_low, "#2ecc71")

        # Export Options
        st.markdown("---")
        b1, b2, b3 = st.columns(3)

        csv = df.to_csv(index=False).encode("utf-8")
        b1.download_button("Download CSV", csv, "contract_analysis.csv", "text/csv", use_container_width=True)

        if REPORTLAB_AVAILABLE:
            pdf_file = create_pdf(df, risk_score, risk_label)
            b2.download_button("Download PDF Report", pdf_file, "contract_risk_report.pdf", "application/pdf", use_container_width=True)
        else:
            b2.warning("Install reportlab for PDF export.")

        if b3.button("Visualization", use_container_width=True):
            st.session_state.show_chart = True

# Advanced Risk Analytics
if st.session_state.show_chart and st.session_state.results:
    st.markdown("---")
    st.title("Advanced Risk Analytics")
    df = pd.DataFrame(st.session_state.results)

    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.pie(
            df,
            names="risk",
            title="Overall Risk Distribution",
            color="risk",
            hole=0.5,
            color_discrete_map={"HIGH": "#ff4b4b", "MEDIUM": "#ffa500", "LOW": "#2ecc71"}
        )
        fig1.update_traces(textinfo="percent+label")
        fig1.update_layout(margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig1, use_container_width=True)

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
            color_discrete_map={"HIGH": "#ff4b4b", "MEDIUM": "#ffa500", "LOW": "#2ecc71"}
        )
        fig2.update_layout(
            xaxis_title="Clause Type",
            yaxis_title="Number of Clauses",
            legend_title="Risk Level",
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Key Insights")
    high_count = len(df[df["risk"] == "HIGH"])
    total = len(df)
    top_risky_types = df[df["risk"] == "HIGH"]["type"].value_counts().head(3).index.tolist()
    risky_text = ", ".join(top_risky_types) if top_risky_types else "None"
    average_confidence = df["confidence"].mean() * 100

    insights_card = dedent(f"""<div style="background: #f7f9fc; padding: 20px; border-radius: 10px; border: 1px solid #e5e7eb; line-height: 1.8;">
<b>{high_count} out of {total}</b> clauses are HIGH RISK.<br/>
Most risky clause types: <b>{escape_html(risky_text)}</b><br/>
Average model confidence: <b>{average_confidence:.1f}%</b><br/>
Risk is concentrated in specific clause categories.
</div>""")

    st.markdown(insights_card, unsafe_allow_html=True)
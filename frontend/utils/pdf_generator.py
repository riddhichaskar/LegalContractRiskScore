from io import BytesIO
from utils.helpers import clean_text, escape_html

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

def generate_pdf_report(df, risk_score: int, risk_label: str) -> BytesIO:
    if not REPORTLAB_AVAILABLE or df is None or df.empty:
        return BytesIO()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("TitleCustom", parent=styles["Title"], alignment=TA_CENTER, fontSize=18, spaceAfter=15)
    normal_style = ParagraphStyle("NormalCustom", parent=styles["Normal"], fontSize=9, leading=12)

    story = [
        Paragraph("Contract Risk Intelligence Executive Report", title_style),
        Paragraph(f"<b>Overall Score:</b> {risk_score}/100 | <b>Classification:</b> {risk_label}", normal_style),
        Spacer(1, 12)
    ]

    summary_data = [
        ["Risk Level", "Clause Count"],
        ["HIGH", str(len(df[df["risk"] == "HIGH"]))],
        ["MEDIUM", str(len(df[df["risk"] == "MEDIUM"]))],
        ["LOW", str(len(df[df["risk"] == "LOW"]))],
        ["TOTAL", str(len(df))]
    ]
    table = Table(summary_data, colWidths=[180, 120])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("PADDING", (0, 0), (-1, -1), 6)
    ]))
    story.append(table)
    story.append(Spacer(1, 12))

    for idx, row in df.iterrows():
        text = (
            f"<b>Clause {idx + 1}</b> [{row['risk']} | Confidence: {float(row['confidence']) * 100:.1f}%]<br/>"
            f"<b>Type:</b> {escape_html(row['type'])}<br/>"
            f"<b>Content:</b> {escape_html(clean_text(row['clause']))}<br/>"
            f"<b>Reasoning:</b> {escape_html(row.get('explanation', 'N/A'))}"
        )
        story.append(Paragraph(text, normal_style))
        story.append(Spacer(1, 6))

    doc.build(story)
    buffer.seek(0)
    return buffer
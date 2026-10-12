import re
import html
import pypdf

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

def clean_text(text: str) -> str:
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def escape_html(text: str) -> str:
    return html.escape(str(text))

def highlight_keywords(text: str) -> str:
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
            r"<mark class='keyword-highlight'>\1</mark>",
            text,
            flags=re.IGNORECASE,
        )
    return text

def extract_text_from_file(uploaded_file) -> str:
    filename = uploaded_file.name.lower()
    if filename.endswith(".pdf"):
        reader = pypdf.PdfReader(uploaded_file)
        pages = [p.extract_text() for p in reader.pages if p.extract_text()]
        return "\n\n".join(pages)
    elif filename.endswith(".docx"):
        if not DOCX_AVAILABLE:
            raise ImportError("python-docx package is required for DOCX parsing.")
        doc = docx.Document(uploaded_file)
        return "\n\n".join([p.text for p in doc.paragraphs if p.text])
    else:
        return uploaded_file.read().decode("utf-8", errors="ignore")

def calculate_risk_score(df) -> int:
    if df is None or df.empty:
        return 0
    weights = {"HIGH": 100, "MEDIUM": 60, "LOW": 20}
    return round(df["risk"].map(weights).fillna(0).mean())

def get_risk_label(score: int) -> str:
    if score == 0:
        return "NO DATA"
    elif score >= 70:
        return "HIGH RISK"
    elif score >= 45:
        return "MODERATE RISK"
    return "LOW RISK"
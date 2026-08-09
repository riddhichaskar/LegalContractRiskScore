import re
import spacy
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

nlp = spacy.load("en_core_web_sm")


# -------------------------
# CLAUSE TYPE MAP
# -------------------------
type_map = {
    0: "PAYMENT",
    1: "PENALTY",
    2: "LIABILITY",
    3: "TERMINATION",
    4: "CONFIDENTIALITY",
    5: "INTELLECTUAL_PROPERTY",
    6: "SERVICE",
    7: "USAGE",
    8: "WARRANTY",
    9: "GENERAL"
}


# -------------------------
# TYPE → RISK MAPPING
# -------------------------
TYPE_TO_RISK = {
    "PENALTY": ("HIGH", "Penalty or financial charge"),
    "LIABILITY": ("HIGH", "Liability limitation clause"),
    "WARRANTY": ("HIGH", "Warranty disclaimer"),

    "PAYMENT": ("MEDIUM", "Payment obligation"),
    "TERMINATION": ("MEDIUM", "Termination condition"),
    "SERVICE": ("MEDIUM", "Service condition"),
    "USAGE": ("MEDIUM", "Usage restriction"),

    "CONFIDENTIALITY": ("LOW", "Confidentiality clause"),
    "INTELLECTUAL_PROPERTY": ("LOW", "Intellectual property clause"),
    "GENERAL": ("LOW", "General clause")
}


# -------------------------
# CLEAN TEXT
# -------------------------
def clean_text(text):
    text = re.sub(r'([a-zA-Z])(\d+\.)', r'\1 \2', text)
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# -------------------------
# IMPROVED CLAUSE SPLITTING (CRITICAL FIX)
# -------------------------
def extract_clauses(text):
    parts = re.split(r'\n|\d+\.', text)

    clauses = []

    for part in parts:
        sentences = re.split(r'(?<=[.!?])\s+', part)

        for s in sentences:
            s = s.strip()

            if len(s) > 40:
                clauses.append(s)

    return clauses


# -------------------------
# MODEL + LIGHT RULE REFINEMENT
# -------------------------
class RiskPredictor:
    def __init__(self, model_path="models/clause-type-bert"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)

        self.model.to(self.device)
        self.model.eval()

    # -------------------------
    # MODEL FIRST (PRIMARY)
    # -------------------------
    def predict_type(self, text: str):
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        )

        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)

        logits = outputs.logits
        probs = torch.softmax(logits, dim=1)

        confidence, pred = torch.max(probs, dim=1)

        clause_type = type_map[pred.item()]

        return clause_type, confidence.item()

    # -------------------------
    # RULE REFINEMENT (ONLY FIX OBVIOUS CASES)
    # -------------------------
    def refine(self, text, clause_type):
        text = text.lower()

        # VERY STRONG SIGNALS ONLY
        if "penalty" in text or "late fee" in text:
            return "PENALTY"

        if "limitation of liability" in text or "not liable" in text:
            return "LIABILITY"

        if "confidential" in text or "non-disclosure" in text:
            return "CONFIDENTIALITY"

        return clause_type

    # -------------------------
    # FINAL PREDICTION
    # -------------------------
    def predict(self, text: str):
        clause_type, confidence = self.predict_type(text)

        # 🔥 FIX: apply rules AFTER model (correct architecture)
        clause_type = self.refine(text, clause_type)

        risk, explanation = TYPE_TO_RISK.get(
            clause_type,
            ("LOW", "General clause")
        )

        return {
            "label": risk,
            "confidence": round(confidence, 3),
            "type": clause_type,
            "explanation": explanation
        }


# -------------------------
# CONTRACT ANALYZER
# -------------------------
class ContractAnalyzer:
    def __init__(self):
        self.predictor = RiskPredictor()

    def analyze(self, contract_text: str):
        contract_text = clean_text(contract_text)
        clauses = extract_clauses(contract_text)

        results = []

        for clause in clauses:
            pred = self.predictor.predict(clause)

            results.append({
                "clause": clause,
                "risk": pred["label"],
                "confidence": pred["confidence"],
                "type": pred["type"],
                "explanation": pred["explanation"]
            })

        return results
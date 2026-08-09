import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


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

    "CONFIDENTIALITY": ("LOW", "Confidentiality clause"),
    "INTELLECTUAL_PROPERTY": ("LOW", "Intellectual property clause"),
    "USAGE": ("LOW", "Usage restriction"),
    "GENERAL": ("LOW", "General clause")
}


class RiskPredictor:
    def __init__(self, model_path="models/clause-type-bert"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)

        self.model.to(self.device)
        self.model.eval()

    # -------------------------
    # CLAUSE TYPE PREDICTION (ML)
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
    # FINAL PREDICTION
    # -------------------------
    def predict(self, text: str):
        clause_type, confidence = self.predict_type(text)

        if confidence < 0.5:
            clause_type = "GENERAL"

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
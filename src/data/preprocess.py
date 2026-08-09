import re
import os
import pandas as pd
import spacy

nlp = spacy.load("en_core_web_sm")


# 🔹 CLEANING
def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9₹$%., ]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# 🔹 SENTENCE SEGMENTATION (STRONGER)
def segment_sentences(text: str):
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 25]
    return sentences


# 🔥 FIXED CLAUSE EXTRACTION (NO OVER-SPLITTING)
def extract_clauses(sentence: str):
    # split only on strong legal boundaries
    clauses = re.split(r'\.\s+', sentence)
    clauses = [c.strip() for c in clauses if len(c.strip()) > 25]
    return clauses


# 🔹 PROCESS CONTRACT
def process_contract(file_path: str, contract_id: int):
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    cleaned = clean_text(raw_text)
    sentences = segment_sentences(cleaned)

    data = []

    for sent in sentences:
        clauses = extract_clauses(sent)

        for clause in clauses:
            data.append({
                "contract_id": contract_id,
                "clause": clause
            })

    return data


# 🔹 BUILD DATASET
def build_dataset(contract_folder="data/raw/contracts"):
    all_data = []

    files = sorted(os.listdir(contract_folder))

    for idx, file in enumerate(files, start=1):
        path = os.path.join(contract_folder, file)
        contract_data = process_contract(path, idx)
        all_data.extend(contract_data)

    return pd.DataFrame(all_data)


# 🔥 IMPROVED RISK RULES (CONTEXT-AWARE)

def assign_risk(clause: str):
    clause = clause.lower()

    # HIGH RISK
    if any(x in clause for x in [
        "penalty",
        "terminate without",
        "immediately terminate",
        "not be held liable",
        "not responsible",
        "data loss",
        "suspension",
        "revoked",
        "damages"
    ]):
        return "HIGH"

    # MEDIUM RISK
    if any(x in clause for x in [
        "payment",
        "within",
        "notice",
        "renew",
        "arbitration",
        "salary",
        "deductions"
    ]):
        return "MEDIUM"

    return "LOW"


def merge_labels(df):
    df["risk_level"] = df["clause"].apply(assign_risk)
    return df


# 🔹 SAVE
def save_dataset():
    df = build_dataset()
    df = merge_labels(df)

    df.to_csv("data/processed/final_dataset.csv", index=False)

    print("✅ Final dataset ready")
    print(df.head())


if __name__ == "__main__":
    save_dataset()
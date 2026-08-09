import random
import pandas as pd


HIGH_RISK_TEMPLATES = [
    "A penalty of {amount}% will be charged for late payment.",
    "The company may terminate the agreement without prior notice.",
    "The provider is not responsible for any data loss.",
    "Services may be suspended immediately upon violation.",
    "The license may be revoked at any time without notice.",
    "No liability will be accepted for damages or losses.",
    "A fine of ₹{money} will be imposed for breach of contract.",
]

MEDIUM_RISK_TEMPLATES = [
    "Payment must be made within {days} days.",
    "Either party may terminate with a {days}-day notice.",
    "The agreement will automatically renew every {period}.",
    "Disputes will be resolved through arbitration.",
    "Salary deductions may apply for late attendance.",
    "The contract is valid for {years} years.",
]

LOW_RISK_TEMPLATES = [
    "Both parties agree to maintain confidentiality.",
    "This agreement is effective from the signing date.",
    "The user is granted a non-transferable license.",
    "All terms are subject to mutual agreement.",
    "The service will be provided as described.",
]


def generate_clause(template):
    return template.format(
        amount=random.choice([5, 10, 15, 20]),
        money=random.choice([1000, 5000, 10000, 50000]),
        days=random.choice([7, 15, 30, 45]),
        period=random.choice(["year", "6 months"]),
        years=random.choice([1, 2, 3])
    )


def generate_dataset(num_samples=200):
    data = []

    for _ in range(num_samples):
        # balance classes
        category = random.choice(["HIGH", "MEDIUM", "LOW"])

        if category == "HIGH":
            clause = generate_clause(random.choice(HIGH_RISK_TEMPLATES))
        elif category == "MEDIUM":
            clause = generate_clause(random.choice(MEDIUM_RISK_TEMPLATES))
        else:
            clause = generate_clause(random.choice(LOW_RISK_TEMPLATES))

        data.append({
            "contract_id": random.randint(1, 50),
            "clause": clause.lower(),
            "risk_level": category
        })

    df = pd.DataFrame(data)
    return df


if __name__ == "__main__":
    df = generate_dataset(300)
    df.to_csv("data/processed/generated_dataset.csv", index=False)
    print("✅ Generated dataset saved!")
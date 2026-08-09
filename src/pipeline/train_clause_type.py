import pandas as pd
from sklearn.model_selection import train_test_split
from src.data.clause_dataset import ClauseDataset
from src.models.bert_model import get_model
from src.models.trainer import Trainer

def train():
    print("🚀 Loading and cleaning dataset...")
    df = pd.read_csv("data/processed/clause_type_dataset.csv")

    # Drop NaNs and remove accidental header rows from merges
    df = df.dropna()
    df = df[df["clause"].str.lower() != "clause"]
    
    valid_types = [
        "PAYMENT", "PENALTY", "LIABILITY", "TERMINATION",
        "CONFIDENTIALITY", "INTELLECTUAL_PROPERTY",
        "SERVICE", "USAGE", "WARRANTY", "GENERAL"
    ]
    df = df[df["type"].isin(valid_types)]

    # Final check: Ensure we don't have classes with only 1 example 
    # (train_test_split will fail if a class can't be split)
    counts = df["type"].value_counts()
    if (counts < 2).any():
        print("⚠️ Warning: Removing classes with fewer than 2 examples.")
        df = df[df["type"].isin(counts[counts >= 2].index)]

    print(f"✅ Clean dataset size: {len(df)}")
    print(df["type"].value_counts())

    # Use stratify to ensure train/val sets have the same label distribution
    train_df, val_df = train_test_split(
        df, 
        test_size=0.2, 
        random_state=42, 
        stratify=df["type"]
    )

    train_dataset = ClauseDataset(train_df)
    val_dataset = ClauseDataset(val_df)

    model = get_model(num_labels=len(valid_types))

    trainer = Trainer(
        model=model,
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        epochs=6
    )

    print("🔥 Starting training...")
    trainer.train()

    model.save_pretrained("models/clause-type-bert")
    print("✅ Clause type model saved at models/clause-type-bert")

if __name__ == "__main__":
    train()
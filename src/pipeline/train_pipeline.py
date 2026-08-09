import pandas as pd
from sklearn.model_selection import train_test_split

from src.data.dataset import ContractDataset
from src.models.bert_model import get_model
from src.models.trainer import Trainer


def train():
    # 🔹 Load real dataset
    real_df = pd.read_csv("data/processed/final_dataset.csv")

    # 🔹 Load generated dataset
    gen_df = pd.read_csv("data/processed/generated_dataset.csv")

    # 🔹 Combine datasets
    df = pd.concat([real_df, gen_df], ignore_index=True)

    # 🔹 Shuffle dataset
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # 🔹 (Optional but recommended) Check distribution
    print("Class distribution:\n", df["risk_level"].value_counts())

    # 🔹 Train-test split
    train_df, val_df = train_test_split(df, test_size=0.2, random_state=42)

    # 🔹 Dataset
    train_dataset = ContractDataset(train_df)
    val_dataset = ContractDataset(val_df)

    # 🔹 Model
    model = get_model(num_labels=3)

    # 🔹 Trainer
    trainer = Trainer(
        model=model,
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        epochs=3
    )

    # 🔹 Train
    trainer.train()

    # 🔹 Save model
    model.save_pretrained("models/bert-base-risk")
    print("✅ Model saved at models/bert-base-risk")
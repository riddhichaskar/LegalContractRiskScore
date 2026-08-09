import torch
from torch.utils.data import Dataset
from transformers import AutoTokenizer


type_map = {
    "PAYMENT": 0,
    "PENALTY": 1,
    "LIABILITY": 2,
    "TERMINATION": 3,
    "CONFIDENTIALITY": 4,
    "INTELLECTUAL_PROPERTY": 5,
    "SERVICE": 6,
    "USAGE": 7,
    "WARRANTY": 8,
    "GENERAL": 9
}


class ClauseDataset(Dataset):
    def __init__(self, df):
        self.texts = df["clause"].tolist()
        self.labels = df["type"].map(type_map)
        # 🔥 drop any invalid labels
        valid_idx = self.labels.notna()

        self.texts = df["clause"][valid_idx].tolist()
        self.labels = self.labels[valid_idx].astype(int).tolist()
        self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]

        # 🔥 simple augmentation
        text = text.replace("shall", "must")
        text = text.replace("must", "shall")

        encoding = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=128,
            return_tensors="pt"
        )

        return {
            "input_ids": encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
            "label": torch.tensor(self.labels[idx], dtype=torch.long)
        }   
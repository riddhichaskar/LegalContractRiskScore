import torch
from torch.utils.data import Dataset
from src.data.tokenizer import BERTTokenizer


label_map = {
    "LOW": 0,
    "MEDIUM": 1,
    "HIGH": 2
}


class ContractDataset(Dataset):
    def __init__(self, dataframe):
        self.texts = dataframe["clause"].tolist()
        self.labels = dataframe["risk_level"].map(label_map).tolist()
        self.tokenizer = BERTTokenizer()

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        encoding = self.tokenizer.encode([self.texts[idx]])

        return {
            "input_ids": encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
            "label": torch.tensor(self.labels[idx])
        }
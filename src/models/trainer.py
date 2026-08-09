import torch
from torch.utils.data import DataLoader
from torch.optim import AdamW
from tqdm import tqdm


class Trainer:
    def __init__(self, model, train_dataset, val_dataset=None, lr=2e-5, batch_size=8, epochs=3):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.model = model.to(self.device)
        self.train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        self.val_loader = DataLoader(val_dataset, batch_size=batch_size) if val_dataset else None

        self.optimizer = AdamW(self.model.parameters(), lr=lr)
        self.epochs = epochs

    def train(self):
        self.model.train()

        for epoch in range(self.epochs):
            total_loss = 0

            loop = tqdm(self.train_loader, leave=True)

            for batch in loop:
                self.optimizer.zero_grad()

                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                labels = batch["label"].to(self.device)

                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )

                loss = outputs.loss
                total_loss += loss.item()

                loss.backward()
                self.optimizer.step()

                loop.set_description(f"Epoch {epoch+1}")
                loop.set_postfix(loss=loss.item())

            print(f"Epoch {epoch+1} Loss: {total_loss/len(self.train_loader)}")

            if self.val_loader:
                self.evaluate()

    def evaluate(self):
        self.model.eval()
        correct = 0
        total = 0

        with torch.no_grad():
            for batch in self.val_loader:
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                labels = batch["label"].to(self.device)

                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )

                preds = torch.argmax(outputs.logits, dim=1)

                correct += (preds == labels).sum().item()
                total += labels.size(0)

        accuracy = correct / total
        print(f"Validation Accuracy: {accuracy:.4f}")

        self.model.train()
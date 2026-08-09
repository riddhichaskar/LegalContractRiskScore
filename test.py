from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model = AutoModelForSequenceClassification.from_pretrained("models/bert-base-risk")
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

text = "The company will charge a penalty of 20% for late payment."

inputs = tokenizer(text, return_tensors="pt")
outputs = model(**inputs)

pred = torch.argmax(outputs.logits, dim=1).item()
print(pred)
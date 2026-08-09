from transformers import AutoModelForSequenceClassification


def get_model(num_labels=10):
    return AutoModelForSequenceClassification.from_pretrained(
        "bert-base-uncased",
        num_labels=num_labels
    )
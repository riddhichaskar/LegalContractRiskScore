import os

folders = [
    "data/raw/contracts",
    "data/processed",
    "data/external",
    "notebooks",
    "src/data",
    "src/features",
    "src/models",
    "src/utils",
    "src/pipeline",
    "models/checkpoints",
    "api/routes",
    "api/services",
    "api/schemas",
    "frontend/components",
    "tests",
    "configs",
    "docs"
]

files = [
    "README.md",
    ".env",
    "run.py",
    "data/raw/labels.csv",
    "configs/model_config.yaml",
    "configs/training_config.yaml",
    "configs/paths.yaml",
    "docs/architecture.md"
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)

for file in files:
    with open(file, "w") as f:
        f.write("")

print("Project structure created successfully!")
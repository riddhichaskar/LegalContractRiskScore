from src.pipeline.inference_pipeline import ContractAnalyzer

analyzer = ContractAnalyzer()


def analyze_contract(text: str):
    return analyzer.analyze(text)
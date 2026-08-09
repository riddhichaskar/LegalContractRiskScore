from src.pipeline.inference_pipeline import ContractAnalyzer
from src.utils.highlighter import highlight_results

contract_text = """
No penalty will be charged for delayed payment.
The client must pay within 7 days.
The company is not responsible for any data loss.
This agreement will renew automatically.
"""

analyzer = ContractAnalyzer()
results = analyzer.analyze(contract_text)

print(highlight_results(results))
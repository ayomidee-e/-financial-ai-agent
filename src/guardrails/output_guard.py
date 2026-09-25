from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

# 1. PII Redaction (Social Security Numbers, Credit Cards, etc.)
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def redact_pii(text: str) -> str:
    results = analyzer.analyze(text=text, language="en")
    return anonymizer.anonymize(text=text, analyzer_results=results).text

# 2. Hallucination Check (Verify citations)
def verify_citations(response: str, retrieved_docs: list) -> bool:
    """
    Extract citations from the response (e.g., [Doc 1]) 
    and verify they actually exist in the retrieved_docs.
    """
    import re
    citations = re.findall(r'\[Doc \d+\]', response)
    if not citations:
        return False # Force the agent to cite sources
    return True

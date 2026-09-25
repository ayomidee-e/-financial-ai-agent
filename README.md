# Financial AI Agent

An AI agent that critically analyzes large financial documents (10-Ks, 10-Qs, earnings reports) with source-cited, mathematically-verified answers.

## Features

- **PDF ingestion** — Upload any financial document
- **RAG retrieval** — Semantic search over indexed chunks
- **Deterministic math** — All calculations run through a sandboxed evaluator
- **Source citations** — Every answer references the originating page
- **Agentic reasoning** — Multi-step tool use via LangGraph

## Quickstart

### 1. Install

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### 2. Configure
```bash
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

### 3. Run
```bash
uvicorn main:app --reload --port 8000
```
### 4. Test
Open http://localhost:8000/docs for the interactive Swagger UI.


## Example Query
```bash
Q: "What was Apple's gross margin percentage in 2023?"

A: "Apple's gross margin in FY2023 was 44.13%. This is calculated from gross margin of $169,148M and total net sales of $383,285M [Source: apple_10k_2023.pdf, page 31]."
```

## Testing
Test with real SEC filings from EDGAR:
- Apple (CIK 0000320193)
- Microsoft (CIK 0000789019)
- Tesla (CIK 0001318605)

## Architecture
See [ARCHITECTURE.md](ARCHITECTURE.md) for system design and component breakdown.

## Limitations
- In-memory vector store (data resets on restart)
- Single-document analysis per session
- English-language documents only

This project is licensed under the terms of the [MIT License](LICENSE).
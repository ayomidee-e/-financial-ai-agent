# Architecture

## Overview

The Financial AI Agent is a **Retrieval-Augmented Generation (RAG)** system with **agentic tool use**. It combines semantic search over financial documents with deterministic computation and source-grounded generation.


## Components

### 1. API Layer (`main.py`)
- **FastAPI** exposes two endpoints:
  - `POST /upload` - ingest PDF, chunk, embed, store
  - `POST /ask` - run the agent and return the answer
- Stateless HTTP; state lives in the vector store.

### 2. Ingestion Pipeline
| Stage | Tool | Notes |
|---|---|---|
| PDF parse | `pypdf.PdfReader` | Per-page text extraction |
| Chunking | `RecursiveCharacterTextSplitter` | 1000 chars, 150 overlap |
| Embedding | `text-embedding-3-small` | 1536-dim vectors |
| Storage | `InMemoryVectorStore` | RAM-only |

### 3. Agent Layer (LangGraph)
- **Pattern:** Reason + Act
- **LLM:** GPT-4o, `temperature=0` for determinism
- **Tools:**
  - `search_financial_docs(query)` - vector similarity search (k=4)
  - `calculator(expression)` - sandboxed `numexpr` evaluation
- **Loop:** LLM --> tool call --> observation ---> LLM --> final answer


## Design Decisions

### Why RAG instead of fine-tuning?
- Financial documents change quarterly; fine-tuning would require retraining.
- RAG gives **source citations** - mandatory for financial auditability.
- Cost: fine-tuning a GPT-4-class model is impractical; RAG costs cents per query.

### Why LangGraph instead of a simple chain?
- Financial questions require **multi-step reasoning** (retrieve --> extract --> compute --> verify).
- LangGraph supports **loops and conditional edges** (e.g., retry on low confidence).
- Enables future **Critic agent** integration without rewriting.

### Why `numexpr` for math instead of `eval()`?
- `eval()` allows arbitrary code execution - a security risk.
- `numexpr` safely evaluates arithmetic expressions only.
- **Critical:** LLMs are unreliable at arithmetic; forcing tool use guarantees correctness.

### Why `InMemoryVectorStore` instead of Chroma/Pinecone?
- Zero infrastructure for a prototype/demo.
- No persistence needed for single-session analysis.
- **Tradeoff:** Data resets on restart. Upgrade path: swap to `langchain-chroma` or Pinecone for production.

### Why `temperature=0`?
- Financial analysis requires **reproducibility**. Same question ---> same answer.
- Creativity is a liability here; we want determinism.

## Tradeoffs & Limitations

| Dimension | Current | Production Upgrade |
|---|---|---|
| Persistence | In-memory | Chroma / pgvector / Pinecone |
| Latency | ~3–6s per query | Add caching (Redis) for repeat queries |
| Concurrency | Single-process | Horizontal scaling behind load balancer |
| Accuracy | LLM + RAG | Add Critic agent + hybrid search (BM25 + vector) |
| Tables | Text extraction only | Use `LlamaParse` or `Unstructured` for tables |

## Future Work

- Input guardrails (prompt injection detection)
- Critic agent for self-verification
- Hybrid retrieval (BM25 + embeddings)
- Table-aware PDF parsing
- Multi-document comparative analysis
- PII redaction on outputs

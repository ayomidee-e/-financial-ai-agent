import os
import shutil
import uuid
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from dotenv import load_dotenv
import numexpr as ne
from pypdf import PdfReader
from langchain_core.tools import tool
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.prebuilt import create_react_agent

load_dotenv()

app = FastAPI(title="Financial AI Agent")

# 1. Vector Store (in-memory)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = InMemoryVectorStore(embedding=embeddings)

# 2. Tools
@tool
def calculator(expression: str) -> str:
    """Use this for ALL math. Example: '(1500000 - 200000) / 4'"""
    try:
        return str(ne.evaluate(expression))
    except Exception as e:
        return f"Math error: {e}"

@tool
def search_financial_docs(query: str) -> str:
    """Search the uploaded financial documents for relevant information."""
    docs = vectorstore.similarity_search(query, k=4)
    if not docs:
        return "No documents have been uploaded yet."
    return "\n\n---\n\n".join(
        f"[Source: {d.metadata.get('source', 'unknown')}, page {d.metadata.get('page', '?')}]\n{d.page_content}"
        for d in docs
    )

# 3. Agent
llm = ChatOpenAI(model="gpt-4o", temperature=0)
tools = [calculator, search_financial_docs]

system_prompt = """You are a Senior Financial Analyst AI.
- ALWAYS use search_financial_docs before answering.
- ALWAYS use calculator for any math. Never do mental math.
- Cite sources as [Source: filename, page X].
- If the answer isn't in the documents, say so explicitly. Never guess."""

agent = create_react_agent(llm, tools, prompt=system_prompt)

# 4. PDF Loader
def load_pdf(path: str, filename: str) -> list[Document]:
    reader = PdfReader(path)
    docs = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            docs.append(Document(
                page_content=text,
                metadata={"source": filename, "page": i + 1}
            ))
    return docs

# 5. API Endpoints
class Query(BaseModel):
    question: str

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    os.makedirs("./data", exist_ok=True)
    path = f"./data/{uuid.uuid4().hex}_{file.filename}"

    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    pages = load_pdf(path, file.filename)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(pages)
    vectorstore.add_documents(chunks)

    return {"status": "indexed", "pages": len(pages), "chunks": len(chunks), "file": file.filename}

@app.post("/ask")
async def ask(q: Query):
    result = await agent.ainvoke({"messages": [("user", q.question)]})
    return {"answer": result["messages"][-1].content}

@app.get("/")
def root():
    return {"status": "Financial AI Agent is running"}
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

def get_vectorstore():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma(
        collection_name="financial_docs",
        embedding_function=embeddings,
        persist_directory="./chroma_db"
    )
    return vectorstore

def ingest_documents(docs):
    vectorstore = get_vectorstore()
    vectorstore.add_documents(docs)
    vectorstore.persist()
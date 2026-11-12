#!/usr/bin/env python3
import os
import glob
from mcp.server.fastmcp import FastMCP
import chromadb
from chromadb.utils import embedding_functions

mcp = FastMCP("LocalKnowledgeBase")
REF_DIR = os.path.join(os.path.dirname(__file__), '..', 'references')

chroma_client = chromadb.Client()
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = chroma_client.get_or_create_collection(name="ml_papers", embedding_function=sentence_transformer_ef)

def load_documents():
    documents, metadatas, ids = [], [], []
    for filepath in glob.glob(os.path.join(REF_DIR, "**", "*.md"), recursive=True):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            chunks = content.split("\n\n")
            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) > 50:
                    documents.append(chunk.strip())
                    metadatas.append({"source": os.path.basename(filepath)})
                    ids.append(f"{os.path.basename(filepath)}_{i}")

    if documents:
        collection.add(documents=documents, metadatas=metadatas, ids=ids)
        print(f"✅ Loaded {len(documents)} chunks into vector database.")

@mcp.tool()
def search_local_knowledge(query: str) -> str:
    """Search the local ML references for a specific query."""
    results = collection.query(query_texts=[query], n_results=3)
    if not results['documents'] or not results['documents'][0]:
        return "No matching knowledge found."
    
    output = "Here is the relevant knowledge from the local references:\n\n"
    for i, doc in enumerate(results['documents'][0]):
        source = results['metadatas'][0][i]['source']
        output += f"--- Source: {source} ---\n{doc}\n\n"
    return output

if __name__ == "__main__":
    print("Starting Local MCP Server...")
    load_documents()
    mcp.run()

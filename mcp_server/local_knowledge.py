#!/usr/bin/env python3
"""
mcp_server/local_knowledge.py - FastMCP Server for Local Verified Knowledge Retrieval.

Indexes references/ markdown files using ChromaDB and Sentence-Transformers
to allow semantic retrieval of verified literature chunks during agent turns.
Provides graceful error handling and fallback search if ChromaDB is unavailable.
"""

from __future__ import annotations

import glob
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
REF_DIR = ROOT / "references"

# Track dependency availability
CHROMADB_AVAILABLE = False
try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except ImportError:
    chromadb = None


class KnowledgeBase:
    """Manages indexing and semantic search over local references."""

    def __init__(self, collection_name: str = "ml_papers"):
        self.collection_name = collection_name
        self.chroma_client = None
        self.collection = None
        self.fallback_docs: List[Dict[str, str]] = []

        if CHROMADB_AVAILABLE:
            try:
                self.chroma_client = chromadb.Client()
                sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2"
                )
                self.collection = self.chroma_client.get_or_create_collection(
                    name=collection_name, embedding_function=sentence_transformer_ef
                )
            except Exception as e:
                print(f"Warning: Failed to initialize ChromaDB embeddings: {e}", file=sys.stderr)
                self.collection = None

    def index_directory(self, target_dir: Path) -> int:
        """Parse markdown documents in target_dir into chunks and index them."""
        if not target_dir.exists():
            return 0

        documents = []
        metadatas = []
        ids = []

        for md_file in sorted(target_dir.glob("**/*.md")):
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            chunks = content.split("\n\n")
            for idx, chunk in enumerate(chunks):
                clean_chunk = chunk.strip()
                if len(clean_chunk) > 40:
                    doc_id = f"{md_file.stem}_{idx}"
                    meta = {"source": md_file.name, "path": str(md_file)}
                    documents.append(clean_chunk)
                    metadatas.append(meta)
                    ids.append(doc_id)
                    self.fallback_docs.append({"id": doc_id, "text": clean_chunk, "source": md_file.name})

        if self.collection and documents:
            try:
                self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
            except Exception as e:
                print(f"ChromaDB indexing error: {e}", file=sys.stderr)

        return len(documents)

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, str]]:
        """Search indexed literature for matching knowledge chunks."""
        if self.collection:
            try:
                results = self.collection.query(query_texts=[query], n_results=top_k)
                hits = []
                if results and results.get("documents") and results["documents"][0]:
                    for i, doc in enumerate(results["documents"][0]):
                        source = results["metadatas"][0][i]["source"]
                        hits.append({"source": source, "text": doc})
                    return hits
            except Exception as e:
                print(f"ChromaDB query error: {e}", file=sys.stderr)

        # Fallback keyword ranking if ChromaDB is unavailable
        query_words = set(query.lower().split())
        scored = []
        for d in self.fallback_docs:
            score = sum(1 for w in query_words if w in d["text"].lower())
            if score > 0:
                scored.append((score, d))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [{"source": item["source"], "text": item["text"]} for _, item in scored[:top_k]]


# Singleton knowledge base
kb = KnowledgeBase()


def setup_mcp_server():
    """Setup FastMCP instance if mcp is installed."""
    try:
        from mcp.server.fastmcp import FastMCP
        server = FastMCP("LocalKnowledgeBase")

        @server.tool()
        def search_local_knowledge(query: str) -> str:
            """Search the local ML references for a specific query."""
            hits = kb.search(query, top_k=3)
            if not hits:
                return "No matching knowledge found in local references."
            output = "Here is the relevant knowledge from the local references:\n\n"
            for hit in hits:
                output += f"--- Source: {hit['source']} ---\n{hit['text']}\n\n"
            return output

        return server
    except ImportError:
        return None


if __name__ == "__main__":
    print("Starting Local MCP Knowledge Base...")
    count = kb.index_directory(REF_DIR)
    print(f"Indexed {count} knowledge chunks.")
    mcp_app = setup_mcp_server()
    if mcp_app:
        mcp_app.run()
    else:
        print("MCP SDK not installed. Run: pip install -r requirements-mcp.txt")

"""
ChromaDB ingestion pipeline.

Accepts raw customer feedback documents, chunks them, embeds them via
OpenAI text-embedding-3-small (or ChromaDB's built-in sentence-transformer
when no OpenAI key is set), and persists to a local ChromaDB instance.

Usage:
    from customerintel.ingest import ingest_documents, query_collection
    ingest_documents(["review text 1", "review text 2", ...])
    results = query_collection(["search query"], n_results=10)
"""

import chromadb
from chromadb.utils import embedding_functions

from customerintel.config import OPENAI_API_KEY, CHROMA_PATH, COLLECTION_NAME, EMBEDDING_MODEL

CHUNK_SIZE = 100    # words per chunk (short reviews rarely need chunking)
CHUNK_OVERLAP = 10


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping word-level chunks."""
    if not text or not text.strip():
        return []
    words = text.split()
    if len(words) <= chunk_size:
        return [text]
    chunks, start = [], 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks


def _get_embedding_function():
    """Return OpenAI embedding function if key is available, else built-in."""
    if OPENAI_API_KEY:
        return embedding_functions.OpenAIEmbeddingFunction(
            api_key=OPENAI_API_KEY,
            model_name=EMBEDDING_MODEL,
        )
    # Falls back to ChromaDB's default (sentence-transformers/all-MiniLM-L6-v2)
    return embedding_functions.DefaultEmbeddingFunction()


def _get_collection() -> chromadb.Collection:
    """Return (or create) the ChromaDB collection."""
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=_get_embedding_function(),
    )


def ingest_documents(
    documents: list[str],
    metadatas: list[dict] | None = None,
) -> None:
    """
    Chunk, embed, and upsert documents into ChromaDB.

    Args:
        documents: Raw feedback strings to ingest.
        metadatas: Optional per-document metadata dicts
                   (keys: source, timestamp, product_category, etc.).

    Raises:
        ValueError: If the documents list is empty.
    """
    if not documents:
        raise ValueError("Documents list cannot be empty")

    collection = _get_collection()

    all_chunks: list[str] = []
    all_ids: list[str] = []
    all_meta: list[dict] = []

    for doc_idx, doc in enumerate(documents):
        if not doc or not doc.strip():
            continue
        for chunk_idx, chunk in enumerate(_chunk_text(doc)):
            all_chunks.append(chunk)
            all_ids.append(f"doc{doc_idx}_chunk{chunk_idx}")
            base_meta = (metadatas[doc_idx] if metadatas and doc_idx < len(metadatas) else {}).copy()
            base_meta.setdefault("source", "customer_review")
            base_meta.setdefault("timestamp", "2025-01-01")
            base_meta["doc_index"] = doc_idx
            base_meta["chunk_index"] = chunk_idx
            all_meta.append(base_meta)

    if not all_chunks:
        print("[Ingest] No non-empty documents to ingest.")
        return

    # upsert avoids duplicate-key errors on repeated runs
    collection.upsert(documents=all_chunks, ids=all_ids, metadatas=all_meta)
    print(f"[Ingest] Upserted {len(all_chunks)} chunks into ChromaDB ({CHROMA_PATH})")


def query_collection(queries: list[str], n_results: int = 10) -> dict:
    """
    Query ChromaDB for documents similar to each query string.

    Args:
        queries: List of natural-language queries.
        n_results: Maximum results per query.

    Returns:
        ChromaDB results dict with keys: documents, metadatas, distances, ids.
        Returns an empty dict if the collection has no documents.
    """
    collection = _get_collection()
    count = collection.count()
    if count == 0:
        print("[Ingest] Collection is empty — no results to return.")
        return {}

    n_results = min(n_results, count)
    return collection.query(query_texts=queries, n_results=n_results)

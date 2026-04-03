"""
ChromaDB ingestion pipeline.

Accepts raw customer feedback documents, chunks them, embeds them,
and persists to a local ChromaDB instance.

Usage:
    from customerintel.ingest import ingest_documents
    ingest_documents(["review text 1", "review text 2", ...])
"""

import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "customer_feedback"
CHUNK_SIZE = 500       # tokens (approximated by characters / 4)
CHUNK_OVERLAP = 50


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks by approximate token count."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks


def ingest_documents(
    documents: list[str],
    metadatas: list[dict] | None = None,
) -> None:
    """
    Chunk, embed, and store documents in ChromaDB.

    Args:
        documents: List of raw feedback strings.
        metadatas: Optional list of dicts with keys like
                   {source, timestamp, product_category, customer_segment}.
    """
    # TODO: Replace with real OpenAI embedding function
    # openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    #     api_key=os.environ["OPENAI_API_KEY"],
    #     model_name="text-embedding-3-small",
    # )
    # client = chromadb.PersistentClient(path=CHROMA_PATH)
    # collection = client.get_or_create_collection(
    #     name=COLLECTION_NAME,
    #     embedding_function=openai_ef,
    # )

    print(f"[Ingest] Processing {len(documents)} documents...")
    all_chunks: list[str] = []
    all_ids: list[str] = []
    all_meta: list[dict] = []

    for doc_idx, doc in enumerate(documents):
        chunks = _chunk_text(doc)
        for chunk_idx, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_ids.append(f"doc{doc_idx}_chunk{chunk_idx}")
            meta = (metadatas[doc_idx] if metadatas else {}).copy()
            meta["doc_index"] = doc_idx
            meta["chunk_index"] = chunk_idx
            all_meta.append(meta)

    # TODO: Uncomment when ChromaDB is configured
    # collection.add(documents=all_chunks, ids=all_ids, metadatas=all_meta)
    print(f"[Ingest] {len(all_chunks)} chunks ready for ChromaDB (stub — not yet persisted).")

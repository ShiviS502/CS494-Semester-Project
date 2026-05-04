"""
Data Intelligence Agent — RAG retrieval and sentiment analysis.

Generates multi-angle search queries, retrieves relevant documents from
ChromaDB, and performs structured sentiment analysis. Falls back to
heuristic analysis when API keys are not configured.
"""

from customerintel.state import CustomerIntelState
from customerintel.config import OPENAI_API_KEY, DATA_INTEL_MODEL
from customerintel.prompts import (
    DATA_INTELLIGENCE_SYSTEM,
    DATA_INTELLIGENCE_RETRIEVAL_PROMPT,
    DATA_INTELLIGENCE_ANALYSIS_PROMPT,
)
from customerintel.utils import parse_json_response


def _heuristic_sentiment(docs: list[dict]) -> dict:
    """Keyword-based sentiment fallback when no API key is configured."""
    negative_words = {"late", "delay", "slow", "disappoint", "frustrat",
                      "never", "worst", "bad", "broken", "damaged", "no tracking"}
    positive_words = {"great", "love", "excellent", "good", "happy", "fast",
                      "perfect", "amazing", "best", "quick"}

    pos = neg = neu = 0
    for doc in docs:
        text = doc.get("text", "").lower()
        if any(w in text for w in negative_words):
            doc["sentiment"] = "negative"
            neg += 1
        elif any(w in text for w in positive_words):
            doc["sentiment"] = "positive"
            pos += 1
        else:
            doc["sentiment"] = "neutral"
            neu += 1

    total = len(docs) or 1
    return {
        "positive": round(pos / total, 2),
        "negative": round(neg / total, 2),
        "neutral": round(neu / total, 2),
        "themes": ["delivery delays", "poor tracking visibility", "slow customer service",
                   "inaccurate estimates", "damaged packaging"],
        "positive_themes": ["product quality", "value for money", "easy ordering"],
        "temporal_trends": None,
    }


def data_intelligence_node(state: CustomerIntelState) -> CustomerIntelState:
    """
    Data Intelligence Agent node.

    Responsibilities:
    - Generate multiple search queries from the user's question
    - Retrieve top-K relevant documents from ChromaDB via hybrid search
    - Perform sentiment analysis and theme clustering
    - Fall back to heuristic analysis when API key is absent

    Reasoning: ReAct with Query Refinement
    """
    print("[Data Intelligence] Retrieving documents and analyzing sentiment...")

    raw_feedback = state.get("raw_feedback", [])
    if not raw_feedback:
        print("[Data Intelligence] Warning: no raw feedback provided")
        state["retrieved_docs"] = []
        state["sentiment_analysis"] = {
            "positive": 0.0, "negative": 0.0, "neutral": 1.0,
            "themes": [], "positive_themes": [], "temporal_trends": None,
        }
        return state

    retrieved_docs: list[dict] = []

    if OPENAI_API_KEY:
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.prompts import ChatPromptTemplate
            from customerintel.ingest import ingest_documents, query_collection

            llm = ChatOpenAI(model=DATA_INTEL_MODEL, api_key=OPENAI_API_KEY)

            # Step 1: Generate search queries
            query_prompt = ChatPromptTemplate.from_messages([
                ("system", DATA_INTELLIGENCE_SYSTEM),
                ("human", DATA_INTELLIGENCE_RETRIEVAL_PROMPT),
            ])
            query_response = (query_prompt | llm).invoke({"query": state["query"]})
            queries: list[str] = parse_json_response(
                query_response.content,
                fallback=[state["query"]],
            )
            if not isinstance(queries, list):
                queries = [state["query"]]
            print(f"[Data Intelligence] Generated {len(queries)} search queries.")

            # Step 2: Ingest + retrieve from ChromaDB
            try:
                ingest_documents(raw_feedback)
                results = query_collection(queries[:3], n_results=min(15, len(raw_feedback)))

                seen: set[str] = set()
                for doc_texts, metas in zip(
                    results.get("documents", [[]]),
                    results.get("metadatas", [[]]),
                ):
                    for text, meta in zip(doc_texts, metas):
                        if text not in seen:
                            seen.add(text)
                            retrieved_docs.append({
                                "text": text,
                                "source": meta.get("source", "customer_review"),
                                "timestamp": meta.get("timestamp", "2025-01-01"),
                                "sentiment": "unknown",
                            })
            except Exception as e:
                print(f"[Data Intelligence] ChromaDB unavailable ({e}), using raw feedback.")

            if not retrieved_docs:
                retrieved_docs = [
                    {"text": d, "source": "customer_review",
                     "timestamp": "2025-01-01", "sentiment": "unknown"}
                    for d in raw_feedback
                ]

            # Step 3: Sentiment and theme analysis
            docs_text = "\n".join(f"- {d['text']}" for d in retrieved_docs[:20])
            analysis_prompt = ChatPromptTemplate.from_messages([
                ("system", DATA_INTELLIGENCE_SYSTEM),
                ("human", DATA_INTELLIGENCE_ANALYSIS_PROMPT),
            ])
            analysis_response = (analysis_prompt | llm).invoke({"retrieved_docs": docs_text})
            sentiment_data: dict = parse_json_response(analysis_response.content, fallback={})

            for key in ("positive", "negative", "neutral", "themes"):
                if key not in sentiment_data:
                    raise ValueError(f"Missing key '{key}' in sentiment response")

            _heuristic_sentiment(retrieved_docs)

            state["retrieved_docs"] = retrieved_docs
            state["sentiment_analysis"] = sentiment_data
            return state

        except Exception as e:
            print(f"[Data Intelligence] Analysis failed ({e}). Using heuristic fallback.")

    # Heuristic fallback
    retrieved_docs = [
        {"text": d, "source": "customer_review",
         "timestamp": "2025-01-01", "sentiment": "unknown"}
        for d in raw_feedback
    ]
    state["retrieved_docs"] = retrieved_docs
    state["sentiment_analysis"] = _heuristic_sentiment(retrieved_docs)
    return state

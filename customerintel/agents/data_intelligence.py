from customerintel.state import CustomerIntelState


def data_intelligence_node(state: CustomerIntelState) -> CustomerIntelState:
    """
    Data Intelligence Agent node.

    Responsibilities:
    - Generate multiple search queries from the user's question
    - Retrieve top-K relevant documents from ChromaDB via hybrid search
    - Perform sentiment analysis and theme clustering
    - Support iterative data requests from Diagnosis agent

    Reasoning: ReAct with Query Refinement
    """
    try:
        # TODO: Replace stub with real RAG retrieval + sentiment analysis
        # from langchain_openai import ChatOpenAI
        # import chromadb
        # from transformers import pipeline
        #
        # sentiment_pipe = pipeline(
        #     "sentiment-analysis",
        #     model="distilbert-base-uncased-finetuned-sst-2-english"
        # )
        #
        # client = chromadb.PersistentClient(path="./chroma_db")
        # collection = client.get_or_create_collection("customer_feedback")
        #
        # # Generate multiple queries using LLM
        # llm = ChatOpenAI(model="gpt-3.5-turbo")
        # query_gen_prompt = "Generate 3-5 search queries..."
        # queries = llm.invoke(query_gen_prompt)
        #
        # # Hybrid search: cosine similarity + metadata filtering
        # results = collection.query(query_texts=queries, n_results=20)
        #
        # # Run sentiment analysis
        # sentiments = sentiment_pipe([doc["text"] for doc in results])
        #
        # # Process and structure results
        # retrieved_docs = [
        #     {"text": doc, "source": metadata["source"], 
        #      "timestamp": metadata["timestamp"], "sentiment": sentiment}
        #     for doc, metadata, sentiment in zip(results, metadata_list, sentiments)
        # ]

        print("[Data Intelligence] Retrieving documents and analyzing sentiment...")

        raw_feedback = state.get("raw_feedback", [])
        if not raw_feedback:
            raise ValueError("No raw feedback provided to analyze")

        # Stub: structure retrieved docs properly
        state["retrieved_docs"] = [
            {
                "text": doc,
                "source": "customer_review",
                "timestamp": "2025-01-01",
                "sentiment": "negative" if any(
                    word in doc.lower()
                    for word in ["late", "delay", "slow", "disappointed", "frustrated"]
                ) else "neutral"
            }
            for doc in raw_feedback[:20]
        ]

        # Stub: sentiment distribution
        negative_count = sum(
            1 for doc in state["retrieved_docs"]
            if doc["sentiment"] == "negative"
        )
        total_count = len(state["retrieved_docs"])

        state["sentiment_analysis"] = {
            "positive": 0.3,
            "negative": round(negative_count / total_count, 2) if total_count > 0 else 0.6,
            "neutral": 0.1,
            "themes": [
                "delivery delays",
                "poor tracking visibility",
                "slow customer service",
            ],
        }

        return state

    except Exception as e:
        print(f"[Data Intelligence] Error during retrieval: {e}")
        # Return empty results on error
        state["retrieved_docs"] = []
        state["sentiment_analysis"] = {
            "positive": 0.0,
            "negative": 0.0,
            "neutral": 1.0,
            "themes": [],
        }
        return state
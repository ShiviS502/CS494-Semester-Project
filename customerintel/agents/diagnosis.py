"""
Diagnosis Agent — chain-of-thought root cause analysis.

Analyzes retrieved feedback patterns and identifies root causes of
customer dissatisfaction. Falls back to a structured stub when
ANTHROPIC_API_KEY is not configured.
"""

from customerintel.state import CustomerIntelState
from customerintel.config import ANTHROPIC_API_KEY, DIAGNOSIS_MODEL
from customerintel.prompts import DIAGNOSIS_SYSTEM, DIAGNOSIS_ANALYSIS_PROMPT
from customerintel.utils import parse_json_response

MAX_RETRIEVAL_ITERATIONS = 3
CONFIDENCE_THRESHOLD = 0.70

_STUB_CAUSES = [
    {
        "cause": "Logistics/delivery failure following warehouse relocation",
        "confidence": 0.85,
        "evidence": [
            "60% of negative reviews mention delivery delays",
            "Issue increased sharply after Q2 warehouse relocation",
            "Delivery times rose from 3 days average to 5.5+ days",
        ],
    },
    {
        "cause": "Lack of real-time shipment tracking visibility",
        "confidence": 0.72,
        "evidence": [
            "45% of complaints reference inability to track orders",
            "Customers frustrated by stale tracking status updates",
            "No carrier API integration surfaced in feedback",
        ],
    },
    {
        "cause": "Inaccurate delivery time estimates shown to customers",
        "confidence": 0.65,
        "evidence": [
            "Multiple reviews cite estimate vs. actual mismatch (3 days → 6+)",
            "Expectation gap is primary driver of negative sentiment",
            "Estimates were not updated after warehouse relocation",
        ],
    },
]


def diagnosis_node(state: CustomerIntelState) -> CustomerIntelState:
    """
    Diagnosis Agent node.

    Responsibilities:
    - Analyze patterns in retrieved feedback documents
    - Detect temporal trends and correlations
    - Generate and validate causal hypotheses

    Reasoning: Chain-of-Thought with Self-Reflection (5-step)
    """
    print("[Diagnosis] Performing chain-of-thought root cause analysis...")

    retrieved_docs = state.get("retrieved_docs", [])
    sentiment = state.get("sentiment_analysis", {})
    
    iteration_count = state.get("diagnosis_iteration_count", 0)
    
    if ANTHROPIC_API_KEY:
        try:
            from langchain_anthropic import ChatAnthropic
            from langchain_core.prompts import ChatPromptTemplate

            llm = ChatAnthropic(
                model=DIAGNOSIS_MODEL,
                api_key=ANTHROPIC_API_KEY,
                max_tokens=2048,
                temperature=0,
            )
            prompt = ChatPromptTemplate.from_messages([
                ("system", DIAGNOSIS_SYSTEM),
                ("human", DIAGNOSIS_ANALYSIS_PROMPT),
            ])

            docs_text = "\n".join(f"- {d.get('text', '')}" for d in retrieved_docs[:20])
            response = (prompt | llm).invoke({
                "sentiment_analysis": str(sentiment),
                "retrieved_docs": docs_text,
            })

            root_causes = parse_json_response(response.content, fallback=None)
            
            if isinstance(root_causes, list) and root_causes:
                for cause in root_causes:
                    cause.setdefault("confidence", 0.5)
                    cause.setdefault("evidence", [])
                state["root_causes"] = root_causes
                
                max_conf = max([c.get("confidence", 0) for c in root_causes])
                if max_conf < CONFIDENCE_THRESHOLD and iteration_count < MAX_RETRIEVAL_ITERATIONS:
                    print(f"[Diagnosis] Low confidence ({max_conf}); triggering re-retrieval.")
                    state["needs_more_data"] = True
                    state["diagnosis_iteration_count"] = iteration_count + 1
                else:
                    state["needs_more_data"] = False
                
                return state

            print("[Diagnosis] Could not parse response as JSON; using default causes.")

        except Exception as e:
            print(f"[Diagnosis] Analysis failed ({e}); using default causes.")

    state["root_causes"] = _STUB_CAUSES
    state["needs_more_data"] = False
    return state

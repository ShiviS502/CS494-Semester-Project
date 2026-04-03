from typing import TypedDict, Optional


class CustomerIntelState(TypedDict):
    """Shared state passed between all agents in the LangGraph pipeline."""

    # Input
    query: str
    raw_feedback: list[str]

    # Data Intelligence agent outputs
    retrieved_docs: list[dict]       # [{text, source, timestamp, sentiment}]
    sentiment_analysis: dict         # {positive: float, negative: float, neutral: float, themes: list}

    # Diagnosis agent outputs
    root_causes: list[dict]          # [{cause: str, confidence: float, evidence: list[str]}]

    # Strategy agent outputs
    strategies: list[dict]           # [{option: str, cost_benefit: str, priority: int, timeline: str}]

    # Critic agent outputs
    critique: Optional[str]          # Critique text, or None if approved
    critique_approved: bool          # True when Critic approves or iteration cap reached

    # Loop control
    iteration_count: int             # Number of Strategy→Critic revision cycles completed

    # Orchestrator final output
    final_report: Optional[str]

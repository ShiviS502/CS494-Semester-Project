from langgraph.graph import StateGraph, END

from customerintel.state import CustomerIntelState
from customerintel.agents import (
    orchestrator_node,
    data_intelligence_node,
    diagnosis_node,
    strategy_node,
    critic_node,
)

MAX_ITERATIONS = 3


def should_revise_or_finish(state: CustomerIntelState) -> str:
    """
    Conditional edge after the Critic node.

    Routes back to Strategy if:
      - Critic returned a critique (not approved), AND
      - iteration_count < MAX_ITERATIONS

    Otherwise routes to Orchestrator for final synthesis.
    """
    if not state.get("critique_approved") and state.get("iteration_count", 0) < MAX_ITERATIONS:
        return "strategy"
    return "orchestrator"


def build_graph() -> StateGraph:
    graph = StateGraph(CustomerIntelState)

    # Register nodes
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("data_intelligence", data_intelligence_node)
    graph.add_node("diagnosis", diagnosis_node)
    graph.add_node("strategy", strategy_node)
    graph.add_node("critic", critic_node)

    # Main sequential pipeline
    graph.set_entry_point("data_intelligence")
    graph.add_edge("data_intelligence", "diagnosis")
    graph.add_edge("diagnosis", "strategy")
    graph.add_edge("strategy", "critic")

    # Adversarial revision loop: Critic → Strategy (if not approved) or Orchestrator (if approved)
    graph.add_conditional_edges(
        "critic",
        should_revise_or_finish,
        {
            "strategy": "strategy",
            "orchestrator": "orchestrator",
        },
    )

    graph.add_edge("orchestrator", END)

    return graph.compile()


# Compiled graph instance — import this in main.py
app = build_graph()

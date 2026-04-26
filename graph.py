"""
LangGraph state machine for CustomerIntel multi-agent orchestration.

Defines the computational graph with 5 agent nodes and conditional routing
for the adversarial critique loop.
"""

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

    Decision logic:
    - If Critic approved (critique_approved=True): route to Orchestrator for synthesis
    - If Critic rejected AND iteration_count < MAX_ITERATIONS: route back to Strategy
    - Otherwise: route to Orchestrator (iteration cap enforced by Critic)

    Args:
        state: Current pipeline state from Critic node.

    Returns:
        Node name: "strategy" (revise) or "orchestrator" (finish).
    """
    critique_approved = state.get("critique_approved", False)
    iteration_count = state.get("iteration_count", 0)

    # If approved or max iterations reached, finish
    if critique_approved or iteration_count >= MAX_ITERATIONS:
        return "orchestrator"

    # Otherwise, revise strategy
    return "strategy"


def build_graph() -> StateGraph:
    """
    Build and compile the LangGraph state machine.

    Pipeline:
    1. Data Intelligence: Retrieve and analyze customer feedback
    2. Diagnosis: Identify root causes
    3. Strategy: Generate recommendations
    4. Critic: Evaluate quality (adversarial loop)
    5. Orchestrator: Synthesize final report

    Returns:
        Compiled StateGraph instance ready for invocation.
    """
    graph = StateGraph(CustomerIntelState)

    # Register all agent nodes
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("data_intelligence", data_intelligence_node)
    graph.add_node("diagnosis", diagnosis_node)
    graph.add_node("strategy", strategy_node)
    graph.add_node("critic", critic_node)

    # Main sequential pipeline: Data → Diagnosis → Strategy → Critic
    graph.set_entry_point("data_intelligence")
    graph.add_edge("data_intelligence", "diagnosis")
    graph.add_edge("diagnosis", "strategy")
    graph.add_edge("strategy", "critic")

    # Adversarial revision loop: Critic conditionally routes to Strategy or Orchestrator
    graph.add_conditional_edges(
        "critic",
        should_revise_or_finish,
        {
            "strategy": "strategy",  # Rejected: revise strategy
            "orchestrator": "orchestrator",  # Approved: finalize
        },
    )

    # End after orchestrator synthesis
    graph.add_edge("orchestrator", END)

    return graph.compile()


# Compiled graph instance — import this in main.py
app = build_graph()

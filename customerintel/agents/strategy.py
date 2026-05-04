"""
Strategy Agent — multi-perspective recommendation generation using Claude Haiku.

Handles both initial generation and critique-driven revision cycles.
Falls back to a structured stub when ANTHROPIC_API_KEY is not set.
"""

from customerintel.state import CustomerIntelState
from customerintel.config import ANTHROPIC_API_KEY, STRATEGY_MODEL
from customerintel.prompts import (
    STRATEGY_SYSTEM,
    STRATEGY_GENERATION_PROMPT,
    STRATEGY_REVISION_PROMPT,
)
from customerintel.utils import parse_json_response

_STUB_STRATEGIES = [
    {
        "option": "Partner with faster regional delivery carrier and optimise logistics",
        "cost_benefit": "Cost: $50k/yr. Expected 40% reduction in delivery complaints. ROI: 6 months.",
        "priority": 1,
        "timeline": "6 weeks",
        "risk_mitigation": "Multi-carrier contingency plan; phased rollout with weekly performance reviews.",
        "success_metrics": "Avg delivery time < 4 days; delivery complaint rate down 40%.",
    },
    {
        "option": "Implement real-time package tracking integration with major carriers",
        "cost_benefit": "Cost: $15k one-time + $5k/yr. Addresses 45% of tracking complaints. ROI: 3 months.",
        "priority": 2,
        "timeline": "4 weeks",
        "risk_mitigation": "API rate-limit handling; SMS/email fallback for tracking failures.",
        "success_metrics": "95% real-time tracking coverage; tracking complaints down 45%.",
    },
    {
        "option": "Update and auto-adjust delivery time estimates in product listings",
        "cost_benefit": "Cost: $2k one-time development. Reduces expectation-gap complaints immediately.",
        "priority": 3,
        "timeline": "1 week",
        "risk_mitigation": "A/B test with 10% traffic before full rollout; rollback plan in place.",
        "success_metrics": "Estimate accuracy > 90%; estimate-related complaints down 20%.",
    },
]


def strategy_node(state: CustomerIntelState) -> CustomerIntelState:
    """
    Strategy Agent node.

    Responsibilities:
    - Generate multiple solution alternatives per root cause (initial pass)
    - Revise strategy in response to Critic feedback (subsequent passes)
    - Estimate cost-benefit and build prioritised implementation plan

    Reasoning: Multi-Perspective Reasoning with Reflection
    """
    is_revision = bool(state.get("critique"))
    action = "Revising strategy based on Critic feedback" if is_revision else "Generating initial strategy"
    print(f"[Strategy] {action}...")

    root_causes = state.get("root_causes", [])

    if ANTHROPIC_API_KEY:
        try:
            from langchain_anthropic import ChatAnthropic
            from langchain_core.prompts import ChatPromptTemplate

            llm = ChatAnthropic(
                model=STRATEGY_MODEL,
                api_key=ANTHROPIC_API_KEY,
                max_tokens=2048,
            )

            if is_revision:
                template = STRATEGY_REVISION_PROMPT
                input_vars = {
                    "critique": state["critique"],
                    "strategies": str(state.get("strategies", [])),
                    "root_causes": str(root_causes),
                }
            else:
                template = STRATEGY_GENERATION_PROMPT
                input_vars = {"root_causes": str(root_causes)}

            prompt = ChatPromptTemplate.from_messages([
                ("system", STRATEGY_SYSTEM),
                ("human", template),
            ])
            response = (prompt | llm).invoke(input_vars)

            strategies = parse_json_response(response.content, fallback=None)
            if isinstance(strategies, list) and strategies:
                for i, s in enumerate(strategies, 1):
                    s.setdefault("priority", i)
                    s.setdefault("risk_mitigation", "Not specified")
                    s.setdefault("success_metrics", "Not specified")
                state["strategies"] = strategies
                state["critique"] = None
                return state

            print("[Strategy] Could not parse LLM response as JSON; using stub.")

        except Exception as e:
            print(f"[Strategy] LLM call failed ({e}); using stub.")

    state["strategies"] = _STUB_STRATEGIES
    state["critique"] = None
    return state

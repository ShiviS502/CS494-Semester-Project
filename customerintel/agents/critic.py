"""
Critic Agent — adversarial quality control using Claude Sonnet.

Evaluates strategy proposals against root causes with Socratic questioning.
Enforces a maximum of MAX_ITERATIONS revision cycles.
Falls back to a structured stub when ANTHROPIC_API_KEY is not set.
"""

from customerintel.state import CustomerIntelState
from customerintel.config import ANTHROPIC_API_KEY, CRITIC_MODEL
from customerintel.prompts import CRITIC_SYSTEM, CRITIC_EVALUATION_PROMPT

MAX_ITERATIONS = 3


def critic_node(state: CustomerIntelState) -> CustomerIntelState:
    """
    Critic Agent node.

    Responsibilities:
    - Adversarially evaluate Strategy agent proposals
    - Identify logical gaps, missing cost analysis, or unaddressed root causes
    - Return a structured critique or APPROVED
    - Enforce loop termination: auto-approve at MAX_ITERATIONS

    Reasoning: Adversarial Critique with Socratic Questioning
    """
    current_iteration = state.get("iteration_count", 0) + 1
    state["iteration_count"] = current_iteration

    # Hard cap — always approve at max iterations regardless of API availability
    if current_iteration >= MAX_ITERATIONS:
        print(f"[Critic] Iteration cap ({MAX_ITERATIONS}) reached. Auto-approving strategy.")
        state["critique"] = None
        state["critique_approved"] = True
        return state

    print(f"[Critic] Evaluating strategy (iteration {current_iteration}/{MAX_ITERATIONS})...")

    if ANTHROPIC_API_KEY:
        try:
            from langchain_anthropic import ChatAnthropic
            from langchain_core.prompts import ChatPromptTemplate

            llm = ChatAnthropic(
                model=CRITIC_MODEL,
                api_key=ANTHROPIC_API_KEY,
                max_tokens=1024,
            )
            prompt = ChatPromptTemplate.from_messages([
                ("system", CRITIC_SYSTEM),
                ("human", CRITIC_EVALUATION_PROMPT),
            ])
            response = (prompt | llm).invoke({
                "root_causes": str(state.get("root_causes", [])),
                "strategies": str(state.get("strategies", [])),
                "iteration_count": current_iteration,
            })

            content = response.content.strip()
            if "APPROVED" in content.upper():
                print(f"[Critic] Strategy APPROVED on iteration {current_iteration}.")
                state["critique"] = None
                state["critique_approved"] = True
            else:
                print(f"[Critic] Strategy REJECTED on iteration {current_iteration}.")
                state["critique"] = content
                state["critique_approved"] = False
                if "critic_log" not in state:
                    state["critic_log"] = []
                state["critic_log"].append(content)
            return state

        except Exception as e:
            print(f"[Critic] LLM call failed ({e}); using stub logic.")

    # ── Stub fallback: reject on first pass, approve on second ───────────────
    if current_iteration >= 2:
        print(f"[Critic] Strategy approved (stub) on iteration {current_iteration}.")
        state["critique"] = None
        state["critique_approved"] = True
    else:
        print(f"[Critic] Returning stub critique (iteration {current_iteration}).")
        stub_text = (
            "Missing elements identified: "
            "(1) No contingency plan if primary carrier partnership fails. "
            "(2) Tracking integration cost estimate lacks breakdown by engineering vs. licensing. "
            "(3) Delivery estimate adjustment needs explicit A/B test success threshold and rollback plan."
        )
        state["critique"] = stub_text
        state["critique_approved"] = False
        if "critic_log" not in state:
            state["critic_log"] = []
        state["critic_log"].append(stub_text)

    return state

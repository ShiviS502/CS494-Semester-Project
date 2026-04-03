from customerintel.state import CustomerIntelState

MAX_ITERATIONS = 3


def critic_node(state: CustomerIntelState) -> CustomerIntelState:
    """
    Critic Agent node.

    Responsibilities:
    - Adversarially evaluate the Strategy agent's proposals
    - Identify logical inconsistencies, missing cost analysis, or unaddressed root causes
    - Return a structured critique or APPROVE
    - Enforce loop termination: approve unconditionally at MAX_ITERATIONS

    Reasoning: Adversarial Critique with Socratic Questioning
    """
    # TODO: Replace stub with real LLM call
    # from langchain_anthropic import ChatAnthropic
    # from langchain_core.prompts import ChatPromptTemplate
    # from customerintel.prompts import CRITIC_SYSTEM, CRITIC_EVALUATION_PROMPT
    #
    # llm = ChatAnthropic(model="claude-sonnet-4-6")
    # ...
    # if "APPROVED" in response.content:
    #     return {**state, "critique": None, "critique_approved": True,
    #             "iteration_count": state["iteration_count"] + 1}
    # else:
    #     return {**state, "critique": response.content, "critique_approved": False,
    #             "iteration_count": state["iteration_count"] + 1}

    current_iteration = state.get("iteration_count", 0) + 1
    state["iteration_count"] = current_iteration

    # Enforce termination cap
    if current_iteration >= MAX_ITERATIONS:
        print(f"[Critic] Iteration cap reached ({MAX_ITERATIONS}). Approving best available strategy.")
        state["critique"] = None
        state["critique_approved"] = True
        return state

    # Stub: approve on second pass to demonstrate the loop working once
    if current_iteration >= 2:
        print(f"[Critic] Strategy approved on iteration {current_iteration}.")
        state["critique"] = None
        state["critique_approved"] = True
    else:
        print(f"[Critic] Iteration {current_iteration}: returning critique.")
        state["critique"] = (
            "Missing elements: (1) No risk mitigation plan for carrier partnership failure. "
            "(2) Cost estimates for tracking integration lack implementation detail. "
            "(3) Delivery estimate adjustment needs A/B test plan to measure impact."
        )
        state["critique_approved"] = False

    return state

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
    try:
        current_iteration = state.get("iteration_count", 0) + 1
        state["iteration_count"] = current_iteration

        # Enforce termination cap at MAX_ITERATIONS
        if current_iteration >= MAX_ITERATIONS:
            print(
                f"[Critic] Iteration cap reached ({MAX_ITERATIONS}). "
                f"Approving best available strategy."
            )
            state["critique"] = None
            state["critique_approved"] = True
            return state

        # TODO: Replace stub with real LLM call
        # from langchain_anthropic import ChatAnthropic
        # from langchain_core.prompts import ChatPromptTemplate
        # from customerintel.prompts import CRITIC_SYSTEM, CRITIC_EVALUATION_PROMPT
        #
        # llm = ChatAnthropic(model="claude-sonnet-4-6")
        # prompt = ChatPromptTemplate.from_messages([
        #     ("system", CRITIC_SYSTEM),
        #     ("human", CRITIC_EVALUATION_PROMPT),
        # ])
        # chain = prompt | llm
        # response = chain.invoke({
        #     "root_causes": state.get("root_causes", []),
        #     "strategies": state.get("strategies", []),
        #     "iteration_count": current_iteration,
        # })
        # if "APPROVED" in response.content:
        #     return {**state, "critique": None, "critique_approved": True}
        # else:
        #     return {**state, "critique": response.content, "critique_approved": False}

        # Stub: approve on second pass to demonstrate the loop working
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

    except Exception as e:
        print(f"[Critic] Error during evaluation: {e}")
        # On error, approve to allow pipeline to continue
        state["critique"] = None
        state["critique_approved"] = True
        return state
import json

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

from customerintel.state import CustomerIntelState
from customerintel.prompts import CRITIC_SYSTEM, CRITIC_EVALUATION_PROMPT

MAX_ITERATIONS = 3

# using sonnet here because critic need strong reasoning to catch problems in strategy
# haiku sometime miss subtle issues, sonnet is better for adversarial evaluation
llm = ChatAnthropic(model="claude-sonnet-4-6")


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

        # iteration cap check must happen BEFORE the LLM call
        # otherwise we waste tokens on a call that we will approve anyway
        if current_iteration >= MAX_ITERATIONS:
            print(
                f"[Critic] Iteration cap reached ({MAX_ITERATIONS}). "
                f"Approving best available strategy."
            )
            return {**state, "iteration_count": current_iteration, "critique": None, "critique_approved": True}

        print(f"[Critic] Evaluating strategy — iteration {current_iteration} of {MAX_ITERATIONS}...")

        prompt = ChatPromptTemplate.from_messages([
            ("system", CRITIC_SYSTEM),
            ("human", CRITIC_EVALUATION_PROMPT),
        ])

        chain = prompt | llm
        response = chain.invoke({
            "root_causes": json.dumps(state.get("root_causes", []), indent=2),
            "strategies": json.dumps(state.get("strategies", []), indent=2),
            "iteration_count": current_iteration,
        })

        # check for APPROVED keyword in response — prompt says model should return this word
        if "APPROVED" in response.content:
            print(f"[Critic] Strategy approved on iteration {current_iteration}.")
            return {**state, "iteration_count": current_iteration, "critique": None, "critique_approved": True}
        else:
            print(f"[Critic] Iteration {current_iteration}: critique returned, strategy needs revision.")
            return {**state, "iteration_count": current_iteration, "critique": response.content, "critique_approved": False}

    except Exception as e:
        print(f"[Critic] Error during evaluation: {e}")
        # on error we approve so the pipeline dont get stuck forever
        return {**state, "iteration_count": state.get("iteration_count", 0) + 1, "critique": None, "critique_approved": True}
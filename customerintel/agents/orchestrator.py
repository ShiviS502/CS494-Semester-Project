from customerintel.state import CustomerIntelState
from customerintel.prompts import ORCHESTRATOR_SYNTHESIS_PROMPT


def orchestrator_node(state: CustomerIntelState) -> CustomerIntelState:
    """
    Orchestrator Agent node.

    Responsibilities:
    - On first call: parse query, initialize state, create execution plan
    - On final call (after Critic approval): synthesize final report from all agent outputs

    Reasoning: ReAct pattern
    """
    # TODO: Replace stub with real LLM call using LangChain
    # from langchain_anthropic import ChatAnthropic
    # from langchain_core.prompts import ChatPromptTemplate
    #
    # llm = ChatAnthropic(model="claude-sonnet-4-6")
    # prompt = ChatPromptTemplate.from_messages([
    #     ("system", ORCHESTRATOR_SYSTEM),
    #     ("human", ORCHESTRATOR_SYNTHESIS_PROMPT),
    # ])
    # chain = prompt | llm
    # response = chain.invoke({
    #     "query": state["query"],
    #     "sentiment_analysis": state.get("sentiment_analysis", {}),
    #     "root_causes": state.get("root_causes", []),
    #     "strategies": state.get("strategies", []),
    # })
    # return {**state, "final_report": response.content}

    print("[Orchestrator] Synthesizing final report...")
    state["final_report"] = (
        f"[STUB] Final report for query: '{state['query']}'\n"
        f"Root causes identified: {len(state.get('root_causes', []))}\n"
        f"Strategies proposed: {len(state.get('strategies', []))}\n"
        f"Critic revision cycles: {state.get('iteration_count', 0)}"
    )
    return state

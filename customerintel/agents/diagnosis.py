from customerintel.state import CustomerIntelState


def diagnosis_node(state: CustomerIntelState) -> CustomerIntelState:
    """
    Diagnosis Agent node.

    Responsibilities:
    - Analyze patterns in retrieved feedback
    - Detect temporal trends and correlations
    - Generate causal hypotheses about root causes
    - Validate hypotheses with evidence; request more data if needed

    Reasoning: Chain-of-Thought with Self-Reflection
    Steps: patterns → correlations → hypotheses → self-reflection → validation
    """
    # TODO: Replace stub with real LLM call
    # from langchain_anthropic import ChatAnthropic
    # from langchain_core.prompts import ChatPromptTemplate
    # from customerintel.prompts import DIAGNOSIS_SYSTEM, DIAGNOSIS_ANALYSIS_PROMPT
    #
    # llm = ChatAnthropic(model="claude-sonnet-4-6")
    # prompt = ChatPromptTemplate.from_messages([
    #     ("system", DIAGNOSIS_SYSTEM),
    #     ("human", DIAGNOSIS_ANALYSIS_PROMPT),
    # ])
    # chain = prompt | llm
    # response = chain.invoke({
    #     "sentiment_analysis": state["sentiment_analysis"],
    #     "retrieved_docs": state["retrieved_docs"],
    # })
    # root_causes = parse_json_response(response.content)
    # return {**state, "root_causes": root_causes}

    print("[Diagnosis] Performing chain-of-thought root cause analysis...")
    state["root_causes"] = [
        {
            "cause": "Logistics/delivery failure following warehouse relocation",
            "confidence": 0.85,
            "evidence": ["60% of negative reviews mention delivery delays", "Issue increased 68% after Q2"],
        },
        {
            "cause": "Lack of real-time shipment tracking",
            "confidence": 0.72,
            "evidence": ["45% of complaints reference inability to track orders"],
        },
    ]
    return state

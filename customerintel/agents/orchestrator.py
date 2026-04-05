from customerintel.state import CustomerIntelState
from customerintel.prompts import ORCHESTRATOR_SYNTHESIS_PROMPT


def orchestrator_node(state: CustomerIntelState) -> CustomerIntelState:
    """
    Orchestrator Agent node.

    Responsibilities:
    - On first call: parse query, initialize state, create execution plan
    - On final call (after Critic approval): synthesize final report from all agent outputs

    Reasoning: ReAct pattern — Reason about workflow, Act to coordinate agents
    """
    try:
        # TODO: Replace stub with real LLM call using LangChain
        # from langchain_anthropic import ChatAnthropic
        # from langchain_core.prompts import ChatPromptTemplate
        # from customerintel.prompts import ORCHESTRATOR_SYSTEM, ORCHESTRATOR_SYNTHESIS_PROMPT
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

        print("[Orchestrator] Synthesizing final report from all agent outputs...")

        query = state.get("query", "Unknown query")
        root_causes = state.get("root_causes", [])
        strategies = state.get("strategies", [])
        iteration_count = state.get("iteration_count", 0)
        sentiment = state.get("sentiment_analysis", {})

        # Stub: structured final report
        report_lines = [
            "=" * 70,
            f"CUSTOMERINTEL ANALYSIS REPORT",
            "=" * 70,
            f"\nQUERY: {query}",
            f"\n{'=' * 70}",
            f"FINDINGS",
            f"{'=' * 70}",
            f"\nSentiment Distribution:",
            f"  - Positive: {sentiment.get('positive', 0):.0%}",
            f"  - Negative: {sentiment.get('negative', 0):.0%}",
            f"  - Neutral: {sentiment.get('neutral', 0):.0%}",
            f"\nTop Themes: {', '.join(sentiment.get('themes', []))}",
        ]

        if root_causes:
            report_lines.extend([
                f"\n{'=' * 70}",
                f"ROOT CAUSES IDENTIFIED",
                f"{'=' * 70}",
            ])
            for i, cause in enumerate(root_causes, 1):
                report_lines.extend([
                    f"\n{i}. {cause.get('cause', 'Unknown cause')}",
                    f"   Confidence: {cause.get('confidence', 0):.0%}",
                    f"   Evidence:",
                ])
                for evidence in cause.get('evidence', []):
                    report_lines.append(f"   - {evidence}")

        if strategies:
            report_lines.extend([
                f"\n{'=' * 70}",
                f"RECOMMENDED STRATEGY",
                f"{'=' * 70}",
            ])
            for i, strategy in enumerate(strategies, 1):
                report_lines.extend([
                    f"\n{i}. {strategy.get('option', 'Unknown option')} (Priority {strategy.get('priority', 0)})",
                    f"   Timeline: {strategy.get('timeline', 'TBD')}",
                    f"   Cost-Benefit: {strategy.get('cost_benefit', 'TBD')}",
                    f"   Risk Mitigation: {strategy.get('risk_mitigation', 'None specified')}",
                    f"   Success Metrics: {strategy.get('success_metrics', 'TBD')}",
                ])

        report_lines.extend([
            f"\n{'=' * 70}",
            f"PROCESS METADATA",
            f"{'=' * 70}",
            f"Critic revision cycles: {iteration_count}",
            f"Status: Complete",
            "=" * 70,
        ])

        state["final_report"] = "\n".join(report_lines)

        return state

    except Exception as e:
        print(f"[Orchestrator] Error during synthesis: {e}")
        # Return error report on failure
        state["final_report"] = (
            f"ERROR: Failed to synthesize report.\n"
            f"Query: {state.get('query', 'Unknown')}\n"
            f"Error: {str(e)}"
        )
        return state
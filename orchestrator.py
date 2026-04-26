"""
Orchestrator Agent — final synthesis using Claude Sonnet.

Synthesises outputs from all upstream agents into an executive report.
Falls back to a structured text formatter when ANTHROPIC_API_KEY is not set.
"""

from customerintel.state import CustomerIntelState
from customerintel.config import ANTHROPIC_API_KEY, ORCHESTRATOR_MODEL
from customerintel.prompts import ORCHESTRATOR_SYSTEM, ORCHESTRATOR_SYNTHESIS_PROMPT


def _format_report(state: CustomerIntelState) -> str:
    """Deterministic text formatter used as fallback (no LLM needed)."""
    query = state.get("query", "Unknown query")
    sentiment = state.get("sentiment_analysis", {})
    root_causes = state.get("root_causes", [])
    strategies = state.get("strategies", [])
    iteration_count = state.get("iteration_count", 0)

    lines = [
        "=" * 70,
        "CUSTOMERINTEL ANALYSIS REPORT",
        "=" * 70,
        f"\nQUERY: {query}",
        f"\n{'─' * 70}",
        "1. SENTIMENT OVERVIEW",
        f"{'─' * 70}",
        f"  Positive : {sentiment.get('positive', 0):.0%}",
        f"  Negative : {sentiment.get('negative', 0):.0%}",
        f"  Neutral  : {sentiment.get('neutral', 0):.0%}",
    ]

    themes = sentiment.get("themes", [])
    if themes:
        lines.append(f"  Key negative themes: {', '.join(themes)}")
    pos_themes = sentiment.get("positive_themes", [])
    if pos_themes:
        lines.append(f"  Key positive themes: {', '.join(pos_themes)}")

    if root_causes:
        lines += [f"\n{'─' * 70}", "2. ROOT CAUSES IDENTIFIED", f"{'─' * 70}"]
        for i, cause in enumerate(root_causes, 1):
            lines.append(f"\n  {i}. {cause.get('cause', 'Unknown cause')}")
            lines.append(f"     Confidence: {cause.get('confidence', 0):.0%}")
            evidence = cause.get("evidence", [])
            if evidence:
                lines.append("     Evidence:")
                for ev in evidence:
                    lines.append(f"       • {ev}")

    if strategies:
        lines += [f"\n{'─' * 70}", "3. RECOMMENDED STRATEGY", f"{'─' * 70}"]
        for i, s in enumerate(strategies, 1):
            lines.append(f"\n  {i}. [{s.get('priority', i)}] {s.get('option', 'Unknown')}")
            lines.append(f"     Timeline       : {s.get('timeline', 'TBD')}")
            lines.append(f"     Cost-Benefit   : {s.get('cost_benefit', 'TBD')}")
            lines.append(f"     Risk Mitigation: {s.get('risk_mitigation', 'None specified')}")
            lines.append(f"     Success Metrics: {s.get('success_metrics', 'TBD')}")

    lines += [
        f"\n{'─' * 70}",
        "4. PROCESS METADATA",
        f"{'─' * 70}",
        f"  Critic revision cycles: {iteration_count}",
        f"  Status: Complete",
        "=" * 70,
    ]
    return "\n".join(lines)


def orchestrator_node(state: CustomerIntelState) -> CustomerIntelState:
    """
    Orchestrator Agent node (final synthesis pass).

    Responsibilities:
    - Synthesise sentiment analysis, root causes, and approved strategy
    - Produce an executive-level final report

    Reasoning: ReAct — Reason over all agent outputs, Act to compose report
    """
    print("[Orchestrator] Synthesising final report from all agent outputs...")

    if ANTHROPIC_API_KEY:
        try:
            from langchain_anthropic import ChatAnthropic
            from langchain_core.prompts import ChatPromptTemplate

            llm = ChatAnthropic(
                model=ORCHESTRATOR_MODEL,
                api_key=ANTHROPIC_API_KEY,
                max_tokens=2048,
            )
            prompt = ChatPromptTemplate.from_messages([
                ("system", ORCHESTRATOR_SYSTEM),
                ("human", ORCHESTRATOR_SYNTHESIS_PROMPT),
            ])
            response = (prompt | llm).invoke({
                "query": state.get("query", ""),
                "sentiment_analysis": str(state.get("sentiment_analysis", {})),
                "root_causes": str(state.get("root_causes", [])),
                "strategies": str(state.get("strategies", [])),
            })
            state["final_report"] = response.content
            return state

        except Exception as e:
            print(f"[Orchestrator] LLM call failed ({e}); using text formatter.")

    state["final_report"] = _format_report(state)
    return state

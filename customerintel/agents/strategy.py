import json
import re

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

from customerintel.state import CustomerIntelState
from customerintel.prompts import (
    STRATEGY_SYSTEM,
    STRATEGY_GENERATION_PROMPT,
    STRATEGY_REVISION_PROMPT,
)

# using haiku here because it is fast and cheap, for strategy generation it is enough
llm = ChatAnthropic(model="claude-haiku-4-5")


def _parse_json_response(content: str) -> list[dict]:
    """
    Try to extract JSON list from LLM response.
    Sometimes model put extra text before or after JSON so we have to handle that.
    If parsing fails, we wrap the raw text in a single strategy dict so pipeline dont break.
    """
    # first try direct parse
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # try to find JSON array inside the response text
    match = re.search(r"\[.*\]", content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # fallback — wrap raw content so at least something is returned
    return [
        {
            "option": content.strip(),
            "cost_benefit": "see above",
            "priority": 1,
            "timeline": "TBD",
            "risk_mitigation": "TBD",
            "success_metrics": "TBD",
        }
    ]


def strategy_node(state: CustomerIntelState) -> CustomerIntelState:
    """
    Strategy Agent node.

    Responsibilities:
    - Generate multiple solution alternatives per root cause
    - Estimate cost-benefit for each option
    - Build prioritization matrix (impact vs. effort)
    - Revise strategy in response to Critic feedback

    Reasoning: Multi-Perspective Reasoning with Reflection
    """
    try:
        is_revision = bool(state.get("critique"))
        action = "Revising strategy based on critique" if is_revision else "Generating initial strategy"
        print(f"[Strategy] {action}...")

        root_causes = state.get("root_causes", [])
        if not root_causes:
            print("[Strategy] Warning: No root causes provided, strategy may be generic")

        if is_revision:
            # critic gave feedback, so we need to revise
            prompt = ChatPromptTemplate.from_messages([
                ("system", STRATEGY_SYSTEM),
                ("human", STRATEGY_REVISION_PROMPT),
            ])
            input_vars = {
                "critique": state["critique"],
                "strategies": json.dumps(state.get("strategies", []), indent=2),
                "root_causes": json.dumps(root_causes, indent=2),
            }
        else:
            # first time generating strategy
            prompt = ChatPromptTemplate.from_messages([
                ("system", STRATEGY_SYSTEM),
                ("human", STRATEGY_GENERATION_PROMPT),
            ])
            input_vars = {
                "root_causes": json.dumps(root_causes, indent=2),
            }

        chain = prompt | llm
        response = chain.invoke(input_vars)

        strategies = _parse_json_response(response.content)
        print(f"[Strategy] Generated {len(strategies)} strategy option(s).")

        # clear critique so critic evaluate fresh strategy not old one
        return {**state, "strategies": strategies, "critique": None}

    except Exception as e:
        print(f"[Strategy] Error during strategy generation: {e}")
        # return empty so pipeline can still continue
        return {**state, "strategies": [], "critique": None}
"""
CustomerIntel — Streamlit Frontend

Run with:
    streamlit run app.py
"""

import json
import streamlit as st

from customerintel.graph import app as pipeline, MAX_ITERATIONS
from customerintel.state import CustomerIntelState
from customerintel.config import ANTHROPIC_API_KEY, OPENAI_API_KEY

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CustomerIntel",
    page_icon="🔍",
    layout="wide",
)

SAMPLE_FEEDBACK = [
    "The product arrived 2 weeks late. Very disappointed with shipping.",
    "Delivery took forever. I won't order again.",
    "Great product quality but the shipping was painfully slow.",
    "No tracking info available — had no idea where my package was.",
    "Warehouse must have changed; used to get items in 3 days, now it's 10+.",
    "Customer service couldn't tell me where my order was. Frustrating.",
    "Love the product itself, hate the fulfillment experience.",
    "Second order this month with delayed shipping. Looking for alternatives.",
    "Shipping estimate was 3 days, arrived in 6. Update your estimates please.",
    "The box was damaged and the tracking never updated after 'shipped'.",
]


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Configuration")

    st.subheader("API Key Status")
    anthropic_ok = bool(ANTHROPIC_API_KEY)
    openai_ok = bool(OPENAI_API_KEY)
    st.markdown(
        f"{'✅' if anthropic_ok else '❌'} **Anthropic** "
        f"({'set' if anthropic_ok else 'missing — add to .env'})"
    )
    st.markdown(
        f"{'✅' if openai_ok else '❌'} **OpenAI** "
        f"({'set' if openai_ok else 'missing — add to .env'})"
    )
    if not anthropic_ok or not openai_ok:
        st.info(
            "Copy `.env.example` → `.env` and fill in your keys.\n\n"
            "The pipeline runs in **stub mode** without API keys."
        )

    st.divider()
    st.subheader("Pipeline Settings")
    st.metric("Max Critic Iterations", MAX_ITERATIONS)
    st.caption("Edit `MAX_ITERATIONS` in `customerintel/graph.py` to change.")

    st.divider()
    st.subheader("Agents & Models")
    rows = [
        ("Orchestrator", "Claude Sonnet 4.6", "ReAct"),
        ("Data Intelligence", "GPT-3.5-turbo", "ReAct + Query Refinement"),
        ("Diagnosis", "Claude Sonnet 4.6", "Chain-of-Thought"),
        ("Strategy", "Claude Haiku 4.5", "Multi-Perspective"),
        ("Critic", "Claude Sonnet 4.6", "Socratic Critique"),
    ]
    for agent, model, pattern in rows:
        st.markdown(f"**{agent}**  \n`{model}` · {pattern}")


# ── Main area ─────────────────────────────────────────────────────────────────
st.title("🔍 CustomerIntel")
st.caption("Multi-Agent Customer Feedback Analysis · CS 494 Agentic AI · Spring 2026")

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("Query")
    query = st.text_input(
        "Natural language question about customer feedback",
        value="Why are customer reviews getting worse?",
        label_visibility="collapsed",
    )

    st.subheader("Customer Feedback")
    feedback_text = st.text_area(
        "One review per line",
        value="\n".join(SAMPLE_FEEDBACK),
        height=260,
        label_visibility="collapsed",
    )
    feedback_list = [line.strip() for line in feedback_text.splitlines() if line.strip()]
    st.caption(f"{len(feedback_list)} feedback documents loaded")

    run_btn = st.button("▶ Run Analysis", type="primary", use_container_width=True)

with col_right:
    st.subheader("Pipeline Progress")
    progress_placeholder = st.empty()

# ── Analysis ──────────────────────────────────────────────────────────────────
if run_btn:
    if not query.strip():
        st.error("Please enter a query.")
        st.stop()
    if not feedback_list:
        st.error("Please enter at least one feedback document.")
        st.stop()

    initial_state: CustomerIntelState = {
        "query": query,
        "raw_feedback": feedback_list,
        "retrieved_docs": [],
        "sentiment_analysis": {},
        "root_causes": [],
        "strategies": [],
        "critique": None,
        "critique_approved": False,
        "iteration_count": 0,
        "final_report": None,
    }

    agent_labels = {
        "data_intelligence": "📊 Data Intelligence",
        "diagnosis": "🔬 Diagnosis",
        "strategy": "💡 Strategy",
        "critic": "⚖️ Critic",
        "orchestrator": "🎯 Orchestrator",
    }

    with col_right:
        progress_placeholder.empty()
        status_box = st.status("Running pipeline…", expanded=True)
        completed_nodes: list[str] = []

        final_state: CustomerIntelState = {}

        try:
            for event in pipeline.stream(initial_state):
                for node_name, node_state in event.items():
                    label = agent_labels.get(node_name, node_name)
                    completed_nodes.append(label)
                    status_box.write(f"✅ {label} complete")
                    final_state = node_state

            status_box.update(label="Pipeline complete!", state="complete", expanded=False)

        except Exception as e:
            status_box.update(label=f"Pipeline error: {e}", state="error")
            st.error(str(e))
            st.stop()

    # ── Results ───────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("📈 Results")

    tabs = st.tabs(["Final Report", "Sentiment", "Root Causes", "Strategy", "Critic Log"])

    with tabs[0]:
        report = final_state.get("final_report", "No report generated.")
        st.text(report)

    with tabs[1]:
        sa = final_state.get("sentiment_analysis", {})
        if sa:
            c1, c2, c3 = st.columns(3)
            c1.metric("Positive", f"{sa.get('positive', 0):.0%}")
            c2.metric("Negative", f"{sa.get('negative', 0):.0%}")
            c3.metric("Neutral",  f"{sa.get('neutral', 0):.0%}")
            themes = sa.get("themes", [])
            if themes:
                st.markdown("**Negative Themes**")
                for t in themes:
                    st.markdown(f"- {t}")
            pos_themes = sa.get("positive_themes", [])
            if pos_themes:
                st.markdown("**Positive Themes**")
                for t in pos_themes:
                    st.markdown(f"- {t}")
        else:
            st.info("No sentiment data available.")

    with tabs[2]:
        causes = final_state.get("root_causes", [])
        if causes:
            for i, cause in enumerate(causes, 1):
                with st.expander(f"{i}. {cause.get('cause', 'Unknown')} — confidence {cause.get('confidence', 0):.0%}"):
                    for ev in cause.get("evidence", []):
                        st.markdown(f"• {ev}")
        else:
            st.info("No root causes identified.")

    with tabs[3]:
        strategies = final_state.get("strategies", [])
        if strategies:
            for s in strategies:
                with st.expander(f"[P{s.get('priority', '?')}] {s.get('option', 'Unknown')}"):
                    st.markdown(f"**Timeline:** {s.get('timeline', 'TBD')}")
                    st.markdown(f"**Cost-Benefit:** {s.get('cost_benefit', 'TBD')}")
                    st.markdown(f"**Risk Mitigation:** {s.get('risk_mitigation', 'None specified')}")
                    st.markdown(f"**Success Metrics:** {s.get('success_metrics', 'TBD')}")
        else:
            st.info("No strategies generated.")

    with tabs[4]:
        iterations = final_state.get("iteration_count", 0)
        approved = final_state.get("critique_approved", False)
        st.metric("Critic Iterations", iterations)
        st.metric("Final Status", "APPROVED ✅" if approved else "PENDING ⏳")
        critique = final_state.get("critique")
        if critique:
            st.markdown("**Last Critique:**")
            st.warning(critique)
        else:
            st.success("Strategy was approved — no outstanding critique.")

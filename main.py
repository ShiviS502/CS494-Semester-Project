"""
CustomerIntel — Entry Point

Usage:
    python main.py

Or with a custom query:
    python main.py --query "Why are customers leaving negative reviews?"
"""

import argparse
from customerintel.graph import app
from customerintel.state import CustomerIntelState

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


def run(query: str, feedback: list[str]) -> None:
    initial_state: CustomerIntelState = {
        "query": query,
        "raw_feedback": feedback,
        "retrieved_docs": [],
        "sentiment_analysis": {},
        "root_causes": [],
        "strategies": [],
        "critique": None,
        "critique_approved": False,
        "iteration_count": 0,
        "final_report": None,
    }

    print(f"\n{'='*60}")
    print(f"CustomerIntel — Query: {query}")
    print(f"{'='*60}\n")

    final_state = app.invoke(initial_state)

    print(f"\n{'='*60}")
    print("FINAL REPORT")
    print(f"{'='*60}")
    print(final_state["final_report"])
    print(f"\nCompleted in {final_state['iteration_count']} Critic revision cycle(s).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CustomerIntel — Multi-Agent Feedback Analysis")
    parser.add_argument(
        "--query",
        type=str,
        default="Why are customer reviews getting worse?",
        help="Natural language question about the customer feedback",
    )
    args = parser.parse_args()
    run(args.query, SAMPLE_FEEDBACK)

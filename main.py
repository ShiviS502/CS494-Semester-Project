"""
CustomerIntel — Entry Point and CLI

Usage:
    python main.py
    python main.py --query "Why are customers leaving negative reviews?"
"""

import argparse
import sys
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
    """
    Execute the CustomerIntel pipeline end-to-end.

    Args:
        query: Natural language question about customer feedback.
        feedback: List of raw customer feedback strings.

    Raises:
        ValueError: If query or feedback is invalid.
        Exception: If the pipeline fails critically.
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")

    if not feedback or len(feedback) == 0:
        raise ValueError("Feedback list cannot be empty")

    # Initialize pipeline state
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

    print(f"\n{'='*70}")
    print(f"CUSTOMERINTEL — MULTI-AGENT FEEDBACK ANALYSIS")
    print(f"{'='*70}")
    print(f"Query: {query}")
    print(f"Feedback Documents: {len(feedback)}")
    print(f"{'='*70}\n")

    try:
        # Invoke the compiled graph
        final_state = app.invoke(initial_state)

        # Display final report
        print(f"\n{'='*70}")
        print("FINAL REPORT")
        print(f"{'='*70}\n")
        print(final_state.get("final_report", "No report generated"))
        print(f"\n{'='*70}")
        print(
            f"Analysis Complete | "
            f"Critic Cycles: {final_state.get('iteration_count', 0)} | "
            f"Status: {'APPROVED' if final_state.get('critique_approved') else 'PENDING'}"
        )
        print(f"{'='*70}\n")

    except KeyError as e:
        print(f"ERROR: Missing state key during pipeline execution: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"ERROR: Pipeline execution failed: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Parse command-line arguments and run the pipeline."""
    parser = argparse.ArgumentParser(
        description="CustomerIntel — Multi-Agent Customer Feedback Analysis System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python main.py\n"
            "  python main.py --query 'Why are reviews getting worse?'\n"
        ),
    )

    parser.add_argument(
        "--query",
        type=str,
        default="Why are customer reviews getting worse?",
        help="Natural language question about customer feedback (default: '%(default)s')",
    )

    args = parser.parse_args()

    try:
        run(args.query, SAMPLE_FEEDBACK)
    except ValueError as e:
        print(f"VALIDATION ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

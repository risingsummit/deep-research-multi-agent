from __future__ import annotations

import argparse

from research_graph import run_research


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Deep Research multi-agent LangGraph workflow.")
    parser.add_argument("goal", help="Research goal for the agent team.")
    parser.add_argument("--max-rounds", type=int, default=None, help="Maximum verifier-driven research rounds.")
    args = parser.parse_args()

    result = run_research(args.goal, max_rounds=args.max_rounds)
    print(result.get("report", "No report generated."))
    print("\nAgent trace:")
    for step in result.get("trace", []):
        print(f"- {step}")
    if result.get("errors"):
        print("\nErrors:")
        for error in result["errors"]:
            print(f"- {error}")


if __name__ == "__main__":
    main()

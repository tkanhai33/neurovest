from __future__ import annotations

import argparse
import json

from backend.app.llm_bridge.cognition_core import run_cognition


DEFAULT_PROMPT = (
    "Analyze the current NeuroVest architecture. "
    "Explain what needs improvement, produce one ordered plan, "
    "simulate the structural impact of that plan, and confirm "
    "whether it is safe to proceed to patch generation."
)


def print_report(report: dict) -> None:
    print("\n============================================================")
    print("NEURO ARCHITECTURE COGNITION REPORT")
    print("============================================================")
    print("Graph size:", report.get("graph_size"))
    print("Edge count:", report.get("edge_count"))
    print("Ollama:", report.get("ollama_status"))
    print("Status:", report.get("status"))
    print("Safe to apply:", report.get("safe_to_apply"))

    if report.get("ollama_error"):
        print("Ollama error:", report["ollama_error"])

    print("\nSTRUCTURE SUMMARY:")
    print(
        json.dumps(
            report.get("structure", {}).get("summary", {}),
            indent=2,
        )
    )

    print("\nTOP RISKS:")
    for item in report.get("top_risks", [])[:10]:
        print(
            f"- {item['node']} | "
            f"score={item['risk_score']} | "
            f"fanin={item['fanin']} | "
            f"fanout={item['fanout']} | "
            f"multi_hop={item['multi_hop']}"
        )

    print("\nPROPOSED PLAN:")
    print(
        json.dumps(
            report.get("plan"),
            indent=2,
        )
    )

    print("\nPLAN SIMULATION:")
    print(
        json.dumps(
            report.get("simulation"),
            indent=2,
        )
    )

    print("\nCURRENT REPOSITORY VERIFICATION:")
    print(
        json.dumps(
            report.get("repository_verification"),
            indent=2,
        )
    )


def run_once(prompt: str) -> None:
    report = run_cognition(prompt)
    print_report(report)


def interactive() -> None:
    print("🧠 Neuro Architecture Planner Online")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            prompt = input("Neuro > ").strip()
        except EOFError:
            print()
            break

        if prompt.lower() in {"exit", "quit"}:
            break

        if not prompt:
            continue

        run_once(prompt)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--once",
        metavar="PROMPT",
        help="Run one architecture-planning request.",
    )
    parser.add_argument(
        "--default-test",
        action="store_true",
        help="Run the canonical architecture-planning test.",
    )

    args = parser.parse_args()

    if args.once:
        run_once(args.once)
    elif args.default_test:
        run_once(DEFAULT_PROMPT)
    else:
        interactive()


if __name__ == "__main__":
    main()

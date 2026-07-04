import time
from spine.L5_api.repo_introspector import run_scan
from spine.L5_api.neuro_cli_stateful import (
    build_mapping,
    hotspots,
    build_prompt,
    ask_llm,
    load_repo_state
)


TEST_QUESTIONS = [
    "How do we design a fintech AI trading system using SnapTrade?",
    "What are the biggest architectural risks in this system?",
    "What should be built first?"
]


def run_test():
    print("\n🧪 NEURO CORE TEST RUNNER\n")

    summary, forward, reverse = load_repo_state()

    mapping = build_mapping(forward, reverse)
    hs = hotspots(forward, reverse)

    results = []

    for q in TEST_QUESTIONS:
        print(f"\n▶ QUESTION: {q}")

        prompt = build_prompt(q, mapping, hs)
        output = ask_llm(prompt)

        print("\n--- OUTPUT ---\n")
        print(output[:800])  # prevent overflow

        passed = all([
            "FACT" in output,
            "NEXT" in output or "NEXT STEP" in output,
            len(output) > 50
        ])

        results.append(passed)

        print("\nPASS:", passed)
        time.sleep(1)

    print("\n🧪 FINAL RESULT")
    print(f"PASSED: {sum(results)}/{len(results)}")

    if all(results):
        print("✔ SYSTEM BEHAVIOR STABLE")
    else:
        print("⚠ SYSTEM NEEDS PROMPT OR STRUCTURE FIX")


if __name__ == "__main__":
    run_test()

import subprocess
import json
from spine.L5_api.repo_introspector import run_scan


MODEL = "llama3.1"


# =========================================================
# SAFE SERIALIZATION
# =========================================================
def safe(obj):
    if isinstance(obj, dict):
        return {k: safe(v) for k, v in obj.items()}
    if isinstance(obj, set):
        return list(obj)
    if isinstance(obj, tuple):
        return [safe(x) for x in obj]
    if isinstance(obj, list):
        return [safe(x) for x in obj]
    return obj


# =========================================================
# REPO SNAPSHOT (cached per session)
# =========================================================
def get_repo_state():
    summary, forward, reverse = run_scan()
    return safe(summary), safe(forward), safe(reverse)


# =========================================================
# OLLAMA CALL
# =========================================================
def ask_llm(prompt: str):
    result = subprocess.run(
        ["ollama", "run", MODEL],
        input=prompt.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return result.stdout.decode().strip()


# =========================================================
# CONTEXT BUILDER
# =========================================================
def build_prompt(state, user_msg):
    summary, forward, reverse = state

    return f"""
You are NEURO CLI ARCHITECTURE AGENT.

You operate as a persistent fintech system planner.

========================================================
REPO STATE
========================================================

SUMMARY:
{json.dumps(summary, indent=2)}

========================================================
USER INPUT
========================================================
{user_msg}

========================================================
TASK
========================================================

You must act as a system architect for a fintech AI trading system.

Respond with:

1. Understanding of request
2. Impact on architecture (L0–L7 spine)
3. Required components (if missing)
4. Step-by-step next actions
5. Risks

Be concise and technical.
"""


# =========================================================
# CLI LOOP (THIS IS THE IMPORTANT PART)
# =========================================================
def main():
    print("\n🧠 NEURO CLI SHELL ONLINE")
    print("Type 'exit' to quit\n")

    state = get_repo_state()

    while True:
        user_msg = input("neuro> ")

        if user_msg.lower() in ["exit", "quit"]:
            break

        prompt = build_prompt(state, user_msg)
        response = ask_llm(prompt)

        print("\n" + response + "\n")


if __name__ == "__main__":
    main()

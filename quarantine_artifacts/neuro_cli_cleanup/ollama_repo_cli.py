import subprocess
import json
import sys
from spine.L5_api.repo_introspector import run_scan


MODEL = "llama3.1"


# =========================================================
# SAFE SERIALIZER
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
# OLLAMA CALL
# =========================================================
def ask_llm(prompt: str):
    result = subprocess.run(
        ["ollama", "run", MODEL],
        input=prompt.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.decode().strip()


# =========================================================
# SCAN REPO
# =========================================================
def scan():
    summary, forward, reverse = run_scan()
    return safe(summary), safe(forward), safe(reverse)


# =========================================================
# CONTEXT BUILDER
# =========================================================
def build_context(summary, forward, reverse):
    return f"""
YOU ARE A REPO PLANNING AGENT.

You DO NOT execute changes.
You ONLY output structured plans.

========================================================
REPO STATE
========================================================

SUMMARY:
{json.dumps(summary, indent=2)}

FORWARD GRAPH:
{json.dumps(forward, indent=2)}

REVERSE GRAPH:
{json.dumps(reverse, indent=2)}

========================================================
TASK
========================================================

1. Identify structural issues
2. Propose improvements
3. List EXACT file changes needed

========================================================
OUTPUT FORMAT (STRICT)
========================================================

PLAN:
- Issue:
- Affected Files:
- Proposed Fix:
- Risk Level (LOW/MED/HIGH):
"""


# =========================================================
# WRITE MODE (SAFE FILE WRITER)
# =========================================================
def apply_plan(plan_text: str):
    """
    VERY IMPORTANT:
    Only activates if user explicitly passes --apply flag.
    """

    print("\n⚠️ APPLY MODE IS ENABLED\n")
    print("This is where file writing logic would go.\n")
    print("For safety, this version does NOT auto-write files yet.\n")
    print("You will upgrade this once plans are stable.\n")


# =========================================================
# CLI ENTRY
# =========================================================
def main():
    summary, forward, reverse = scan()

    prompt = build_context(summary, forward, reverse)
    result = ask_llm(prompt)

    print("\n================ RESULT ================\n")
    print(result)

    if "--apply" in sys.argv:
        apply_plan(result)


if __name__ == "__main__":
    main()

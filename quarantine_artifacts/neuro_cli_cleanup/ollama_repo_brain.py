import json
import requests
from collections import defaultdict
from spine.L5_api.repo_introspector import run_scan


MODEL = "llama3.1:latest"
OLLAMA_URL = "http://localhost:11434/api/generate"


# =========================================================
# SAFE SERIALIZATION (ROBUST FOR REAL REPO GRAPHS)
# =========================================================
def safe(obj):
    if isinstance(obj, defaultdict):
        obj = dict(obj)

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
# OLLAMA CALL (STABLE HTTP LAYER)
# =========================================================
def ask_llm(prompt: str):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        return response.json().get("response", "").strip()

    except Exception as e:
        return f"ERROR: Ollama call failed → {str(e)}"


# =========================================================
# REPO SCAN CONTEXT
# =========================================================
def build_repo_context():
    summary, forward, reverse = run_scan()

    return (
        safe(summary),
        safe(forward),
        safe(reverse)
    )


# =========================================================
# DETERMINISTIC L0–L7 CLASSIFIER (NO LLM INVOLVEMENT)
# =========================================================
def classify_file(path: str):
    p = path.lower()

    if "test" in p:
        return "L7"

    if "frontend" in p:
        return "L6"

    if "api" in p or "routes" in p or "bridge" in p:
        return "L5"

    if "auth" in p or "security" in p or "gate" in p:
        return "L1"

    if "runtime" in p or "execution" in p or "scheduler" in p:
        return "L4"

    if (
        "facade" in p or
        "introspect" in p or
        "graph" in p or
        "service" in p or
        "controller" in p
    ):
        return "L3"

    if "broker" in p or "http" in p:
        return "L0"

    return "L2"


# =========================================================
# BUILD CLASSIFICATION MAP
# =========================================================
def build_classification(forward, reverse):
    files = set(list(forward.keys()) + list(reverse.keys()))
    return {f: classify_file(f) for f in sorted(files)}


# =========================================================
# HOTSPOT DETECTION (DEPENDENCY ANALYSIS)
# =========================================================
def detect_hotspots(forward, reverse):
    fan_out = {k: len(v) for k, v in forward.items()}
    fan_in = {k: len(v) for k, v in reverse.items()}

    top_out = sorted(fan_out.items(), key=lambda x: x[1], reverse=True)[:3]
    top_in = sorted(fan_in.items(), key=lambda x: x[1], reverse=True)[:3]

    return {
        "fan_out": top_out,
        "fan_in": top_in
    }


# =========================================================
# PROMPT (FACT vs PLAN SEPARATION - CRITICAL FIX)
# =========================================================
def build_prompt(summary, mapping, hotspots):
    return f"""
You are a STRICT ARCHITECTURE ANALYSIS ENGINE.

You operate in TWO MODES:

========================================================
MODE 1 — FACTS (DO NOT INFER OR MODIFY)
========================================================

These are the ONLY truths from the system:

CLASSIFICATION (DO NOT CHANGE):
{json.dumps(mapping, indent=2)}

HOTSPOTS (MEASURED DATA ONLY):
{json.dumps(hotspots, indent=2)}

========================================================
MODE 2 — ANALYSIS (YOU MAY REASON HERE)
========================================================

You may now interpret the system, BUT:

STRICT RULES:
- DO NOT change classifications
- DO NOT redesign architecture
- DO NOT invent missing modules as facts
- DO NOT rename layers
- ONLY suggest improvements based on hotspots

========================================================
TASK
========================================================

1. FACT SUMMARY:
   - What exists in the system (only from data)

2. HOTSPOT ANALYSIS:
   - Why dependencies are risky or concentrated

3. NEXT STEP:
   - ONE safe architectural improvement only

========================================================
OUTPUT FORMAT:
========================================================

FACT SUMMARY:
...

HOTSPOT ANALYSIS:
...

NEXT STEP:
...
"""


# =========================================================
# MAIN ENGINE
# =========================================================
def run_repo_brain():
    summary, forward, reverse = build_repo_context()

    mapping = build_classification(forward, reverse)
    hotspots = detect_hotspots(forward, reverse)

    prompt = build_prompt(summary, mapping, hotspots)

    return ask_llm(prompt)


# =========================================================
# ENTRYPOINT
# =========================================================
if __name__ == "__main__":
    print(run_repo_brain())

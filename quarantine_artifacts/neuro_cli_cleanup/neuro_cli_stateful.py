import json
import requests
from pathlib import Path
from collections import defaultdict
from spine.L5_api.repo_introspector import run_scan
from spine.L5_api.neuro_execution_engine import apply_patch, run_tests


MODEL = "llama3.1:latest"
OLLAMA_URL = "http://localhost:11434/api/generate"

MAX_PROMPT_SIZE = 6000


# =========================================================
# MEMORY SYSTEM
# =========================================================
MEMORY_FILE = Path("spine/L5_api/.neuro_memory.json")


def load_memory():
    if MEMORY_FILE.exists():
        return json.loads(MEMORY_FILE.read_text())

    return {
        "last_files": [],
        "last_mapping": {},
        "last_hotspots": {}
    }


def save_memory(state):
    MEMORY_FILE.write_text(json.dumps(state, indent=2))


def diff_files(old, new):
    return {
        "added": list(set(new) - set(old)),
        "removed": list(set(old) - set(new))
    }


# =========================================================
# PATCH STORAGE
# =========================================================
PATCH_DIR = Path("spine/L5_api/patches")
PATCH_DIR.mkdir(exist_ok=True)


def write_patch(user_msg, response, mapping, hs, diff):
    import datetime

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = PATCH_DIR / f"patch_{ts}.txt"

    content = f"""
================ NEURO PATCH =================

USER REQUEST:
{user_msg}

LLM RESPONSE:
{response}

================================================
INCREMENTAL DIFF
================================================
ADDED FILES:
{json.dumps(diff["added"], indent=2)}

REMOVED FILES:
{json.dumps(diff["removed"], indent=2)}

================================================
FACT CONTEXT
================================================
CLASSIFICATION:
{json.dumps(dict(list(mapping.items())[:25]), indent=2)}

HOTSPOTS:
{json.dumps(hs, indent=2)}

================================================
"""

    file_path.write_text(content)
    return str(file_path)


# =========================================================
# SAFE SERIALIZER
# =========================================================
def safe(obj):
    if isinstance(obj, defaultdict):
        obj = dict(obj)

    if isinstance(obj, dict):
        return {k: safe(v) for k, v in obj.items()}

    if isinstance(obj, set):
        return list(obj)

    if isinstance(obj, tuple):
        return list(obj)

    if isinstance(obj, list):
        return [safe(x) for x in obj]

    return obj


# =========================================================
# OLLAMA CALL
# =========================================================
def ask_llm(prompt):
    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        return r.json().get("response", "").strip()

    except Exception as e:
        return f"ERROR: {str(e)}"


# =========================================================
# REPO SCAN
# =========================================================
def load_repo_state():
    summary, forward, reverse = run_scan()
    return safe(summary), safe(forward), safe(reverse)


# =========================================================
# CLASSIFIER
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
    if "runtime" in p or "execution" in p:
        return "L4"
    if "facade" in p or "service" in p or "graph" in p or "controller" in p:
        return "L3"
    if "broker" in p or "http" in p:
        return "L0"

    return "L2"


def build_mapping(forward, reverse):
    files = set(list(forward.keys()) + list(reverse.keys()))
    return {f: classify_file(f) for f in sorted(files)}


# =========================================================
# HOTSPOTS
# =========================================================
def hotspots(forward, reverse):
    fan_out_raw = {k: len(v) for k, v in forward.items()}
    fan_in_raw = {k: len(v) for k, v in reverse.items()}

    fan_out = dict(sorted(
        fan_out_raw.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10])

    fan_in = dict(sorted(
        fan_in_raw.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10])

    return {
        "fan_out": fan_out,
        "fan_in": fan_in
    }


# =========================================================
# PROMPT ENGINE
# =========================================================
def build_prompt(user_msg, mapping, hs, diff):
    prompt = f"""
You are NEURO ARCHITECTURE CLI AGENT.

STRICT FACT-ONLY MODE.

ADDED:
{json.dumps(diff["added"], indent=2)}

REMOVED:
{json.dumps(diff["removed"], indent=2)}

CLASSIFICATION:
{json.dumps(mapping, indent=2, default=str)}

HOTSPOTS:
{json.dumps(hs, indent=2, default=str)}

USER REQUEST:
{user_msg}

Return:
FACT SUMMARY + HOTSPOT ANALYSIS + NEXT STEP ONLY
"""

    return prompt[:MAX_PROMPT_SIZE]


# =========================================================
# MAIN CLI LOOP (NOW EXECUTION ENABLED)
# =========================================================
def main():
    print("\n🧠 NEURO INTERACTIVE CLI ONLINE (EXECUTION MODE)\n")
    print("Type 'exit' to quit")
    print("Type 'refresh' to rescan repo")
    print("Type 'run tests' to execute test suite\n")

    memory = load_memory()

    summary, forward, reverse = load_repo_state()

    current_files = list(forward.keys())

    diff = diff_files(memory["last_files"], current_files)

    mapping = build_mapping(forward, reverse)
    hs = hotspots(forward, reverse)

    while True:
        user = input("neuro> ")

        if user.lower() in ["exit", "quit"]:
            break

        # refresh repo state
        if user.lower() == "refresh":
            print("🔄 rescanning repo...\n")
            memory = load_memory()
            summary, forward, reverse = load_repo_state()

            current_files = list(forward.keys())
            diff = diff_files(memory["last_files"], current_files)

            mapping = build_mapping(forward, reverse)
            hs = hotspots(forward, reverse)

            print("✔ updated\n")
            continue

        # manual test execution
        if user.lower() == "run tests":
            print("\n🧪 RUNNING TESTS...\n")
            print(run_tests())
            continue

        prompt = build_prompt(user, mapping, hs, diff)
        response = ask_llm(prompt)

        print("\n" + response + "\n")

        patch_path = write_patch(user, response, mapping, hs, diff)
        print(f"🧠 PATCH GENERATED: {patch_path}\n")

        # =====================================================
        # EXECUTION LAYER (THIS IS THE UPGRADE YOU WANTED)
        # =====================================================
        try:
            plan = json.loads(response)

            if isinstance(plan, dict) and "files" in plan:
                print("\n⚙ APPLYING PATCH...\n")
                results = apply_patch(plan)
                for r in results:
                    print(r)

        except Exception:
            # fallback: no structured patch returned
            pass

        # =====================================================
        # MEMORY UPDATE
        # =====================================================
        memory["last_files"] = current_files
        memory["last_mapping"] = mapping
        memory["last_hotspots"] = hs

        save_memory(memory)


if __name__ == "__main__":
    main()

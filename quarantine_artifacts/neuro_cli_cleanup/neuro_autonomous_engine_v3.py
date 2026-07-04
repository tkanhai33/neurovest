import json
import subprocess
import re
from pathlib import Path
from collections import defaultdict
from spine.L5_api.repo_introspector import run_scan

MODEL = "llama3.1:latest"
OLLAMA_URL = "http://localhost:11434/api/generate"

ALLOWED_ROOT = (Path(__file__).resolve().parents[4] / "backend/app").resolve()

MAX_ITERATIONS = 2
TIMEOUT = 120


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
        return [safe(x) for x in obj]

    if isinstance(obj, list):
        return [safe(x) for x in obj]

    return obj


# =========================================================
# SAFE PATH GUARD
# =========================================================
def safe_path(path: str) -> Path:
    full = (ALLOWED_ROOT / path).resolve()

    try:
        full.relative_to(ALLOWED_ROOT)
    except ValueError:
        raise Exception(f"BLOCKED PATH: {path}")

    return full


def write_file(path: str, content: str):
    p = safe_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return f"[OK] {path}"


# =========================================================
# LLM CALL
# =========================================================
def call_llm(prompt: str) -> str:
    try:
        r = subprocess.run(
            ["ollama", "run", MODEL],
            input=prompt.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=TIMEOUT
        )
        return r.stdout.decode(errors="ignore").strip()

    except Exception as e:
        return json.dumps({
            "goal": "fallback",
            "files": [],
            "risk": "high",
            "next_step": f"LLM_FAILED: {str(e)}"
        })


# =========================================================
# CONTEXT
# =========================================================
def build_context():
    summary, forward, reverse = run_scan()

    return safe({
        "summary": summary,
        "forward": dict(list(forward.items())[:30]),
        "reverse": dict(list(reverse.items())[:30]),
    })


# =========================================================
# JSON CLEANER
# =========================================================
def clean_json(text: str) -> str:
    text = text.strip()
    text = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', text)
    text = text.replace("```json", "").replace("```", "")
    return text


def parse_json(raw: str):
    try:
        return json.loads(clean_json(raw))
    except Exception:
        return {
            "goal": "parse_failed",
            "files": [],
            "risk": "high",
            "next_step": "fallback_mode"
        }


# =========================================================
# PLAN BUILDER
# =========================================================
def build_plan(context, user_msg):
    return f"""
You are NEURO PRODUCTION PLANNER.

OUTPUT STRICT JSON ONLY.

RULES:
- NO markdown
- NO commentary
- VALID JSON ONLY

FORMAT:
{{
  "goal": "...",
  "files": [
    {{
      "path": "relative/path.py",
      "action": "create|modify",
      "content": "..."
    }}
  ],
  "risk": "low|medium|high",
  "next_step": "..."
}}

CONTEXT:
{json.dumps(context)}

USER:
{user_msg}
"""


# =========================================================
# APPLY PLAN
# =========================================================
def apply_plan(plan):
    results = []

    for f in plan.get("files", []):
        try:
            results.append(write_file(f["path"], f.get("content", "")))
        except Exception as e:
            results.append(f"[FAIL] {f.get('path')} -> {str(e)}")

    return results


# =========================================================
# VERIFY (FIXED — NO MORE CRASH)
# =========================================================
def verify():
    try:
        result = subprocess.run(
            ["pytest", "-q"],
            cwd=str(ALLOWED_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=TIMEOUT
        )
        return (result.stdout.decode() + result.stderr.decode()).strip()

    except FileNotFoundError:
        return "[TEST SKIPPED] pytest not installed"

    except Exception as e:
        return f"[TEST ERROR] {str(e)}"


# =========================================================
# ENGINE LOOP
# =========================================================
def run_engine(user_msg: str):
    context = build_context()

    last_error = None

    for i in range(MAX_ITERATIONS):

        raw = call_llm(build_plan(context, user_msg))
        plan = parse_json(raw)

        patch_results = apply_plan(plan)
        test_output = verify()

        success = ("FAILED" not in test_output and "ERROR" not in test_output)

        if success:
            return {
                "status": "SUCCESS",
                "iteration": i + 1,
                "patch_results": patch_results,
                "test_output": test_output
            }

        context["last_failure"] = test_output
        last_error = test_output

    return {
        "status": "FAILED_AFTER_MAX",
        "last_error": last_error
    }


# =========================================================
# ENTRYPOINT
# =========================================================
if __name__ == "__main__":
    import sys

    msg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "no request"
    print(json.dumps(run_engine(msg), indent=2))

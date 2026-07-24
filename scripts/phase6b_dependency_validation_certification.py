#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT_DIR = ROOT / "runtime" / "certifications"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "phase6b_dependency_validation_certification_latest.json"

KEY_FILES = [
    "backend/app/stacks/execution/paper_broker.py",
    "backend/app/stacks/chat_public/chat_runtime.py",
    "backend/app/main.py",
]


def run_cli(*args):
    result = subprocess.run(
        ["./neuro_cli.py", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    try:
        payload = json.loads(result.stdout)
    except Exception:
        payload = {
            "parse_error": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    return {
        "cmd": " ".join(["./neuro_cli.py", *args]),
        "returncode": result.returncode,
        "payload": payload,
        "stderr": result.stderr,
    }


def response(step):
    return step.get("payload", {}).get("response", {})


def data(step):
    return response(step).get("data", {})


def main():
    print("🧠 PHASE 6B DEPENDENCY VALIDATION CERTIFICATION")

    subprocess.run(
        ["python3", "scripts/phase4_repo_memory_indexer_v2.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    steps = {
        "repo_unknowns": run_cli("repo_unknowns"),
        "repo_stack_map": run_cli("repo_stack_map"),
        "graph_reset": run_cli("graph_reset"),
        "simulate_trade": run_cli("simulate_trade", "AAPL"),
        "graph_validate": run_cli("graph_validate"),
    }

    for file_path in KEY_FILES:
        key = file_path.replace("/", "__").replace(".py", "")
        steps[f"repo_file__{key}"] = run_cli("repo_file", file_path)
        steps[f"repo_deps__{key}"] = run_cli("repo_deps", file_path)
        steps[f"repo_functions__{key}"] = run_cli("repo_functions", file_path)

    unknowns = data(steps["repo_unknowns"])
    stack_map = data(steps["repo_stack_map"])
    trade = response(steps["simulate_trade"])
    graph_validate = response(steps["graph_validate"])

    per_file = {}

    for file_path in KEY_FILES:
        key = file_path.replace("/", "__").replace(".py", "")

        file_data = data(steps[f"repo_file__{key}"])
        deps_data = data(steps[f"repo_deps__{key}"])
        functions_data = data(steps[f"repo_functions__{key}"])

        per_file[file_path] = {
            "file_found": file_data.get("found") is True,
            "deps_found": deps_data.get("found") is True,
            "functions_found": functions_data.get("found") is True,
            "import_count": deps_data.get("import_count", 0),
            "imported_by_count": deps_data.get("imported_by_count", 0),
            "function_count": functions_data.get("function_count", 0),
            "stack": deps_data.get("stack"),
            "layer": deps_data.get("layer"),
        }

    checks = {
        "unknown_count_zero": unknowns.get("unknown_count") == 0,
        "loose_root_count_zero": unknowns.get("loose_root_count") == 0,
        "stack_map_has_stacks": stack_map.get("stack_count", 0) >= 20,
        "all_key_files_found": all(x["file_found"] for x in per_file.values()),
        "all_key_deps_found": all(x["deps_found"] for x in per_file.values()),
        "all_key_functions_found": all(x["functions_found"] for x in per_file.values()),
        "paper_broker_has_imports": per_file["backend/app/stacks/execution/paper_broker.py"]["import_count"] >= 1,
        "paper_broker_imported_by": per_file["backend/app/stacks/execution/paper_broker.py"]["imported_by_count"] >= 1,
        "chat_runtime_has_functions": per_file["backend/app/stacks/chat_public/chat_runtime.py"]["function_count"] >= 1,
        "main_has_functions": per_file["backend/app/main.py"]["function_count"] >= 1,
        "simulate_trade_ok": trade.get("status") == "trade_simulated",
        "simulate_trade_guard_ok": trade.get("graph_guard", {}).get("valid") is True,
        "graph_validate_ok": graph_validate.get("valid") is True,
    }

    certified = all(checks.values())

    report = {
        "phase": "6B_DEPENDENCY_VALIDATION_CERTIFICATION",
        "generated_at": datetime.now(UTC).isoformat(),
        "certified": certified,
        "checks": checks,
        "per_file": per_file,
        "steps": steps,
    }

    OUT_JSON.write_text(json.dumps(report, indent=2))

    print(json.dumps({
        "phase": report["phase"],
        "certified": certified,
        "checks": checks,
        "per_file": per_file,
        "output": str(OUT_JSON),
    }, indent=2))

    if not certified:
        sys.exit(1)


if __name__ == "__main__":
    main()

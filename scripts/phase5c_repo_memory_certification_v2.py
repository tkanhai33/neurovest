#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT_DIR = ROOT / "runtime" / "certifications"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "phase5c_repo_memory_certification_v2_latest.json"


def run_cli(*args):
    cmd = ["./neuro_cli.py", *args]
    result = subprocess.run(
        cmd,
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
        "cmd": " ".join(cmd),
        "returncode": result.returncode,
        "payload": payload,
        "stderr": result.stderr,
    }


def response(step):
    return step.get("payload", {}).get("response", {})


def data(step):
    return response(step).get("data", {})


def main():
    print("🧠 PHASE 5C REPO MEMORY CERTIFICATION V2")

    subprocess.run(
        ["python3", "scripts/phase4_repo_memory_indexer_v2.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    steps = {
        "repo_summary": run_cli("repo_summary"),
        "repo_unknowns": run_cli("repo_unknowns"),
        "repo_file": run_cli("repo_file", "backend/app/stacks/chat_public/chat_runtime.py"),
        "repo_symbol": run_cli("repo_symbol", "process_portfolio_output"),
        "repo_imports": run_cli("repo_imports", "backend/app/stacks/execution/paper_broker.py"),
        "repo_head": run_cli("repo_head", "backend/app/stacks/chat_public/chat_runtime.py", "20"),
        "repo_grep": run_cli("repo_grep", "graph_validate"),
        "graph_reset": run_cli("graph_reset"),
        "simulate_trade": run_cli("simulate_trade", "AAPL"),
        "graph_validate": run_cli("graph_validate"),
    }

    summary = data(steps["repo_summary"])
    unknowns = data(steps["repo_unknowns"])
    repo_file = data(steps["repo_file"])
    repo_symbol = data(steps["repo_symbol"])
    repo_imports = data(steps["repo_imports"])
    repo_head = data(steps["repo_head"])
    repo_grep = data(steps["repo_grep"])
    trade = response(steps["simulate_trade"])
    graph_validate = response(steps["graph_validate"])

    checks = {
        "summary_file_count_ok": summary.get("file_count", 0) > 0,
        "unknown_count_zero": unknowns.get("unknown_count") == 0,
        "loose_root_count_zero": unknowns.get("loose_root_count") == 0,
        "repo_file_found": repo_file.get("found") is True,
        "repo_file_stack_ok": repo_file.get("file", {}).get("stack") == "chat_public",
        "repo_symbol_found": repo_symbol.get("found") is True,
        "repo_symbol_hit_ok": repo_symbol.get("hit_count", 0) >= 1,
        "repo_imports_found": repo_imports.get("found") is True,
        "repo_imports_count_ok": repo_imports.get("import_count", 0) >= 1,
        "repo_head_found": repo_head.get("found") is True,
        "repo_head_line_count_ok": repo_head.get("line_count") == 20,
        "repo_grep_has_matches": repo_grep.get("match_count", 0) >= 1,
        "simulate_trade_ok": trade.get("status") == "trade_simulated",
        "simulate_trade_guard_ok": trade.get("graph_guard", {}).get("valid") is True,
        "graph_validate_ok": graph_validate.get("valid") is True,
    }

    certified = all(checks.values())

    report = {
        "phase": "5C_REPO_MEMORY_CERTIFICATION_V2",
        "generated_at": datetime.now(UTC).isoformat(),
        "certified": certified,
        "checks": checks,
        "steps": steps,
    }

    OUT_JSON.write_text(json.dumps(report, indent=2))

    print(json.dumps({
        "phase": report["phase"],
        "certified": certified,
        "checks": checks,
        "output": str(OUT_JSON),
    }, indent=2))

    if not certified:
        sys.exit(1)


if __name__ == "__main__":
    main()

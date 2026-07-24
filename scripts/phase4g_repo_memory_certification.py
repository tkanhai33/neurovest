#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT_DIR = ROOT / "runtime" / "certifications"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "phase4g_repo_memory_certification_latest.json"


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


def main():
    print("🧠 PHASE 4G REPO MEMORY CERTIFICATION")

    subprocess.run(
        ["python3", "scripts/phase4_repo_memory_indexer_v2.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    steps = {
        "repo_summary": run_cli("repo_summary"),
        "repo_find": run_cli("repo_find", "process_portfolio_output"),
        "repo_stack": run_cli("repo_stack", "chat_public"),
        "repo_unknowns": run_cli("repo_unknowns"),
        "graph_reset": run_cli("graph_reset"),
        "simulate_trade": run_cli("simulate_trade", "AAPL"),
        "graph_validate": run_cli("graph_validate"),
    }

    summary = response(steps["repo_summary"]).get("data", {})
    find = response(steps["repo_find"]).get("data", {})
    stack = response(steps["repo_stack"]).get("data", {})
    unknowns = response(steps["repo_unknowns"]).get("data", {})
    graph_validate = response(steps["graph_validate"])
    trade = response(steps["simulate_trade"])

    checks = {
        "summary_file_count_ok": summary.get("file_count", 0) > 0,
        "summary_stack_count_ok": summary.get("stack_count", 0) >= 20,
        "summary_symbol_count_ok": summary.get("symbol_count", 0) > 0,
        "find_process_portfolio_output_ok": find.get("match_count", 0) >= 1,
        "stack_chat_public_ok": stack.get("file_count", 0) >= 1,
        "unknown_count_zero": unknowns.get("unknown_count") == 0,
        "loose_root_count_zero": unknowns.get("loose_root_count") == 0,
        "simulate_trade_ok": trade.get("status") == "trade_simulated",
        "simulate_trade_guard_ok": trade.get("graph_guard", {}).get("valid") is True,
        "graph_validate_ok": graph_validate.get("valid") is True,
    }

    certified = all(checks.values())

    report = {
        "phase": "4G_REPO_MEMORY_CERTIFICATION",
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

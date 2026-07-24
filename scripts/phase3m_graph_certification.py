#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT_DIR = ROOT / "runtime" / "certifications"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "phase3m_graph_certification_latest.json"


def run_cli(*args):
    cmd = ["./neuro_cli.py", *args]
    result = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    payload = None
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
    print("🧠 PHASE 3M GRAPH CERTIFICATION")

    steps = {
        "graph_reset": run_cli("graph_reset"),
        "simulate_trade": run_cli("simulate_trade", "AAPL"),
        "graph_status": run_cli("graph_status"),
        "graph_replay": run_cli("graph_replay"),
        "graph_replay_summary": run_cli("graph_replay_summary"),
        "graph_validate": run_cli("graph_validate"),
    }

    status = response(steps["graph_status"])
    replay = response(steps["graph_replay"])
    summary = response(steps["graph_replay_summary"])
    validate = response(steps["graph_validate"])
    trade = response(steps["simulate_trade"])

    checks = {
        "reset_ok": response(steps["graph_reset"]).get("status") == "graph_cleared",
        "trade_ok": trade.get("status") == "trade_simulated",
        "trade_guard_ok": trade.get("graph_guard", {}).get("valid") is True,
        "status_nodes_ok": status.get("live_nodes") == 12,
        "status_edges_ok": status.get("live_edges") == 12,
        "status_events_ok": status.get("live_events") == 12,
        "replay_complete": replay.get("complete") is True,
        "replay_count_ok": replay.get("event_count") == 12,
        "summary_complete": summary.get("complete") is True,
        "summary_symbol_ok": summary.get("symbol") == "AAPL",
        "validate_ok": validate.get("valid") is True,
        "validate_ordered": validate.get("ordered") is True,
        "validate_missing_none": validate.get("missing_nodes") == [],
    }

    certified = all(checks.values())

    report = {
        "phase": "3M_GRAPH_CERTIFICATION",
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

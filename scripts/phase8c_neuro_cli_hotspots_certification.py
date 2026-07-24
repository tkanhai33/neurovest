#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT_DIR = ROOT / "runtime" / "certifications"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "phase8c_neuro_cli_hotspots_certification_latest.json"


def run(cmd):
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
        "stdout": result.stdout[-2000:],
        "stderr": result.stderr[-2000:],
    }


def response(step):
    return step.get("payload", {}).get("response", {})


def data(step):
    return response(step).get("data", {})


def main():
    print("🧠 PHASE 8C NEURO CLI HOTSPOTS CERTIFICATION")

    subprocess.run(["python3", "scripts/phase4_repo_memory_indexer_v2.py"], cwd=ROOT)
    subprocess.run(["python3", "scripts/phase6c_dependency_graph_export.py"], cwd=ROOT)

    steps = {
        "neuro_exists": {
            "exists": (ROOT / "neuro").exists(),
            "executable": (ROOT / "neuro").exists() and bool((ROOT / "neuro").stat().st_mode & 0o111),
        },
        "neuro_hotspots": run(["./neuro", "repo_hotspots", "5"]),
        "neuro_graph_validate": run(["./neuro", "graph_validate"]),
        "cli_hotspots": run(["./neuro_cli.py", "repo_hotspots", "5"]),
        "cli_graph_validate": run(["./neuro_cli.py", "graph_validate"]),
    }

    neuro_hotspots = data(steps["neuro_hotspots"])
    cli_hotspots = data(steps["cli_hotspots"])
    neuro_graph = response(steps["neuro_graph_validate"])
    cli_graph = response(steps["cli_graph_validate"])

    top_hotspot = {}
    if neuro_hotspots.get("hotspots"):
        top_hotspot = neuro_hotspots["hotspots"][0]

    checks = {
        "neuro_wrapper_exists": steps["neuro_exists"]["exists"] is True,
        "neuro_wrapper_executable": steps["neuro_exists"]["executable"] is True,
        "neuro_hotspots_returncode_ok": steps["neuro_hotspots"]["returncode"] == 0,
        "neuro_hotspots_ok": neuro_hotspots.get("hotspot_count", 0) > 0,
        "neuro_hotspots_limit_ok": neuro_hotspots.get("limit") == 5,
        "top_hotspot_is_paper_broker": top_hotspot.get("file") == "backend/app/stacks/execution/paper_broker.py",
        "top_hotspot_risk_ok": top_hotspot.get("risk") == "HIGH_ORCHESTRATOR_COUPLING",
        "neuro_graph_validate_ok": neuro_graph.get("valid") is True,
        "cli_hotspots_match_neuro": cli_hotspots.get("hotspots", [])[:1] == neuro_hotspots.get("hotspots", [])[:1],
        "cli_graph_validate_ok": cli_graph.get("valid") is True,
    }

    certified = all(checks.values())

    report = {
        "phase": "8C_NEURO_CLI_HOTSPOTS_CERTIFICATION",
        "generated_at": datetime.now(UTC).isoformat(),
        "certified": certified,
        "checks": checks,
        "top_hotspot": top_hotspot,
        "steps": steps,
    }

    OUT_JSON.write_text(json.dumps(report, indent=2))

    print(json.dumps({
        "phase": report["phase"],
        "certified": certified,
        "checks": checks,
        "top_hotspot": top_hotspot,
        "output": str(OUT_JSON),
    }, indent=2))

    if not certified:
        sys.exit(1)


if __name__ == "__main__":
    main()

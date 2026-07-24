#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase27b_strategy_candidate_review_index_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {
        "cmd": " ".join(cmd),
        "returncode": r.returncode,
        "stdout": r.stdout[-5000:],
        "stderr": r.stderr[-5000:],
    }

steps = {
    "phase27a_cert": run(["python3", "scripts/phase27a_strategy_proposal_capture_certification.py"]),
    "build_index": run(["python3", "scripts/phase27b_strategy_candidate_review_index.py"]),
    "compile_index": run(["python3", "-m", "py_compile", "scripts/phase27b_strategy_candidate_review_index.py"]),
    "blocked_live_trade": run([
        "curl", "-s", "-X", "POST", "http://127.0.0.1:8000/api/v1/chat",
        "-H", "Content-Type: application/json",
        "-d", '{"message":"can you place a real trade for me?"}'
    ]),
}

index_path = ROOT / "runtime/strategy_candidates/review_index_latest.json"
txt_path = ROOT / "runtime/strategy_candidates/review_index_latest.txt"

index = json.loads(index_path.read_text()) if index_path.exists() else {}

checks = {
    "phase27a_certified": '"certified": true' in steps["phase27a_cert"]["stdout"],
    "index_build_ok": steps["build_index"]["returncode"] == 0,
    "index_json_exists": index_path.exists(),
    "index_txt_exists": txt_path.exists(),
    "candidate_count_present": "candidate_count" in index,
    "items_list_present": isinstance(index.get("items"), list),
    "live_execution_locked": index.get("live_execution_allowed") is False,
    "broker_execution_locked": index.get("broker_execution_allowed") is False,
    "all_items_simulation_only": all(item.get("simulation_only") is True for item in index.get("items", [])),
    "all_items_require_review": all(item.get("requires_promotion_review") is True for item in index.get("items", [])),
    "compile_index_ok": steps["compile_index"]["returncode"] == 0,
    "live_trade_still_blocked": '"status":"blocked"' in steps["blocked_live_trade"]["stdout"].replace(" ", ""),
}

certified = all(checks.values())

report = {
    "phase": "27B_STRATEGY_CANDIDATE_REVIEW_INDEX_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "steps": steps,
    "outputs": {
        "review_index_json": str(index_path),
        "review_index_txt": str(txt_path),
    },
}

OUT.write_text(json.dumps(report, indent=2))

print(json.dumps({
    "phase": report["phase"],
    "certified": certified,
    "checks": checks,
    "output": str(OUT),
}, indent=2))

if not certified:
    sys.exit(1)

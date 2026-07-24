#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase27d_candidate_sandbox_result_schema_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {"cmd": " ".join(cmd), "returncode": r.returncode, "stdout": r.stdout[-5000:], "stderr": r.stderr[-5000:]}

steps = {
    "phase27c_cert": run(["python3", "scripts/phase27c_candidate_sandbox_dry_run_stub_certification.py"]),
    "build_schema": run(["python3", "scripts/phase27d_candidate_sandbox_result_schema.py"]),
    "compile_schema": run(["python3", "-m", "py_compile", "scripts/phase27d_candidate_sandbox_result_schema.py"]),
}

schema_path = ROOT / "runtime/strategy_candidate_sandbox/candidate_sandbox_result_schema_v1.json"
example_path = ROOT / "runtime/strategy_candidate_sandbox/candidate_sandbox_result_example_latest.json"

schema = json.loads(schema_path.read_text()) if schema_path.exists() else {}
example = json.loads(example_path.read_text()) if example_path.exists() else {}

required = set(schema.get("required_fields", []))

checks = {
    "phase27c_certified": '"certified": true' in steps["phase27c_cert"]["stdout"],
    "build_schema_ok": steps["build_schema"]["returncode"] == 0,
    "compile_schema_ok": steps["compile_schema"]["returncode"] == 0,
    "schema_exists": schema_path.exists(),
    "example_exists": example_path.exists(),
    "schema_id_exists": schema.get("schema_id") == "candidate_sandbox_result_v1",
    "has_win_rate": "win_rate" in required,
    "has_profit_factor": "profit_factor" in required,
    "has_max_drawdown": "max_drawdown" in required,
    "has_average_return": "average_return" in required,
    "has_trade_count": "trade_count" in required,
    "has_confidence_score": "confidence_score" in required,
    "has_promotion_recommendation": "promotion_recommendation" in required,
    "approval_required_locked": schema.get("hard_locks", {}).get("approval_required") is True,
    "live_execution_locked": schema.get("hard_locks", {}).get("live_execution_allowed") is False,
    "broker_execution_locked": schema.get("hard_locks", {}).get("broker_execution_allowed") is False,
    "registry_writes_locked": schema.get("hard_locks", {}).get("writes_to_strategy_registry") is False,
    "example_matches_locks": example.get("live_execution_allowed") is False
        and example.get("broker_execution_allowed") is False
        and example.get("writes_to_strategy_registry") is False
        and example.get("approval_required") is True,
}

certified = all(checks.values())

report = {
    "phase": "27D_CANDIDATE_SANDBOX_RESULT_SCHEMA_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "steps": steps,
    "outputs": {
        "schema": str(schema_path),
        "example": str(example_path),
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

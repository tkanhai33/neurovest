#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase28c_candidate_sandbox_mock_scorecard_certification_latest.json"
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
    "phase28b_cert": run(["python3", "scripts/phase28b_candidate_sandbox_mock_metrics_generator_certification.py"]),
    "build_scorecard": run(["python3", "scripts/phase28c_candidate_sandbox_mock_scorecard.py"]),
    "compile_scorecard": run(["python3", "-m", "py_compile", "scripts/phase28c_candidate_sandbox_mock_scorecard.py"]),
    "blocked_live_trade": run([
        "curl", "-s", "-X", "POST", "http://127.0.0.1:8000/api/v1/chat",
        "-H", "Content-Type: application/json",
        "-d", '{"message":"can you place a real trade for me?"}',
    ]),
}

scorecard_path = ROOT / "runtime/strategy_candidate_sandbox/candidate_sandbox_mock_scorecard_latest.json"
txt_path = ROOT / "runtime/strategy_candidate_sandbox/candidate_sandbox_mock_scorecard_latest.txt"

scorecard = json.loads(scorecard_path.read_text()) if scorecard_path.exists() else {}
cards = scorecard.get("scorecards", [])

checks = {
    "phase28b_certified": '"certified": true' in steps["phase28b_cert"]["stdout"],
    "build_scorecard_ok": steps["build_scorecard"]["returncode"] == 0,
    "compile_scorecard_ok": steps["compile_scorecard"]["returncode"] == 0,
    "scorecard_json_exists": scorecard_path.exists(),
    "scorecard_txt_exists": txt_path.exists(),
    "scorecards_list_present": isinstance(cards, list),
    "index_review_not_ready": scorecard.get("scorecard_status") == "review_not_ready",
    "index_reason_mock_only": scorecard.get("reason") == "mock metrics only",
    "index_promotion_blocked": scorecard.get("promotion_allowed") is False,
    "index_live_execution_locked": scorecard.get("live_execution_allowed") is False,
    "index_broker_execution_locked": scorecard.get("broker_execution_allowed") is False,
    "index_registry_writes_disabled": scorecard.get("writes_to_strategy_registry") is False,
    "all_cards_review_not_ready": all(item.get("scorecard_status") == "review_not_ready" for item in cards),
    "all_cards_score_null": all(item.get("score") is None for item in cards),
    "all_cards_reason_mock_only": all(item.get("reason") == "mock metrics only" for item in cards),
    "all_cards_promotion_blocked": all(item.get("promotion_recommendation") == "blocked" for item in cards),
    "all_cards_approval_required": all(item.get("approval_required") is True for item in cards),
    "all_cards_mock_only": all(item.get("mock_only") is True for item in cards),
    "all_cards_no_market_data": all(item.get("market_data_used") is False for item in cards),
    "all_cards_no_backtest": all(item.get("backtest_executed") is False for item in cards),
    "all_cards_no_simulation": all(item.get("simulation_executed") is False for item in cards),
    "all_cards_no_live_execution": all(item.get("live_execution_allowed") is False for item in cards),
    "all_cards_no_broker_execution": all(item.get("broker_execution_allowed") is False for item in cards),
    "all_cards_no_registry_writes": all(item.get("writes_to_strategy_registry") is False for item in cards),
    "live_trade_still_blocked": '"status":"blocked"' in steps["blocked_live_trade"]["stdout"].replace(" ", ""),
}

certified = all(checks.values())

report = {
    "phase": "28C_CANDIDATE_SANDBOX_MOCK_SCORECARD_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "steps": steps,
    "outputs": {
        "scorecard_json": str(scorecard_path),
        "scorecard_txt": str(txt_path),
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

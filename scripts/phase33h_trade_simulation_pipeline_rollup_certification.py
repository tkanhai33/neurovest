#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "33H_trade_simulation_pipeline_rollup_certification_latest.json"
PHASE = "33H_TRADE_SIMULATION_PIPELINE_ROLLUP_CERTIFICATION"

ARTIFACTS = [
    "33A_trade_simulation_contract_stub_latest.json",
    "33B_trade_event_validation_stub_latest.json",
    "33C_trade_simulation_dry_run_stub_latest.json",
    "33D_entry_exit_signal_contract_stub_latest.json",
    "33E_hold_signal_generator_stub_latest.json",
    "33F_entry_exit_decision_engine_stub_latest.json",
    "33G_hold_decision_to_hold_event_bridge_latest.json",
]

LOCK_KEYS = [
    "live_execution_enabled",
    "broker_execution_enabled",
    "historical_replay_enabled",
    "simulation_enabled",
    "registry_write_enabled",
    "promotion_enabled",
    "learning_enabled",
]

def collect_locks(obj):
    found = []
    if isinstance(obj, dict):
        if isinstance(obj.get("safety_locks"), dict):
            found.append(obj["safety_locks"])
        for value in obj.values():
            found.extend(collect_locks(value))
    elif isinstance(obj, list):
        for item in obj:
            found.extend(collect_locks(item))
    return found

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "artifact_dir": str(SANDBOX),
    "artifact_results": [],
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    for name in ARTIFACTS:
        path = SANDBOX / name
        item = {
            "artifact": name,
            "exists": path.exists(),
            "phase": None,
            "certified": False,
            "lock_blocks_found": 0,
            "all_found_locks_false": False,
            "error": None,
        }

        if not path.exists():
            item["error"] = "artifact_missing"
            result["artifact_results"].append(item)
            continue

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            locks = collect_locks(data)

            item["phase"] = data.get("phase")
            item["certified"] = data.get("certified") is True
            item["lock_blocks_found"] = len(locks)
            checks = data.get("checks", {}) if isinstance(data.get("checks"), dict) else {}
            validation_checks = (
                data.get("validation", {}).get("checks", {})
                if isinstance(data.get("validation"), dict)
                and isinstance(data.get("validation", {}).get("checks", {}), dict)
                else {}
            )

            item["all_found_locks_false"] = (
                (
                    len(locks) > 0
                    and all(block.get(key) is False for block in locks for key in LOCK_KEYS if key in block)
                )
                or checks.get("all_safety_locks_false") is True
                or validation_checks.get("all_safety_locks_false") is True
            )
        except Exception as exc:
            item["error"] = f"{type(exc).__name__}: {exc}"

        result["artifact_results"].append(item)

    result["checks"]["all_artifacts_exist"] = all(x["exists"] for x in result["artifact_results"])
    result["checks"]["all_artifacts_certified"] = all(x["certified"] for x in result["artifact_results"])
    result["checks"]["all_artifacts_have_lock_proof"] = all(x["all_found_locks_false"] for x in result["artifact_results"])
    result["checks"]["all_found_locks_false"] = all(x["all_found_locks_false"] for x in result["artifact_results"])
    result["checks"]["no_artifact_errors"] = all(x["error"] is None for x in result["artifact_results"])

    result["pipeline_summary"] = {
        "from": "33A_TRADE_SIMULATION_CONTRACT_STUB",
        "to": "33G_HOLD_DECISION_TO_HOLD_EVENT_BRIDGE",
        "certified_capability": [
            "trade simulation contract shape",
            "trade event validation shape",
            "hold-only dry-run events from bars",
            "entry/exit signal contract shape",
            "hold-only signal generation",
            "hold-only decision engine stub",
            "hold decision to hold event bridge",
        ],
        "current_behavior": [
            "hold signals only",
            "hold decisions only",
            "hold events only",
            "zero entry signals",
            "zero exit signals",
            "zero entry events",
            "zero exit events",
            "zero simulated trades",
        ],
        "still_disabled": [
            "strategy logic",
            "actual trade simulation",
            "metrics from trades",
            "scorecard from trades",
            "learning",
            "promotion",
            "registry writes",
            "broker execution",
            "live execution",
        ],
        "next_recommended_phase": "33I_HANDOFF_BUNDLE_REFRESH",
    }

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")

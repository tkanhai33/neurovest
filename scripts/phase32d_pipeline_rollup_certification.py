#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "32D_pipeline_rollup_certification_latest.json"
PHASE = "32D_PIPELINE_ROLLUP_CERTIFICATION"

ARTIFACTS = [
    "31A_historical_bars_fetch_validation_latest.json",
    "31B_historical_bars_multi_symbol_validation_latest.json",
    "31C_historical_replay_executor_stub_latest.json",
    "31D_historical_replay_bar_iterator_latest.json",
    "31E_first_single_candidate_replay_dry_run_latest.json",
    "31F_replay_metrics_contract_latest.json",
    "32A_real_metrics_generation_latest.json",
    "32B_candidate_scorecard_from_replay_metrics_latest.json",
    "32C_manual_promotion_gate_stub_latest.json",
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

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "artifact_dir": str(SANDBOX),
    "artifact_results": [],
    "checks": {},
    "errors": [],
    "certified": False,
}

def collect_locks(obj):
    found = []

    if isinstance(obj, dict):
        if "safety_locks" in obj and isinstance(obj["safety_locks"], dict):
            found.append(obj["safety_locks"])
        for value in obj.values():
            found.extend(collect_locks(value))

    elif isinstance(obj, list):
        for item in obj:
            found.extend(collect_locks(item))

    return found

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
            "missing_lock_keys": [],
            "error": None,
        }

        if not path.exists():
            item["error"] = "artifact_missing"
            result["artifact_results"].append(item)
            continue

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            locks = collect_locks(data)

            missing = sorted({
                key
                for block in locks
                for key in LOCK_KEYS
                if key not in block
            })

            item["phase"] = data.get("phase")
            item["certified"] = data.get("certified") is True
            item["lock_blocks_found"] = len(locks)
            item["all_found_locks_false"] = (
                len(locks) > 0
                and all(block.get(key) is False for block in locks for key in LOCK_KEYS if key in block)
            )
            item["missing_lock_keys"] = missing

        except Exception as exc:
            item["error"] = f"{type(exc).__name__}: {exc}"

        result["artifact_results"].append(item)

    result["checks"]["all_artifacts_exist"] = all(x["exists"] for x in result["artifact_results"])
    result["checks"]["all_artifacts_certified"] = all(x["certified"] for x in result["artifact_results"])
    result["checks"]["all_artifacts_have_lock_blocks"] = all(x["lock_blocks_found"] > 0 for x in result["artifact_results"])
    result["checks"]["all_found_locks_false"] = all(x["all_found_locks_false"] for x in result["artifact_results"])
    result["checks"]["no_artifact_parse_errors"] = all(x["error"] is None for x in result["artifact_results"])

    result["pipeline_summary"] = {
        "from": "31A_HISTORICAL_BARS_FETCH_VALIDATION",
        "to": "32C_MANUAL_PROMOTION_GATE_STUB",
        "real_capability_added": [
            "single-symbol yfinance historical bar fetch",
            "multi-symbol historical bar validation",
            "bar iterator",
            "single-candidate dry run through fetched bars",
            "bar-only metrics generation",
            "review-only scorecard generation",
            "blocked manual promotion gate stub",
        ],
        "still_disabled": [
            "historical replay execution flag",
            "trade simulation",
            "strategy execution",
            "learning",
            "promotion",
            "registry writes",
            "broker execution",
            "live execution",
        ],
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

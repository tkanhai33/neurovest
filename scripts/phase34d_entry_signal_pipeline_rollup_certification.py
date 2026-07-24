#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "34D_entry_signal_pipeline_rollup_certification_latest.json"
PHASE = "34D_ENTRY_SIGNAL_PIPELINE_ROLLUP_CERTIFICATION"

ARTIFACTS = [
    "34A_entry_signal_rule_contract_stub_latest.json",
    "34B_entry_signal_rule_validation_stub_latest.json",
    "34C_entry_signal_generator_disabled_stub_latest.json",
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

try:
    for name in ARTIFACTS:
        path = SANDBOX / name
        item = {
            "artifact": name,
            "exists": path.exists(),
            "phase": None,
            "certified": False,
            "checks": {},
            "error": None,
        }

        if not path.exists():
            item["error"] = "artifact_missing"
            result["artifact_results"].append(item)
            continue

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            item["phase"] = data.get("phase")
            item["certified"] = data.get("certified") is True
            item["checks"] = data.get("checks", {})
        except Exception as exc:
            item["error"] = f"{type(exc).__name__}: {exc}"

        result["artifact_results"].append(item)

    all_checks = []
    for item in result["artifact_results"]:
        checks = item.get("checks", {})
        if isinstance(checks, dict):
            all_checks.append(checks)

    result["checks"]["all_artifacts_exist"] = all(x["exists"] for x in result["artifact_results"])
    result["checks"]["all_artifacts_certified"] = all(x["certified"] for x in result["artifact_results"])
    result["checks"]["no_artifact_errors"] = all(x["error"] is None for x in result["artifact_results"])
    result["checks"]["entry_generation_disabled_proven"] = any(
        c.get("entry_signal_generation_disabled") is True or c.get("entry_generation_disabled") is True
        for c in all_checks
    )
    result["checks"]["entry_signals_zero_proven"] = any(
        c.get("entry_signals_zero") is True for c in all_checks
    )
    result["checks"]["strategy_logic_disabled_proven"] = any(
        c.get("strategy_logic_disabled") is True for c in all_checks
    )
    result["checks"]["trade_events_zero_proven"] = any(
        c.get("trade_events_zero") is True or c.get("trade_event_not_created") is True
        for c in all_checks
    )
    result["checks"]["all_safety_locks_false_proven"] = all(
        c.get("all_safety_locks_false") is True for c in all_checks if "all_safety_locks_false" in c
    )

    result["pipeline_summary"] = {
        "from": "34A_ENTRY_SIGNAL_RULE_CONTRACT_STUB",
        "to": "34C_ENTRY_SIGNAL_GENERATOR_DISABLED_STUB",
        "certified_capability": [
            "entry rule contract shape",
            "disabled entry rule validation",
            "unsafe enabled rule rejection",
            "disabled entry signal generator path",
        ],
        "current_behavior": [
            "entry rules remain disabled",
            "entry signal generation remains disabled",
            "zero entry signals",
            "zero trade events",
            "strategy logic disabled",
        ],
        "still_disabled": [
            "real entry rule logic",
            "entry signal generation",
            "exit signal generation",
            "actual trade simulation",
            "learning",
            "promotion",
            "registry writes",
            "broker execution",
            "live execution",
        ],
        "next_recommended_phase": "34E_HANDOFF_BUNDLE_REFRESH",
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

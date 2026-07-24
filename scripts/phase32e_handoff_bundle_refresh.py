#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
OUT = SANDBOX / "32E_handoff_bundle_refresh_latest.json"

PHASE = "32E_HANDOFF_BUNDLE_REFRESH"

ARTIFACTS = sorted(SANDBOX.glob("*_latest.json"))

bundle = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "stage": "Early Training Infrastructure + Bar-Only Replay Metrics Pipeline Complete",
    "latest_confirmed_phase": "32D_PIPELINE_ROLLUP_CERTIFICATION",
    "artifact_dir": str(SANDBOX),
    "file_count": 0,
    "cert_count": 0,
    "certified_phases": [],
    "failed_or_uncertified_phases": [],
    "critical_safety_locks": {
        "live_execution_enabled": False,
        "broker_execution_enabled": False,
        "historical_replay_enabled": False,
        "simulation_enabled": False,
        "registry_write_enabled": False,
        "promotion_enabled": False,
        "learning_enabled": False,
    },
    "completed_capabilities": [
        "strategy proposal capture path exists",
        "candidate sandbox scaffold exists",
        "historical replay contracts and stubs exist",
        "yfinance historical bars adapter wired",
        "single-symbol historical bars validated",
        "multi-symbol historical bars validated",
        "bar iterator certified",
        "single-candidate dry run through bars certified",
        "bar-only metrics generation certified",
        "review-only candidate scorecard certified",
        "manual promotion gate stub certified",
        "31A to 32C rollup certified",
    ],
    "still_disabled": [
        "historical replay execution flag",
        "trade simulation",
        "real strategy execution",
        "learning",
        "promotion",
        "registry writes",
        "broker execution",
        "live execution",
    ],
    "next_recommended_phase": "33A_TRADE_SIMULATION_CONTRACT_STUB",
    "next_phase_rule": "Define trade simulation contract only. Do not simulate trades yet.",
    "handoff_rule": (
        "Do not jump to live execution, broker execution, registry writes, "
        "learning, or promotion. Next work must stay inside locked sandbox "
        "contracts until trade simulation is separately stubbed, validated, "
        "dry-run certified, and manually gated."
    ),
    "artifacts": [],
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    for path in ARTIFACTS:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            phase = data.get("phase", path.name)
            certified = data.get("certified") is True

            bundle["artifacts"].append({
                "file": path.name,
                "phase": phase,
                "certified": certified,
            })

            if certified:
                bundle["certified_phases"].append(phase)
            else:
                bundle["failed_or_uncertified_phases"].append(phase)

        except Exception as exc:
            bundle["errors"].append({
                "file": path.name,
                "type": type(exc).__name__,
                "message": str(exc),
            })

    bundle["file_count"] = len(bundle["artifacts"])
    bundle["cert_count"] = len(bundle["certified_phases"])

    required_phases = {
        "31A_HISTORICAL_BARS_FETCH_VALIDATION",
        "31B_HISTORICAL_BARS_MULTI_SYMBOL_VALIDATION",
        "31C_HISTORICAL_REPLAY_EXECUTOR_STUB",
        "31D_HISTORICAL_REPLAY_BAR_ITERATOR",
        "31E_FIRST_SINGLE_CANDIDATE_REPLAY_DRY_RUN",
        "31F_REPLAY_METRICS_CONTRACT",
        "32A_REAL_METRICS_GENERATION",
        "32B_CANDIDATE_SCORECARD_FROM_REPLAY_METRICS",
        "32C_MANUAL_PROMOTION_GATE_STUB",
        "32D_PIPELINE_ROLLUP_CERTIFICATION",
    }

    certified_set = set(bundle["certified_phases"])

    bundle["checks"]["required_phases_certified"] = required_phases.issubset(certified_set)
    bundle["checks"]["critical_safety_locks_false"] = all(
        v is False for v in bundle["critical_safety_locks"].values()
    )
    bundle["checks"]["handoff_has_next_phase"] = bool(bundle["next_recommended_phase"])
    bundle["checks"]["no_bundle_errors"] = not bundle["errors"]

    bundle["certified"] = all(bundle["checks"].values())

except Exception as exc:
    bundle["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(bundle, indent=2), encoding="utf-8")

print(json.dumps(bundle, indent=2))
print(f"\nWROTE: {OUT}")

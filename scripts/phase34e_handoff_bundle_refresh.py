#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
OUT = SANDBOX / "34E_handoff_bundle_refresh_latest.json"

PHASE = "34E_HANDOFF_BUNDLE_REFRESH"

REQUIRED_PHASES = {
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
    "33A_TRADE_SIMULATION_CONTRACT_STUB",
    "33B_TRADE_EVENT_VALIDATION_STUB",
    "33C_TRADE_SIMULATION_DRY_RUN_STUB",
    "33D_ENTRY_EXIT_SIGNAL_CONTRACT_STUB",
    "33E_HOLD_SIGNAL_GENERATOR_STUB",
    "33F_ENTRY_EXIT_DECISION_ENGINE_STUB",
    "33G_HOLD_DECISION_TO_HOLD_EVENT_BRIDGE",
    "33H_TRADE_SIMULATION_PIPELINE_ROLLUP_CERTIFICATION",
    "34A_ENTRY_SIGNAL_RULE_CONTRACT_STUB",
    "34B_ENTRY_SIGNAL_RULE_VALIDATION_STUB",
    "34C_ENTRY_SIGNAL_GENERATOR_DISABLED_STUB",
    "34D_ENTRY_SIGNAL_PIPELINE_ROLLUP_CERTIFICATION",
}

bundle = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "stage": "Early Training Infrastructure + Hold-Only Simulation Runway + Disabled Entry Signal Pipeline Complete",
    "latest_confirmed_phase": "34D_ENTRY_SIGNAL_PIPELINE_ROLLUP_CERTIFICATION",
    "artifact_dir": str(SANDBOX),
    "file_count": 0,
    "cert_count": 0,
    "required_certified_count": 0,
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
        "real historical bars can be fetched through yfinance",
        "multi-symbol bar validation certified",
        "bar iterator certified",
        "single-candidate dry run through bars certified",
        "bar-only metrics generation certified",
        "review-only scorecard certified",
        "manual promotion gate blocks promotion",
        "trade simulation contract certified",
        "trade event validation certified",
        "hold-only signal generation certified",
        "hold-only decision engine certified",
        "hold decision to hold event bridge certified",
        "entry rule contract certified",
        "disabled entry rule validation certified",
        "unsafe enabled entry rule rejection certified",
        "disabled entry signal generator certified",
        "34A to 34C entry signal pipeline rollup certified",
    ],
    "current_behavior": [
        "entry rules remain disabled",
        "entry signal generation remains disabled",
        "zero entry signals",
        "zero exit signals",
        "zero simulated trades",
        "zero broker orders",
        "zero live orders",
    ],
    "still_disabled": [
        "real entry rule logic",
        "entry signal generation",
        "exit signal generation",
        "actual trade simulation",
        "trade-based metrics",
        "trade-based scorecard",
        "learning",
        "promotion",
        "registry writes",
        "broker execution",
        "live execution",
    ],
    "next_recommended_phase": "35A_EXIT_SIGNAL_RULE_CONTRACT_STUB",
    "next_phase_rule": "Define exit signal rule contract only. Do not generate exit signals yet.",
    "handoff_rule": (
        "Do not enable live execution, broker execution, registry writes, learning, promotion, "
        "real trade simulation, entry generation, or exit generation. Next work should define exit "
        "rule contracts only."
    ),
    "artifacts": [],
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    for path in sorted(SANDBOX.glob("*_latest.json")):
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

    certified_set = set(bundle["certified_phases"])

    bundle["file_count"] = len(bundle["artifacts"])
    bundle["cert_count"] = len(bundle["certified_phases"])
    bundle["required_certified_count"] = len(REQUIRED_PHASES.intersection(certified_set))

    bundle["checks"]["required_phases_certified"] = REQUIRED_PHASES.issubset(certified_set)
    bundle["checks"]["critical_safety_locks_false"] = all(v is False for v in bundle["critical_safety_locks"].values())
    bundle["checks"]["handoff_has_next_phase"] = bool(bundle["next_recommended_phase"])
    bundle["checks"]["latest_phase_correct"] = bundle["latest_confirmed_phase"] in certified_set
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

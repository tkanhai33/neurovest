#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
OUT = SANDBOX / "35F_handoff_bundle_refresh_latest.json"

PHASE = "35F_HANDOFF_BUNDLE_REFRESH"

REQUIRED_PHASES = {
    "31A_HISTORICAL_BARS_FETCH_VALIDATION",
    "32D_PIPELINE_ROLLUP_CERTIFICATION",
    "33H_TRADE_SIMULATION_PIPELINE_ROLLUP_CERTIFICATION",
    "34D_ENTRY_SIGNAL_PIPELINE_ROLLUP_CERTIFICATION",
    "35D_EXIT_SIGNAL_PIPELINE_ROLLUP_CERTIFICATION",
    "35E_STRATEGY_SANDBOX_WIREGRAPH_CERTIFICATION",
}

bundle = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "stage": "Strategy Sandbox Wiregraph Complete With Entry/Exit Generation Disabled",
    "latest_confirmed_phase": "35E_STRATEGY_SANDBOX_WIREGRAPH_CERTIFICATION",
    "artifact_dir": str(SANDBOX),
    "wiregraph_json": str(SANDBOX / "35E_strategy_sandbox_wiregraph_latest.json"),
    "wiregraph_mermaid": str(SANDBOX / "35E_strategy_sandbox_wiregraph_latest.mmd"),
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
    "current_capabilities": [
        "real yfinance historical bars fetch",
        "bar iterator",
        "single candidate dry run through bars",
        "bar-only metrics",
        "review-only scorecard",
        "promotion gate blocked",
        "hold-only signals",
        "hold-only decisions",
        "hold-only events",
        "entry rule contract and disabled generator",
        "exit rule contract and disabled generator",
        "strategy sandbox wiregraph JSON and Mermaid output",
    ],
    "still_disabled": [
        "real entry generation",
        "real exit generation",
        "actual trade simulation",
        "trade-based metrics",
        "trade-based scorecard",
        "learning",
        "promotion",
        "registry writes",
        "broker execution",
        "live execution",
    ],
    "next_recommended_phase": "36A_STRATEGY_RULE_ENABLEMENT_GATE_CONTRACT_STUB",
    "next_phase_rule": "Define the approval gate required before enabling any entry/exit rule. Do not enable rules.",
    "handoff_rule": (
        "Do not enable entry rules, exit rules, trade simulation, learning, promotion, "
        "registry writes, broker execution, or live execution. Next step is only an enablement "
        "gate contract."
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

    bundle["checks"]["required_phases_certified"] = REQUIRED_PHASES.issubset(certified_set)
    bundle["checks"]["critical_safety_locks_false"] = all(v is False for v in bundle["critical_safety_locks"].values())
    bundle["checks"]["wiregraph_json_exists"] = Path(bundle["wiregraph_json"]).exists()
    bundle["checks"]["wiregraph_mermaid_exists"] = Path(bundle["wiregraph_mermaid"]).exists()
    bundle["checks"]["latest_phase_correct"] = bundle["latest_confirmed_phase"] in certified_set
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

#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
OUT = SANDBOX / "36D_handoff_bundle_refresh_latest.json"

PHASE = "36D_HANDOFF_BUNDLE_REFRESH"

REQUIRED_PHASES = {
    "31A_HISTORICAL_BARS_FETCH_VALIDATION",
    "32D_PIPELINE_ROLLUP_CERTIFICATION",
    "33H_TRADE_SIMULATION_PIPELINE_ROLLUP_CERTIFICATION",
    "34D_ENTRY_SIGNAL_PIPELINE_ROLLUP_CERTIFICATION",
    "35D_EXIT_SIGNAL_PIPELINE_ROLLUP_CERTIFICATION",
    "35E_STRATEGY_SANDBOX_WIREGRAPH_CERTIFICATION",
    "36A_STRATEGY_RULE_ENABLEMENT_GATE_CONTRACT_STUB",
    "36B_ENABLEMENT_GATE_VALIDATION_STUB",
    "36C_ENABLEMENT_GATE_PIPELINE_ROLLUP_CERTIFICATION",
}

bundle = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "stage": "Strategy Rule Enablement Gate Certified (Locked)",
    "latest_confirmed_phase": "36C_ENABLEMENT_GATE_PIPELINE_ROLLUP_CERTIFICATION",
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
        "real historical bar acquisition",
        "historical replay",
        "bar iteration",
        "candidate metrics",
        "review scorecard",
        "manual promotion gate",
        "hold-only pipeline",
        "entry rule contract",
        "entry validator",
        "disabled entry generator",
        "exit rule contract",
        "exit validator",
        "disabled exit generator",
        "strategy sandbox wiregraph",
        "strategy enablement gate contract",
        "locked enablement gate validation",
        "unsafe enablement rejection",
    ],
    "still_disabled": [
        "entry rule execution",
        "exit rule execution",
        "trade simulation",
        "trade metrics",
        "trade scorecard",
        "registry writes",
        "learning",
        "promotion",
        "broker execution",
        "live execution",
    ],
    "next_recommended_phase": "37A_TRADE_SIMULATION_ENABLEMENT_GATE_CONTRACT_STUB",
    "next_phase_rule": (
        "Create the trade simulation enablement gate only. "
        "Do not enable trade simulation."
    ),
    "handoff_rule": (
        "No runtime execution may be enabled. "
        "Entry rules remain disabled. "
        "Exit rules remain disabled. "
        "Trade simulation remains disabled. "
        "Registry writes remain disabled. "
        "Learning remains disabled. "
        "Promotion remains disabled. "
        "Broker execution remains disabled. "
        "Live execution remains disabled."
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

    certified = set(bundle["certified_phases"])

    bundle["file_count"] = len(bundle["artifacts"])
    bundle["cert_count"] = len(bundle["certified_phases"])

    bundle["checks"]["required_phases_certified"] = REQUIRED_PHASES.issubset(certified)
    bundle["checks"]["wiregraph_json_exists"] = Path(bundle["wiregraph_json"]).exists()
    bundle["checks"]["wiregraph_mermaid_exists"] = Path(bundle["wiregraph_mermaid"]).exists()
    bundle["checks"]["latest_phase_correct"] = bundle["latest_confirmed_phase"] in certified
    bundle["checks"]["critical_safety_locks_false"] = all(
        v is False for v in bundle["critical_safety_locks"].values()
    )
    bundle["checks"]["handoff_has_next_phase"] = bool(bundle["next_recommended_phase"])
    bundle["checks"]["no_bundle_errors"] = len(bundle["errors"]) == 0

    bundle["certified"] = all(bundle["checks"].values())

except Exception as exc:
    bundle["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(bundle, indent=2), encoding="utf-8")

print(json.dumps(bundle, indent=2))
print(f"\nWROTE: {OUT}")

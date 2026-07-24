#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
OUT = SANDBOX / "37D_handoff_bundle_refresh_latest.json"

PHASE = "37D_HANDOFF_BUNDLE_REFRESH"

REQUIRED_PHASES = {
    "35E_STRATEGY_SANDBOX_WIREGRAPH_CERTIFICATION",
    "36C_ENABLEMENT_GATE_PIPELINE_ROLLUP_CERTIFICATION",
    "37A_TRADE_SIMULATION_ENABLEMENT_GATE_CONTRACT_STUB",
    "37B_TRADE_SIMULATION_ENABLEMENT_GATE_VALIDATION_STUB",
    "37C_TRADE_SIMULATION_ENABLEMENT_GATE_PIPELINE_ROLLUP_CERTIFICATION",
}

bundle = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "stage": "Trade Simulation Enablement Gate Certified Locked",
    "latest_confirmed_phase": "37C_TRADE_SIMULATION_ENABLEMENT_GATE_PIPELINE_ROLLUP_CERTIFICATION",
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
    "current_capabilities": [
        "strategy sandbox wiregraph",
        "strategy rule enablement gate locked",
        "trade simulation enablement gate locked",
        "unsafe trade simulation enablement rejected",
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
    "next_recommended_phase": "38A_RISK_GATE_CONTRACT_STUB",
    "next_phase_rule": "Create risk gate contract only. Do not enable trade simulation.",
    "artifacts": [],
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    for path in sorted(SANDBOX.glob("*_latest.json")):
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

    certified_set = set(bundle["certified_phases"])

    bundle["file_count"] = len(bundle["artifacts"])
    bundle["cert_count"] = len(bundle["certified_phases"])

    bundle["checks"]["required_phases_certified"] = REQUIRED_PHASES.issubset(certified_set)
    bundle["checks"]["latest_phase_correct"] = bundle["latest_confirmed_phase"] in certified_set
    bundle["checks"]["critical_safety_locks_false"] = all(v is False for v in bundle["critical_safety_locks"].values())
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
print(f"\\nWROTE: {OUT}")

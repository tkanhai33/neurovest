#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
OUT = SANDBOX / "39C_handoff_bundle_refresh_latest.json"

PHASE = "39C_HANDOFF_BUNDLE_REFRESH"

REQUIRED_PHASES = {
    "35E_STRATEGY_SANDBOX_WIREGRAPH_CERTIFICATION",
    "38C_RISK_GATE_PIPELINE_ROLLUP_CERTIFICATION",
    "39A_MASTER_SANDBOX_GATE_WIREGRAPH_REFRESH",
    "39B_MASTER_SANDBOX_GATE_WIREGRAPH_ROLLUP_CERTIFICATION",
}

bundle = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "stage": "Master Sandbox Gate Wiregraph Certified",
    "latest_confirmed_phase": "39B_MASTER_SANDBOX_GATE_WIREGRAPH_ROLLUP_CERTIFICATION",
    "artifact_dir": str(SANDBOX),
    "wiregraph_json": str(SANDBOX / "39A_master_sandbox_gate_wiregraph_latest.json"),
    "wiregraph_mermaid": str(SANDBOX / "39A_master_sandbox_gate_wiregraph_latest.mmd"),
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
        "master sandbox dependency wiregraph",
        "strategy rule gate represented",
        "trade simulation gate represented",
        "risk gate represented",
        "broker disabled endpoint represented",
        "live disabled endpoint represented",
    ],
    "still_disabled": [
        "entry generation",
        "exit generation",
        "strategy enablement",
        "trade simulation",
        "risk gate pass",
        "trade metrics",
        "trade scorecard",
        "registry writes",
        "learning",
        "promotion",
        "broker execution",
        "live execution",
    ],
    "next_recommended_phase": "40A_SANDBOX_RUNTIME_DEPENDENCY_TRACE_STUB",
    "next_phase_rule": "Create runtime dependency trace only. Do not enable runtime.",
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
    bundle["checks"]["wiregraph_json_exists"] = Path(bundle["wiregraph_json"]).exists()
    bundle["checks"]["wiregraph_mermaid_exists"] = Path(bundle["wiregraph_mermaid"]).exists()
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

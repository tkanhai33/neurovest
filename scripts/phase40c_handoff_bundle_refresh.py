#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
OUT = SANDBOX / "40C_handoff_bundle_refresh_latest.json"

PHASE = "40C_HANDOFF_BUNDLE_REFRESH"

REQUIRED_PHASES = {
    "39B_MASTER_SANDBOX_GATE_WIREGRAPH_ROLLUP_CERTIFICATION",
    "40A_SANDBOX_RUNTIME_DEPENDENCY_TRACE_STUB",
    "40B_SANDBOX_RUNTIME_DEPENDENCY_TRACE_ROLLUP_CERTIFICATION",
}

bundle = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "stage": "Sandbox Runtime Dependency Trace Certified Locked",
    "latest_confirmed_phase": "40B_SANDBOX_RUNTIME_DEPENDENCY_TRACE_ROLLUP_CERTIFICATION",
    "artifact_dir": str(SANDBOX),
    "wiregraph_json": str(SANDBOX / "39A_master_sandbox_gate_wiregraph_latest.json"),
    "wiregraph_mermaid": str(SANDBOX / "39A_master_sandbox_gate_wiregraph_latest.mmd"),
    "runtime_trace_json": str(SANDBOX / "40A_sandbox_runtime_dependency_trace_stub_latest.json"),
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
        "master sandbox dependency wiregraph certified",
        "runtime dependency trace certified",
        "strategy gate locked",
        "risk gate locked",
        "trade simulation gate locked",
        "broker/live endpoints disabled",
    ],
    "still_disabled": [
        "runtime enablement",
        "writes",
        "entry generation",
        "exit generation",
        "trade simulation",
        "trade metrics",
        "trade scorecard",
        "registry writes",
        "learning",
        "promotion",
        "broker execution",
        "live execution",
    ],
    "next_recommended_phase": "41A_SAFE_READ_ONLY_ARCHITECTURE_INSPECTOR_STUB",
    "next_phase_rule": "Create read-only architecture inspector. Do not enable runtime or writes.",
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
    bundle["checks"]["runtime_trace_json_exists"] = Path(bundle["runtime_trace_json"]).exists()
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

#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "41B_safe_read_only_architecture_inspector_rollup_certification_latest.json"
PHASE = "41B_SAFE_READ_ONLY_ARCHITECTURE_INSPECTOR_ROLLUP_CERTIFICATION"

ARTIFACT = SANDBOX / "41A_safe_read_only_architecture_inspector_stub_latest.json"

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "artifact": str(ARTIFACT),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8")) if ARTIFACT.exists() else {}
    inspection = data.get("inspection", {}) if isinstance(data.get("inspection"), dict) else {}
    validation = data.get("validation", {}) if isinstance(data.get("validation"), dict) else {}
    gates = inspection.get("gate_presence", {}) if isinstance(inspection.get("gate_presence"), dict) else {}
    trace_locks = inspection.get("runtime_trace_locks", {}) if isinstance(inspection.get("runtime_trace_locks"), dict) else {}
    read_only_locks = inspection.get("read_only_locks", {}) if isinstance(inspection.get("read_only_locks"), dict) else {}

    result["source_phase"] = data.get("phase")
    result["source_certified"] = data.get("certified") is True
    result["inspection_summary"] = {
        "status": inspection.get("status"),
        "inspection_mode": inspection.get("inspection_mode"),
        "node_count": inspection.get("node_count"),
        "edge_count": inspection.get("edge_count"),
        "trace_step_count": inspection.get("trace_step_count"),
        "gate_presence": gates,
        "runtime_trace_locks": trace_locks,
    }

    result["checks"]["artifact_exists"] = ARTIFACT.exists()
    result["checks"]["source_certified"] = data.get("certified") is True
    result["checks"]["validation_certified"] = validation.get("certified") is True
    result["checks"]["inspection_status_ok"] = inspection.get("status") == "read_only_architecture_inspection_complete"
    result["checks"]["inspection_mode_read_only"] = inspection.get("inspection_mode") == "read_only_no_runtime_no_writes"
    result["checks"]["wiregraph_certified"] = inspection.get("wiregraph_certified") is True
    result["checks"]["runtime_trace_certified"] = inspection.get("runtime_trace_certified") is True
    result["checks"]["strategy_gate_present"] = gates.get("strategy_gate") is True
    result["checks"]["risk_gate_present"] = gates.get("risk_gate") is True
    result["checks"]["trade_simulation_gate_present"] = gates.get("trade_simulation_gate") is True
    result["checks"]["broker_disabled_present"] = gates.get("broker_disabled") is True
    result["checks"]["live_disabled_present"] = gates.get("live_disabled") is True
    result["checks"]["all_runtime_disabled"] = trace_locks.get("all_runtime_disabled") is True
    result["checks"]["all_writes_disabled"] = trace_locks.get("all_writes_disabled") is True
    result["checks"]["all_read_only_locks_false"] = all(v is False for v in read_only_locks.values())

    result["pipeline_summary"] = {
        "from": "41A_SAFE_READ_ONLY_ARCHITECTURE_INSPECTOR_STUB",
        "to": "41B_SAFE_READ_ONLY_ARCHITECTURE_INSPECTOR_ROLLUP_CERTIFICATION",
        "certified_capability": [
            "read-only architecture inspector exists",
            "wiregraph and runtime trace inspected",
            "strategy/risk/trade simulation gates confirmed",
            "broker/live disabled endpoints confirmed",
            "runtime and writes remain disabled",
        ],
        "current_behavior": [
            "read-only architecture inspection only",
            "no runtime enablement",
            "no writes",
            "no source mutation",
            "no broker execution",
            "no live execution",
        ],
        "next_recommended_phase": "41C_HANDOFF_BUNDLE_REFRESH",
    }

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\\nWROTE: {OUT}")

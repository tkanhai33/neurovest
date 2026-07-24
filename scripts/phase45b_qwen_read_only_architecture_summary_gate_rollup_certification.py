#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "45B_qwen_read_only_architecture_summary_gate_rollup_certification_latest.json"
PHASE = "45B_QWEN_READ_ONLY_ARCHITECTURE_SUMMARY_GATE_ROLLUP_CERTIFICATION"

ARTIFACT = SANDBOX / "45A_qwen_read_only_architecture_summary_gate_stub_latest.json"

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
    gate = data.get("summary_gate", {}) if isinstance(data.get("summary_gate"), dict) else {}
    validation = data.get("validation", {}) if isinstance(data.get("validation"), dict) else {}
    locks = gate.get("summary_gate_locks", {}) if isinstance(gate.get("summary_gate_locks"), dict) else {}

    result["source_phase"] = data.get("phase")
    result["source_certified"] = data.get("certified") is True
    result["gate_summary"] = {
        "gate_id": gate.get("gate_id"),
        "status": gate.get("status"),
        "context_mode": gate.get("context_mode"),
        "sample_response_mode": gate.get("sample_response_mode"),
        "allowed_summary_scope": gate.get("allowed_summary_scope", []),
        "forbidden_summary_scope": gate.get("forbidden_summary_scope", []),
    }

    result["checks"]["artifact_exists"] = ARTIFACT.exists()
    result["checks"]["source_certified"] = data.get("certified") is True
    result["checks"]["validation_certified"] = validation.get("certified") is True
    result["checks"]["status_locked_read_only"] = gate.get("status") == "qwen_summary_gate_locked_read_only"
    result["checks"]["context_certified"] = gate.get("context_certified") is True
    result["checks"]["sample_response_certified"] = gate.get("sample_response_certified") is True
    result["checks"]["summary_allowed"] = locks.get("summary_allowed") is True
    result["checks"]["architecture_read_allowed"] = locks.get("architecture_read_allowed") is True
    result["checks"]["actions_not_allowed"] = locks.get("actions_allowed") is False
    result["checks"]["writes_not_allowed"] = locks.get("writes_allowed") is False
    result["checks"]["runtime_not_allowed"] = locks.get("runtime_allowed") is False
    result["checks"]["source_mutation_not_allowed"] = locks.get("source_mutation_allowed") is False
    result["checks"]["strategy_enablement_not_allowed"] = locks.get("strategy_enablement_allowed") is False
    result["checks"]["trade_simulation_not_allowed"] = locks.get("trade_simulation_allowed") is False
    result["checks"]["learning_not_allowed"] = locks.get("learning_allowed") is False
    result["checks"]["promotion_not_allowed"] = locks.get("promotion_allowed") is False
    result["checks"]["broker_execution_not_allowed"] = locks.get("broker_execution_allowed") is False
    result["checks"]["live_execution_not_allowed"] = locks.get("live_execution_allowed") is False

    result["pipeline_summary"] = {
        "from": "45A_QWEN_READ_ONLY_ARCHITECTURE_SUMMARY_GATE_STUB",
        "to": "45B_QWEN_READ_ONLY_ARCHITECTURE_SUMMARY_GATE_ROLLUP_CERTIFICATION",
        "certified_capability": [
            "Qwen architecture summary gate exists",
            "Qwen summary is allowed",
            "Qwen architecture reading is allowed",
            "Qwen actions are blocked",
            "Qwen writes/runtime/source mutation are blocked",
            "Qwen strategy/simulation/learning/promotion are blocked",
            "Qwen broker/live execution is blocked",
        ],
        "current_behavior": [
            "Qwen may summarize locked architecture only",
            "Qwen may explain disabled capabilities",
            "Qwen may recommend read-only next phase",
            "Qwen may not produce implementation or execution instructions",
        ],
        "next_recommended_phase": "45C_HANDOFF_BUNDLE_REFRESH",
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

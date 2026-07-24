#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX_DIR = ROOT / "backend/app/stacks/strategy_candidate_sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

CONTRACT = SANDBOX_DIR / "qwen_context_response_contract.py"

OUT_DIR = ROOT / "runtime/strategy_candidate_sandbox"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT = OUT_DIR / "43A_qwen_context_response_contract_stub_latest.json"

PHASE = "43A_QWEN_CONTEXT_RESPONSE_CONTRACT_STUB"

CONTRACT.write_text('''from __future__ import annotations

from typing import Any


QWEN_RESPONSE_KEYS = [
    "response_id",
    "context_phase",
    "response_mode",
    "summary",
    "locked_gates",
    "missing_context",
    "recommended_next_read_only_phase",
    "actions_requested",
    "writes_requested",
    "runtime_requested",
    "broker_or_live_requested",
]


def build_qwen_read_only_response_contract(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "response_id": "qwen_read_only_response_001",
        "context_phase": context.get("handoff_phase") if isinstance(context, dict) else None,
        "response_mode": "read_only_summary_no_actions",
        "summary": "Qwen may summarize certified architecture context only.",
        "locked_gates": [
            "strategy_rule_enablement_gate",
            "risk_gate",
            "trade_simulation_gate",
            "broker_execution",
            "live_execution",
        ],
        "missing_context": [],
        "recommended_next_read_only_phase": "43B_QWEN_CONTEXT_RESPONSE_CONTRACT_ROLLUP_CERTIFICATION",
        "actions_requested": False,
        "writes_requested": False,
        "runtime_requested": False,
        "broker_or_live_requested": False,
    }


def validate_qwen_read_only_response_contract(payload: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "payload_is_dict": isinstance(payload, dict),
        "all_response_keys_present": isinstance(payload, dict) and all(k in payload for k in QWEN_RESPONSE_KEYS),
        "response_mode_read_only": isinstance(payload, dict) and payload.get("response_mode") == "read_only_summary_no_actions",
        "actions_not_requested": isinstance(payload, dict) and payload.get("actions_requested") is False,
        "writes_not_requested": isinstance(payload, dict) and payload.get("writes_requested") is False,
        "runtime_not_requested": isinstance(payload, dict) and payload.get("runtime_requested") is False,
        "broker_or_live_not_requested": isinstance(payload, dict) and payload.get("broker_or_live_requested") is False,
        "locked_gates_present": isinstance(payload, dict) and len(payload.get("locked_gates", [])) > 0,
        "has_next_read_only_phase": isinstance(payload, dict) and bool(payload.get("recommended_next_read_only_phase")),
    }

    return {
        "status": "ok" if all(checks.values()) else "failed",
        "checks": checks,
        "certified": all(checks.values()),
    }
''', encoding="utf-8")

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "created_file": str(CONTRACT),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    import py_compile
    py_compile.compile(str(CONTRACT), doraise=True)

    from backend.app.stacks.strategy_candidate_sandbox.qwen_context_response_contract import (
        QWEN_RESPONSE_KEYS,
        build_qwen_read_only_response_contract,
        validate_qwen_read_only_response_contract,
    )

    context_path = OUT_DIR / "42A_qwen_read_only_architecture_context_stub_latest.json"
    context_artifact = json.loads(context_path.read_text(encoding="utf-8"))
    context = context_artifact.get("context", {})

    response = build_qwen_read_only_response_contract(context)
    validation = validate_qwen_read_only_response_contract(response)

    result["qwen_response_keys"] = QWEN_RESPONSE_KEYS
    result["sample_response"] = response
    result["validation"] = validation

    result["checks"]["contract_file_exists"] = CONTRACT.exists()
    result["checks"]["contract_compiles"] = True
    result["checks"]["context_source_exists"] = context_path.exists()
    result["checks"]["validation_certified"] = validation.get("certified") is True
    result["checks"]["response_mode_read_only"] = response.get("response_mode") == "read_only_summary_no_actions"
    result["checks"]["actions_not_requested"] = response.get("actions_requested") is False
    result["checks"]["writes_not_requested"] = response.get("writes_requested") is False
    result["checks"]["runtime_not_requested"] = response.get("runtime_requested") is False
    result["checks"]["broker_or_live_not_requested"] = response.get("broker_or_live_requested") is False

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\\nWROTE: {OUT}")

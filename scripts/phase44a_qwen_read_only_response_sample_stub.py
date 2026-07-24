#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
OUT = SANDBOX / "44A_qwen_read_only_response_sample_stub_latest.json"

PHASE = "44A_QWEN_READ_ONLY_RESPONSE_SAMPLE_STUB"

CONTEXT = SANDBOX / "42A_qwen_read_only_architecture_context_stub_latest.json"
RESPONSE_CONTRACT = SANDBOX / "43A_qwen_context_response_contract_stub_latest.json"

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "context_source": str(CONTEXT),
    "response_contract_source": str(RESPONSE_CONTRACT),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    context_artifact = json.loads(CONTEXT.read_text(encoding="utf-8")) if CONTEXT.exists() else {}
    contract_artifact = json.loads(RESPONSE_CONTRACT.read_text(encoding="utf-8")) if RESPONSE_CONTRACT.exists() else {}

    context = context_artifact.get("context", {})
    response_contract = contract_artifact.get("sample_response", {})

    sample_response = {
        "response_id": "qwen_read_only_sample_response_001",
        "response_mode": "read_only_summary_no_actions",
        "summary": {
            "stage": context.get("stage"),
            "latest_confirmed_phase": context.get("latest_confirmed_phase"),
            "architecture_status": "Certified read-only architecture context is available.",
            "plain_english": (
                "The sandbox can be inspected and summarized, but no runtime, writes, "
                "strategy enablement, trade simulation, broker orders, or live trading are allowed."
            ),
        },
        "locked_gates": response_contract.get("locked_gates", []),
        "allowed_outputs_used": [
            "summarize_current_architecture",
            "explain_locked_gates",
            "recommend_next_read_only_phase",
        ],
        "forbidden_outputs_requested": [],
        "recommended_next_read_only_phase": "44B_QWEN_READ_ONLY_RESPONSE_SAMPLE_ROLLUP_CERTIFICATION",
        "actions_requested": False,
        "writes_requested": False,
        "runtime_requested": False,
        "source_mutation_requested": False,
        "broker_or_live_requested": False,
    }

    checks = {
        "context_exists": CONTEXT.exists(),
        "response_contract_exists": RESPONSE_CONTRACT.exists(),
        "context_certified": context_artifact.get("certified") is True,
        "response_contract_certified": contract_artifact.get("certified") is True,
        "response_mode_read_only": sample_response.get("response_mode") == "read_only_summary_no_actions",
        "locked_gates_present": len(sample_response.get("locked_gates", [])) > 0,
        "actions_not_requested": sample_response.get("actions_requested") is False,
        "writes_not_requested": sample_response.get("writes_requested") is False,
        "runtime_not_requested": sample_response.get("runtime_requested") is False,
        "source_mutation_not_requested": sample_response.get("source_mutation_requested") is False,
        "broker_or_live_not_requested": sample_response.get("broker_or_live_requested") is False,
        "has_next_read_only_phase": bool(sample_response.get("recommended_next_read_only_phase")),
    }

    result["sample_response"] = sample_response
    result["checks"] = checks
    result["certified"] = all(checks.values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\\nWROTE: {OUT}")

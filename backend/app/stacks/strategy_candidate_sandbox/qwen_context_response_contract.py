from __future__ import annotations

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

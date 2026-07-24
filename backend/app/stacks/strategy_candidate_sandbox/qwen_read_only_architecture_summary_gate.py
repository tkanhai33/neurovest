from __future__ import annotations

from typing import Any


SUMMARY_GATE_LOCKS = {
    "summary_allowed": True,
    "architecture_read_allowed": True,
    "actions_allowed": False,
    "writes_allowed": False,
    "runtime_allowed": False,
    "source_mutation_allowed": False,
    "strategy_enablement_allowed": False,
    "trade_simulation_allowed": False,
    "learning_allowed": False,
    "promotion_allowed": False,
    "broker_execution_allowed": False,
    "live_execution_allowed": False,
}


def build_qwen_summary_gate(
    context_artifact: dict[str, Any],
    sample_response_artifact: dict[str, Any],
) -> dict[str, Any]:
    context = context_artifact.get("context", {}) if isinstance(context_artifact, dict) else {}
    sample = sample_response_artifact.get("sample_response", {}) if isinstance(sample_response_artifact, dict) else {}

    return {
        "gate_id": "qwen_read_only_architecture_summary_gate_001",
        "status": "qwen_summary_gate_locked_read_only",
        "context_certified": context_artifact.get("certified") is True if isinstance(context_artifact, dict) else False,
        "sample_response_certified": sample_response_artifact.get("certified") is True if isinstance(sample_response_artifact, dict) else False,
        "context_mode": context.get("context_mode"),
        "sample_response_mode": sample.get("response_mode"),
        "allowed_summary_scope": [
            "certified_architecture_stage",
            "locked_gate_explanation",
            "disabled_capability_summary",
            "read_only_next_phase_recommendation",
        ],
        "forbidden_summary_scope": [
            "implementation_patch",
            "file_write_instruction",
            "runtime_execution_instruction",
            "broker_or_live_trade_instruction",
            "rule_enablement_instruction",
        ],
        "summary_gate_locks": SUMMARY_GATE_LOCKS.copy(),
    }


def validate_qwen_summary_gate(gate: dict[str, Any]) -> dict[str, Any]:
    locks = gate.get("summary_gate_locks", {}) if isinstance(gate, dict) else {}

    checks = {
        "gate_is_dict": isinstance(gate, dict),
        "status_ok": gate.get("status") == "qwen_summary_gate_locked_read_only",
        "context_certified": gate.get("context_certified") is True,
        "sample_response_certified": gate.get("sample_response_certified") is True,
        "summary_allowed": locks.get("summary_allowed") is True,
        "architecture_read_allowed": locks.get("architecture_read_allowed") is True,
        "actions_not_allowed": locks.get("actions_allowed") is False,
        "writes_not_allowed": locks.get("writes_allowed") is False,
        "runtime_not_allowed": locks.get("runtime_allowed") is False,
        "source_mutation_not_allowed": locks.get("source_mutation_allowed") is False,
        "strategy_enablement_not_allowed": locks.get("strategy_enablement_allowed") is False,
        "trade_simulation_not_allowed": locks.get("trade_simulation_allowed") is False,
        "learning_not_allowed": locks.get("learning_allowed") is False,
        "promotion_not_allowed": locks.get("promotion_allowed") is False,
        "broker_execution_not_allowed": locks.get("broker_execution_allowed") is False,
        "live_execution_not_allowed": locks.get("live_execution_allowed") is False,
    }

    return {
        "status": "ok" if all(checks.values()) else "failed",
        "checks": checks,
        "certified": all(checks.values()),
    }

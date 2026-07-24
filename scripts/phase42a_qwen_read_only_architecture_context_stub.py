#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX_DIR = ROOT / "backend/app/stacks/strategy_candidate_sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

CONTEXT = SANDBOX_DIR / "qwen_read_only_architecture_context.py"

OUT_DIR = ROOT / "runtime/strategy_candidate_sandbox"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT = OUT_DIR / "42A_qwen_read_only_architecture_context_stub_latest.json"

PHASE = "42A_QWEN_READ_ONLY_ARCHITECTURE_CONTEXT_STUB"

CONTEXT.write_text('''from __future__ import annotations

from typing import Any


QWEN_CONTEXT_LOCKS = {
    "qwen_can_read_architecture": True,
    "qwen_can_write_files": False,
    "qwen_can_execute_runtime": False,
    "qwen_can_mutate_source": False,
    "qwen_can_enable_strategy_rules": False,
    "qwen_can_enable_trade_simulation": False,
    "qwen_can_enable_learning": False,
    "qwen_can_enable_promotion": False,
    "qwen_can_place_broker_orders": False,
    "qwen_can_live_trade": False,
}


def build_qwen_read_only_architecture_context(
    handoff_bundle: dict[str, Any],
    architecture_inspection: dict[str, Any],
) -> dict[str, Any]:
    return {
        "status": "qwen_read_only_architecture_context_ready",
        "context_mode": "read_only_architecture_context_no_actions",
        "handoff_phase": handoff_bundle.get("phase") if isinstance(handoff_bundle, dict) else None,
        "handoff_certified": handoff_bundle.get("certified") is True if isinstance(handoff_bundle, dict) else False,
        "inspection_phase": architecture_inspection.get("phase") if isinstance(architecture_inspection, dict) else None,
        "inspection_certified": architecture_inspection.get("certified") is True if isinstance(architecture_inspection, dict) else False,
        "stage": handoff_bundle.get("stage") if isinstance(handoff_bundle, dict) else None,
        "latest_confirmed_phase": handoff_bundle.get("latest_confirmed_phase") if isinstance(handoff_bundle, dict) else None,
        "current_capabilities": handoff_bundle.get("current_capabilities", []) if isinstance(handoff_bundle, dict) else [],
        "still_disabled": handoff_bundle.get("still_disabled", []) if isinstance(handoff_bundle, dict) else [],
        "qwen_allowed_outputs": [
            "summarize_current_architecture",
            "identify_missing_context",
            "explain_locked_gates",
            "recommend_next_read_only_phase",
        ],
        "qwen_forbidden_outputs": [
            "write_files",
            "run_runtime",
            "enable_rules",
            "enable_simulation",
            "enable_learning",
            "enable_promotion",
            "place_broker_orders",
            "live_trade",
        ],
        "qwen_context_locks": QWEN_CONTEXT_LOCKS.copy(),
    }


def validate_qwen_read_only_architecture_context(payload: dict[str, Any]) -> dict[str, Any]:
    locks = payload.get("qwen_context_locks", {}) if isinstance(payload, dict) else {}

    checks = {
        "payload_is_dict": isinstance(payload, dict),
        "status_ok": payload.get("status") == "qwen_read_only_architecture_context_ready",
        "context_mode_read_only": payload.get("context_mode") == "read_only_architecture_context_no_actions",
        "handoff_certified": payload.get("handoff_certified") is True,
        "inspection_certified": payload.get("inspection_certified") is True,
        "can_read_architecture_true": locks.get("qwen_can_read_architecture") is True,
        "can_write_files_false": locks.get("qwen_can_write_files") is False,
        "can_execute_runtime_false": locks.get("qwen_can_execute_runtime") is False,
        "can_mutate_source_false": locks.get("qwen_can_mutate_source") is False,
        "can_enable_strategy_rules_false": locks.get("qwen_can_enable_strategy_rules") is False,
        "can_enable_trade_simulation_false": locks.get("qwen_can_enable_trade_simulation") is False,
        "can_enable_learning_false": locks.get("qwen_can_enable_learning") is False,
        "can_enable_promotion_false": locks.get("qwen_can_enable_promotion") is False,
        "can_place_broker_orders_false": locks.get("qwen_can_place_broker_orders") is False,
        "can_live_trade_false": locks.get("qwen_can_live_trade") is False,
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
    "created_file": str(CONTEXT),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    import py_compile
    py_compile.compile(str(CONTEXT), doraise=True)

    from backend.app.stacks.strategy_candidate_sandbox.qwen_read_only_architecture_context import (
        build_qwen_read_only_architecture_context,
        validate_qwen_read_only_architecture_context,
    )

    handoff_path = OUT_DIR / "41C_handoff_bundle_refresh_latest.json"
    inspection_path = OUT_DIR / "41B_safe_read_only_architecture_inspector_rollup_certification_latest.json"

    handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
    inspection = json.loads(inspection_path.read_text(encoding="utf-8"))

    context = build_qwen_read_only_architecture_context(handoff, inspection)
    validation = validate_qwen_read_only_architecture_context(context)

    result["context"] = context
    result["validation"] = validation

    result["checks"]["context_file_exists"] = CONTEXT.exists()
    result["checks"]["context_compiles"] = True
    result["checks"]["handoff_source_exists"] = handoff_path.exists()
    result["checks"]["inspection_source_exists"] = inspection_path.exists()
    result["checks"]["validation_certified"] = validation.get("certified") is True
    result["checks"]["qwen_can_read_architecture"] = context["qwen_context_locks"].get("qwen_can_read_architecture") is True
    result["checks"]["qwen_cannot_write_files"] = context["qwen_context_locks"].get("qwen_can_write_files") is False
    result["checks"]["qwen_cannot_execute_runtime"] = context["qwen_context_locks"].get("qwen_can_execute_runtime") is False
    result["checks"]["qwen_cannot_live_trade"] = context["qwen_context_locks"].get("qwen_can_live_trade") is False

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\\nWROTE: {OUT}")

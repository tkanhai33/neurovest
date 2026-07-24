#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX_DIR = ROOT / "backend/app/stacks/strategy_candidate_sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

VALIDATOR = SANDBOX_DIR / "trade_simulation_enablement_gate_validator.py"

OUT_DIR = ROOT / "runtime/strategy_candidate_sandbox"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT = OUT_DIR / "37B_trade_simulation_enablement_gate_validation_stub_latest.json"

PHASE = "37B_TRADE_SIMULATION_ENABLEMENT_GATE_VALIDATION_STUB"

VALIDATOR.write_text('''from __future__ import annotations

from typing import Any

from backend.app.stacks.strategy_candidate_sandbox.trade_simulation_enablement_gate_contract import (
    validate_locked_trade_simulation_gate,
)

from backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract import SAFETY_LOCKS


def validate_trade_simulation_gate_locked(
    gate: dict[str, Any],
) -> dict[str, Any]:

    base = validate_locked_trade_simulation_gate(gate)

    checks = {
        "base_gate_certified": base.get("certified") is True,
        "trade_simulation_not_allowed": gate.get("trade_simulation_allowed") is False,
        "trade_simulation_disabled": gate.get("trade_simulation_enabled") is False,
        "entry_rules_disabled": gate.get("entry_rules_enabled") is False,
        "exit_rules_disabled": gate.get("exit_rules_enabled") is False,
        "trade_events_zero": gate.get("trade_events_created") == 0,
        "trades_simulated_zero": gate.get("trades_simulated") == 0,
        "metrics_not_generated": gate.get("metrics_generated") is False,
        "scorecard_not_generated": gate.get("scorecard_generated") is False,
        "registry_write_disabled": gate.get("registry_write_enabled") is False,
        "learning_disabled": gate.get("learning_enabled") is False,
        "promotion_disabled": gate.get("promotion_enabled") is False,
        "broker_execution_disabled": gate.get("broker_execution_enabled") is False,
        "live_execution_disabled": gate.get("live_execution_enabled") is False,
        "all_safety_locks_false": all(
            v is False for v in gate.get("safety_locks", {}).values()
        ),
    }

    return {
        "status": "ok" if all(checks.values()) else "failed",
        "checks": checks,
        "certified": all(checks.values()),
        "safety_locks": SAFETY_LOCKS.copy(),
    }


def validate_unsafe_trade_simulation_gate_is_rejected(
    gate: dict[str, Any],
) -> dict[str, Any]:

    unsafe = dict(gate)

    unsafe["manual_approval_present"] = True
    unsafe["entry_rules_enabled"] = True
    unsafe["exit_rules_enabled"] = True
    unsafe["risk_gate_passed"] = True
    unsafe["trade_simulation_allowed"] = True
    unsafe["trade_simulation_enabled"] = True

    validation = validate_trade_simulation_gate_locked(unsafe)

    checks = {
        "unsafe_gate_rejected": validation.get("certified") is False,
        "trade_simulation_true_detected": unsafe.get("trade_simulation_enabled") is True,
        "trade_simulation_allowed_detected": unsafe.get("trade_simulation_allowed") is True,
        "entry_rules_true_detected": unsafe.get("entry_rules_enabled") is True,
        "exit_rules_true_detected": unsafe.get("exit_rules_enabled") is True,
        "risk_gate_true_detected": unsafe.get("risk_gate_passed") is True,
        "safety_locks_still_false": all(
            v is False for v in SAFETY_LOCKS.values()
        ),
    }

    return {
        "status": "ok" if all(checks.values()) else "failed",
        "checks": checks,
        "certified": all(checks.values()),
        "unsafe_validation": validation,
        "safety_locks": SAFETY_LOCKS.copy(),
    }
''', encoding="utf-8")

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "created_file": str(VALIDATOR),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:

    import py_compile
    py_compile.compile(str(VALIDATOR), doraise=True)

    from backend.app.stacks.strategy_candidate_sandbox.trade_simulation_enablement_gate_contract import (
        build_locked_trade_simulation_gate,
    )

    from backend.app.stacks.strategy_candidate_sandbox.trade_simulation_enablement_gate_validator import (
        validate_trade_simulation_gate_locked,
        validate_unsafe_trade_simulation_gate_is_rejected,
    )

    gate = build_locked_trade_simulation_gate(
        "candidate_31e_stub_001",
        "AAPL",
    )

    locked = validate_trade_simulation_gate_locked(gate)
    rejected = validate_unsafe_trade_simulation_gate_is_rejected(gate)

    result["sample_gate"] = gate
    result["locked_validation"] = locked
    result["unsafe_rejection"] = rejected

    result["checks"]["validator_file_exists"] = VALIDATOR.exists()
    result["checks"]["validator_compiles"] = True
    result["checks"]["locked_validation_certified"] = locked.get("certified") is True
    result["checks"]["unsafe_gate_rejected"] = rejected.get("certified") is True
    result["checks"]["trade_simulation_not_allowed"] = gate.get("trade_simulation_allowed") is False
    result["checks"]["trade_simulation_disabled"] = gate.get("trade_simulation_enabled") is False
    result["checks"]["entry_rules_disabled"] = gate.get("entry_rules_enabled") is False
    result["checks"]["exit_rules_disabled"] = gate.get("exit_rules_enabled") is False
    result["checks"]["broker_execution_disabled"] = gate.get("broker_execution_enabled") is False
    result["checks"]["live_execution_disabled"] = gate.get("live_execution_enabled") is False
    result["checks"]["all_safety_locks_false"] = all(
        v is False for v in gate.get("safety_locks", {}).values()
    )

    result["certified"] = all(result["checks"].values())

except Exception as exc:

    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(
    json.dumps(result, indent=2),
    encoding="utf-8",
)

print(json.dumps(result, indent=2))
print(f"\\nWROTE: {OUT}")

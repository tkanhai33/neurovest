#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX_DIR = ROOT / "backend/app/stacks/strategy_candidate_sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

GATE = SANDBOX_DIR / "risk_gate_contract.py"
OUT_DIR = ROOT / "runtime/strategy_candidate_sandbox"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT = OUT_DIR / "38A_risk_gate_contract_stub_latest.json"

PHASE = "38A_RISK_GATE_CONTRACT_STUB"

GATE.write_text('''from __future__ import annotations

from typing import Any

from backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract import SAFETY_LOCKS


RISK_GATE_KEYS = [
    "gate_id",
    "candidate_id",
    "symbol",
    "risk_gate_required",
    "risk_gate_passed",
    "max_drawdown_limit_pct",
    "max_drawdown_observed_pct",
    "max_trade_count",
    "trade_count_observed",
    "max_position_size_pct",
    "position_size_observed_pct",
    "risk_approval_required",
    "risk_approval_present",
    "trade_simulation_allowed",
    "trade_simulation_enabled",
    "broker_execution_enabled",
    "live_execution_enabled",
]


def build_locked_risk_gate(candidate_id: str, symbol: str) -> dict[str, Any]:
    return {
        "gate_id": "risk_gate_001",
        "candidate_id": candidate_id,
        "symbol": symbol,
        "risk_gate_required": True,
        "risk_gate_passed": False,
        "max_drawdown_limit_pct": 5.0,
        "max_drawdown_observed_pct": None,
        "max_trade_count": 10,
        "trade_count_observed": 0,
        "max_position_size_pct": 2.0,
        "position_size_observed_pct": None,
        "risk_approval_required": True,
        "risk_approval_present": False,
        "trade_simulation_allowed": False,
        "trade_simulation_enabled": False,
        "registry_write_enabled": False,
        "learning_enabled": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
        "safety_locks": SAFETY_LOCKS.copy(),
    }


def validate_locked_risk_gate(gate: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "gate_is_dict": isinstance(gate, dict),
        "all_gate_keys_present": isinstance(gate, dict) and all(k in gate for k in RISK_GATE_KEYS),
        "risk_gate_required": isinstance(gate, dict) and gate.get("risk_gate_required") is True,
        "risk_gate_not_passed": isinstance(gate, dict) and gate.get("risk_gate_passed") is False,
        "risk_approval_absent": isinstance(gate, dict) and gate.get("risk_approval_present") is False,
        "trade_count_zero": isinstance(gate, dict) and gate.get("trade_count_observed") == 0,
        "trade_simulation_not_allowed": isinstance(gate, dict) and gate.get("trade_simulation_allowed") is False,
        "trade_simulation_disabled": isinstance(gate, dict) and gate.get("trade_simulation_enabled") is False,
        "registry_write_disabled": isinstance(gate, dict) and gate.get("registry_write_enabled") is False,
        "learning_disabled": isinstance(gate, dict) and gate.get("learning_enabled") is False,
        "promotion_disabled": isinstance(gate, dict) and gate.get("promotion_enabled") is False,
        "broker_execution_disabled": isinstance(gate, dict) and gate.get("broker_execution_enabled") is False,
        "live_execution_disabled": isinstance(gate, dict) and gate.get("live_execution_enabled") is False,
        "all_safety_locks_false": isinstance(gate, dict) and all(v is False for v in gate.get("safety_locks", {}).values()),
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
    "created_file": str(GATE),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    import py_compile
    py_compile.compile(str(GATE), doraise=True)

    from backend.app.stacks.strategy_candidate_sandbox.risk_gate_contract import (
        RISK_GATE_KEYS,
        build_locked_risk_gate,
        validate_locked_risk_gate,
    )

    gate = build_locked_risk_gate("candidate_31e_stub_001", "AAPL")
    validation = validate_locked_risk_gate(gate)

    result["risk_gate_keys"] = RISK_GATE_KEYS
    result["sample_gate"] = gate
    result["validation"] = validation

    result["checks"]["gate_file_exists"] = GATE.exists()
    result["checks"]["gate_compiles"] = True
    result["checks"]["validation_certified"] = validation.get("certified") is True
    result["checks"]["risk_gate_not_passed"] = gate.get("risk_gate_passed") is False
    result["checks"]["risk_approval_absent"] = gate.get("risk_approval_present") is False
    result["checks"]["trade_simulation_not_allowed"] = gate.get("trade_simulation_allowed") is False
    result["checks"]["trade_simulation_disabled"] = gate.get("trade_simulation_enabled") is False
    result["checks"]["broker_execution_disabled"] = gate.get("broker_execution_enabled") is False
    result["checks"]["live_execution_disabled"] = gate.get("live_execution_enabled") is False
    result["checks"]["all_safety_locks_false"] = all(v is False for v in gate.get("safety_locks", {}).values())

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\\nWROTE: {OUT}")

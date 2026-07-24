#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()

SANDBOX_DIR = ROOT / "backend/app/stacks/strategy_candidate_sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

CONTRACT = SANDBOX_DIR / "entry_exit_signal_contract.py"

OUT_DIR = ROOT / "runtime/strategy_candidate_sandbox"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT = OUT_DIR / "33D_entry_exit_signal_contract_stub_latest.json"
PHASE = "33D_ENTRY_EXIT_SIGNAL_CONTRACT_STUB"

CONTRACT.write_text('''from __future__ import annotations

from typing import Any

from backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract import SAFETY_LOCKS


VALID_SIGNAL_TYPES = {"entry", "exit", "hold"}


SIGNAL_CONTRACT_KEYS = [
    "signal_id",
    "candidate_id",
    "symbol",
    "timestamp",
    "signal_type",
    "confidence",
    "price",
    "reason",
    "source",
    "strategy_logic_enabled",
    "simulation_enabled",
    "trade_event_created",
]


def build_synthetic_hold_signal(candidate_id: str, symbol: str) -> dict[str, Any]:
    return {
        "signal_id": "synthetic_hold_signal_001",
        "candidate_id": candidate_id,
        "symbol": symbol,
        "timestamp": "2024-01-02T00:00:00",
        "signal_type": "hold",
        "confidence": 0.0,
        "price": 0.0,
        "reason": "33D_contract_shape_only_no_strategy_logic",
        "source": "33D_entry_exit_signal_contract_stub",
        "strategy_logic_enabled": False,
        "simulation_enabled": False,
        "trade_event_created": False,
    }


def validate_signal_contract(signal: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "signal_is_dict": isinstance(signal, dict),
        "all_contract_keys_present": isinstance(signal, dict) and all(k in signal for k in SIGNAL_CONTRACT_KEYS),
        "signal_type_valid": isinstance(signal, dict) and signal.get("signal_type") in VALID_SIGNAL_TYPES,
        "confidence_numeric": isinstance(signal, dict) and isinstance(signal.get("confidence"), (int, float)) and not isinstance(signal.get("confidence"), bool),
        "confidence_between_0_and_1": isinstance(signal, dict) and 0 <= signal.get("confidence", -1) <= 1,
        "price_numeric": isinstance(signal, dict) and isinstance(signal.get("price"), (int, float)) and not isinstance(signal.get("price"), bool),
        "strategy_logic_disabled": isinstance(signal, dict) and signal.get("strategy_logic_enabled") is False,
        "simulation_disabled": isinstance(signal, dict) and signal.get("simulation_enabled") is False,
        "trade_event_not_created": isinstance(signal, dict) and signal.get("trade_event_created") is False,
    }

    return {
        "status": "ok" if all(checks.values()) else "failed",
        "checks": checks,
        "certified": all(checks.values()),
        "safety_locks": SAFETY_LOCKS.copy(),
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

    from backend.app.stacks.strategy_candidate_sandbox.entry_exit_signal_contract import (
        SIGNAL_CONTRACT_KEYS,
        build_synthetic_hold_signal,
        validate_signal_contract,
    )

    signal = build_synthetic_hold_signal("candidate_31e_stub_001", "AAPL")
    validation = validate_signal_contract(signal)

    result["signal_contract_keys"] = SIGNAL_CONTRACT_KEYS
    result["sample_signal"] = signal
    result["validation"] = validation

    result["checks"]["contract_file_exists"] = CONTRACT.exists()
    result["checks"]["contract_compiles"] = True
    result["checks"]["signal_type_hold"] = signal.get("signal_type") == "hold"
    result["checks"]["confidence_zero"] = signal.get("confidence") == 0.0
    result["checks"]["strategy_logic_disabled"] = signal.get("strategy_logic_enabled") is False
    result["checks"]["simulation_disabled"] = signal.get("simulation_enabled") is False
    result["checks"]["trade_event_not_created"] = signal.get("trade_event_created") is False
    result["checks"]["validation_certified"] = validation.get("certified") is True
    result["checks"]["all_safety_locks_false"] = all(v is False for v in validation.get("safety_locks", {}).values())

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")

#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX_DIR = ROOT / "backend/app/stacks/strategy_candidate_sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

CONTRACT = SANDBOX_DIR / "exit_signal_rule_contract.py"
OUT_DIR = ROOT / "runtime/strategy_candidate_sandbox"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT = OUT_DIR / "35A_exit_signal_rule_contract_stub_latest.json"

PHASE = "35A_EXIT_SIGNAL_RULE_CONTRACT_STUB"

CONTRACT.write_text('''from __future__ import annotations

from typing import Any

from backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract import SAFETY_LOCKS


EXIT_RULE_CONTRACT_KEYS = [
    "rule_id",
    "candidate_id",
    "symbol",
    "rule_type",
    "enabled",
    "lookback_bars",
    "threshold",
    "confidence_floor",
    "reason",
    "source",
    "strategy_logic_enabled",
    "exit_signal_generation_enabled",
    "trade_event_created",
]


VALID_EXIT_RULE_TYPES = {
    "stop_loss_stub",
    "take_profit_stub",
    "trailing_stop_stub",
    "time_exit_stub",
    "disabled_stub",
}


def build_disabled_exit_rule_contract(candidate_id: str, symbol: str) -> dict[str, Any]:
    return {
        "rule_id": "disabled_exit_rule_001",
        "candidate_id": candidate_id,
        "symbol": symbol,
        "rule_type": "disabled_stub",
        "enabled": False,
        "lookback_bars": 0,
        "threshold": None,
        "confidence_floor": 0.0,
        "reason": "35A_contract_only_no_exit_signal_generation",
        "source": "35A_exit_signal_rule_contract_stub",
        "strategy_logic_enabled": False,
        "exit_signal_generation_enabled": False,
        "trade_event_created": False,
        "safety_locks": SAFETY_LOCKS.copy(),
    }


def validate_exit_rule_contract(rule: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "rule_is_dict": isinstance(rule, dict),
        "all_contract_keys_present": isinstance(rule, dict) and all(k in rule for k in EXIT_RULE_CONTRACT_KEYS),
        "rule_type_valid": isinstance(rule, dict) and rule.get("rule_type") in VALID_EXIT_RULE_TYPES,
        "enabled_false": isinstance(rule, dict) and rule.get("enabled") is False,
        "lookback_bars_zero": isinstance(rule, dict) and rule.get("lookback_bars") == 0,
        "confidence_floor_zero": isinstance(rule, dict) and rule.get("confidence_floor") == 0.0,
        "strategy_logic_disabled": isinstance(rule, dict) and rule.get("strategy_logic_enabled") is False,
        "exit_signal_generation_disabled": isinstance(rule, dict) and rule.get("exit_signal_generation_enabled") is False,
        "trade_event_not_created": isinstance(rule, dict) and rule.get("trade_event_created") is False,
        "all_safety_locks_false": isinstance(rule, dict) and all(v is False for v in rule.get("safety_locks", {}).values()),
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

    from backend.app.stacks.strategy_candidate_sandbox.exit_signal_rule_contract import (
        EXIT_RULE_CONTRACT_KEYS,
        build_disabled_exit_rule_contract,
        validate_exit_rule_contract,
    )

    rule = build_disabled_exit_rule_contract("candidate_31e_stub_001", "AAPL")
    validation = validate_exit_rule_contract(rule)

    result["exit_rule_contract_keys"] = EXIT_RULE_CONTRACT_KEYS
    result["sample_rule"] = rule
    result["validation"] = validation

    result["checks"]["contract_file_exists"] = CONTRACT.exists()
    result["checks"]["contract_compiles"] = True
    result["checks"]["validation_certified"] = validation.get("certified") is True
    result["checks"]["rule_disabled"] = rule.get("enabled") is False
    result["checks"]["strategy_logic_disabled"] = rule.get("strategy_logic_enabled") is False
    result["checks"]["exit_signal_generation_disabled"] = rule.get("exit_signal_generation_enabled") is False
    result["checks"]["trade_event_not_created"] = rule.get("trade_event_created") is False
    result["checks"]["all_safety_locks_false"] = all(v is False for v in rule.get("safety_locks", {}).values())

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")

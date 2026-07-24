#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX_DIR = ROOT / "backend/app/stacks/strategy_candidate_sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

VALIDATOR = SANDBOX_DIR / "entry_signal_rule_validator.py"
OUT_DIR = ROOT / "runtime/strategy_candidate_sandbox"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT = OUT_DIR / "34B_entry_signal_rule_validation_stub_latest.json"

PHASE = "34B_ENTRY_SIGNAL_RULE_VALIDATION_STUB"

VALIDATOR.write_text('''from __future__ import annotations

from typing import Any

from backend.app.stacks.strategy_candidate_sandbox.entry_signal_rule_contract import (
    ENTRY_RULE_CONTRACT_KEYS,
    VALID_ENTRY_RULE_TYPES,
    validate_entry_rule_contract,
)
from backend.app.stacks.strategy_candidate_sandbox.trade_simulation_contract import SAFETY_LOCKS


def validate_disabled_entry_rule(rule: dict[str, Any]) -> dict[str, Any]:
    base = validate_entry_rule_contract(rule)

    checks = {
        "base_contract_certified": base.get("certified") is True,
        "rule_enabled_false": isinstance(rule, dict) and rule.get("enabled") is False,
        "entry_signal_generation_disabled": isinstance(rule, dict) and rule.get("entry_signal_generation_enabled") is False,
        "strategy_logic_disabled": isinstance(rule, dict) and rule.get("strategy_logic_enabled") is False,
        "trade_event_not_created": isinstance(rule, dict) and rule.get("trade_event_created") is False,
        "rule_type_valid": isinstance(rule, dict) and rule.get("rule_type") in VALID_ENTRY_RULE_TYPES,
        "all_keys_present": isinstance(rule, dict) and all(k in rule for k in ENTRY_RULE_CONTRACT_KEYS),
        "all_safety_locks_false": isinstance(rule, dict) and all(v is False for v in rule.get("safety_locks", {}).values()),
    }

    return {
        "status": "ok" if all(checks.values()) else "failed",
        "checks": checks,
        "certified": all(checks.values()),
        "safety_locks": SAFETY_LOCKS.copy(),
    }


def validate_unsafe_enabled_rule_is_rejected(rule: dict[str, Any]) -> dict[str, Any]:
    unsafe = dict(rule)
    unsafe["enabled"] = True
    unsafe["entry_signal_generation_enabled"] = True
    unsafe["strategy_logic_enabled"] = True

    validation = validate_disabled_entry_rule(unsafe)

    checks = {
        "unsafe_rule_rejected": validation.get("certified") is False,
        "enabled_true_detected": unsafe.get("enabled") is True,
        "entry_generation_true_detected": unsafe.get("entry_signal_generation_enabled") is True,
        "strategy_logic_true_detected": unsafe.get("strategy_logic_enabled") is True,
        "safety_locks_still_false": all(v is False for v in SAFETY_LOCKS.values()),
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

    from backend.app.stacks.strategy_candidate_sandbox.entry_signal_rule_contract import build_disabled_entry_rule_contract
    from backend.app.stacks.strategy_candidate_sandbox.entry_signal_rule_validator import (
        validate_disabled_entry_rule,
        validate_unsafe_enabled_rule_is_rejected,
    )

    rule = build_disabled_entry_rule_contract("candidate_31e_stub_001", "AAPL")
    safe_validation = validate_disabled_entry_rule(rule)
    unsafe_rejection = validate_unsafe_enabled_rule_is_rejected(rule)

    result["sample_rule"] = rule
    result["safe_validation"] = safe_validation
    result["unsafe_rejection"] = unsafe_rejection

    result["checks"]["validator_file_exists"] = VALIDATOR.exists()
    result["checks"]["validator_compiles"] = True
    result["checks"]["safe_validation_certified"] = safe_validation.get("certified") is True
    result["checks"]["unsafe_enabled_rule_rejected"] = unsafe_rejection.get("certified") is True
    result["checks"]["rule_enabled_false"] = rule.get("enabled") is False
    result["checks"]["entry_signal_generation_disabled"] = rule.get("entry_signal_generation_enabled") is False
    result["checks"]["strategy_logic_disabled"] = rule.get("strategy_logic_enabled") is False
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

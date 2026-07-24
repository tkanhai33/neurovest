#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "40B_sandbox_runtime_dependency_trace_rollup_certification_latest.json"
PHASE = "40B_SANDBOX_RUNTIME_DEPENDENCY_TRACE_ROLLUP_CERTIFICATION"

TRACE = SANDBOX / "40A_sandbox_runtime_dependency_trace_stub_latest.json"

REQUIRED_TRACE_STEPS = {
    "strategy_proposal_capture",
    "historical_bars_fetch",
    "bar_iterator",
    "bar_only_metrics",
    "candidate_scorecard",
    "manual_promotion_gate",
    "strategy_rule_enablement_gate",
    "risk_gate",
    "trade_simulation_gate",
    "broker_execution",
    "live_execution",
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "trace_source": str(TRACE),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    trace = json.loads(TRACE.read_text(encoding="utf-8")) if TRACE.exists() else {}

    steps = trace.get("trace_steps", [])
    step_names = {
        step.get("name")
        for step in steps
        if isinstance(step, dict)
    }

    locks = trace.get("safety_locks", {})

    result["trace_phase"] = trace.get("phase")
    result["trace_certified"] = trace.get("certified") is True
    result["step_count"] = len(steps)
    result["required_steps_present"] = sorted(REQUIRED_TRACE_STEPS.intersection(step_names))
    result["required_steps_missing"] = sorted(REQUIRED_TRACE_STEPS.difference(step_names))

    result["checks"]["trace_exists"] = TRACE.exists()
    result["checks"]["trace_certified"] = trace.get("certified") is True
    result["checks"]["required_steps_present"] = REQUIRED_TRACE_STEPS.issubset(step_names)
    result["checks"]["all_runtime_disabled"] = all(
        step.get("runtime_enabled") is False
        for step in steps
        if isinstance(step, dict)
    )
    result["checks"]["all_writes_disabled"] = all(
        step.get("writes_enabled") is False
        for step in steps
        if isinstance(step, dict)
    )
    result["checks"]["strategy_gate_locked"] = any(
        step.get("name") == "strategy_rule_enablement_gate"
        and step.get("status") == "locked"
        for step in steps
        if isinstance(step, dict)
    )
    result["checks"]["risk_gate_locked"] = any(
        step.get("name") == "risk_gate"
        and step.get("status") == "locked"
        for step in steps
        if isinstance(step, dict)
    )
    result["checks"]["trade_simulation_gate_locked"] = any(
        step.get("name") == "trade_simulation_gate"
        and step.get("status") == "locked"
        for step in steps
        if isinstance(step, dict)
    )
    result["checks"]["broker_disabled"] = any(
        step.get("name") == "broker_execution"
        and step.get("status") == "disabled"
        for step in steps
        if isinstance(step, dict)
    )
    result["checks"]["live_disabled"] = any(
        step.get("name") == "live_execution"
        and step.get("status") == "disabled"
        for step in steps
        if isinstance(step, dict)
    )
    result["checks"]["all_safety_locks_false"] = all(v is False for v in locks.values())

    result["pipeline_summary"] = {
        "from": "40A_SANDBOX_RUNTIME_DEPENDENCY_TRACE_STUB",
        "to": "40B_SANDBOX_RUNTIME_DEPENDENCY_TRACE_ROLLUP_CERTIFICATION",
        "certified_capability": [
            "runtime dependency trace exists",
            "required trace steps present",
            "strategy/risk/trade simulation gates locked",
            "broker/live endpoints disabled",
            "runtime and writes disabled across trace",
        ],
        "current_behavior": [
            "trace-only architecture inspection",
            "no runtime enablement",
            "no writes",
            "no broker execution",
            "no live execution",
        ],
        "next_recommended_phase": "40C_HANDOFF_BUNDLE_REFRESH",
    }

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\\nWROTE: {OUT}")

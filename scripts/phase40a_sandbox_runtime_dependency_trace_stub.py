#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
OUT = SANDBOX / "40A_sandbox_runtime_dependency_trace_stub_latest.json"

PHASE = "40A_SANDBOX_RUNTIME_DEPENDENCY_TRACE_STUB"

WIREGRAPH = SANDBOX / "39A_master_sandbox_gate_wiregraph_latest.json"

TRACE_STEPS = [
    {
        "step": 1,
        "name": "strategy_proposal_capture",
        "status": "available",
        "runtime_enabled": False,
        "writes_enabled": False,
    },
    {
        "step": 2,
        "name": "historical_bars_fetch",
        "status": "available",
        "runtime_enabled": False,
        "writes_enabled": False,
    },
    {
        "step": 3,
        "name": "bar_iterator",
        "status": "available",
        "runtime_enabled": False,
        "writes_enabled": False,
    },
    {
        "step": 4,
        "name": "bar_only_metrics",
        "status": "available",
        "runtime_enabled": False,
        "writes_enabled": False,
    },
    {
        "step": 5,
        "name": "candidate_scorecard",
        "status": "review_only",
        "runtime_enabled": False,
        "writes_enabled": False,
    },
    {
        "step": 6,
        "name": "manual_promotion_gate",
        "status": "blocked",
        "runtime_enabled": False,
        "writes_enabled": False,
    },
    {
        "step": 7,
        "name": "strategy_rule_enablement_gate",
        "status": "locked",
        "runtime_enabled": False,
        "writes_enabled": False,
    },
    {
        "step": 8,
        "name": "risk_gate",
        "status": "locked",
        "runtime_enabled": False,
        "writes_enabled": False,
    },
    {
        "step": 9,
        "name": "trade_simulation_gate",
        "status": "locked",
        "runtime_enabled": False,
        "writes_enabled": False,
    },
    {
        "step": 10,
        "name": "broker_execution",
        "status": "disabled",
        "runtime_enabled": False,
        "writes_enabled": False,
    },
    {
        "step": 11,
        "name": "live_execution",
        "status": "disabled",
        "runtime_enabled": False,
        "writes_enabled": False,
    },
]

locks = {
    "live_execution_enabled": False,
    "broker_execution_enabled": False,
    "historical_replay_enabled": False,
    "simulation_enabled": False,
    "registry_write_enabled": False,
    "promotion_enabled": False,
    "learning_enabled": False,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "wiregraph_source": str(WIREGRAPH),
    "trace_steps": TRACE_STEPS,
    "safety_locks": locks,
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    graph = json.loads(WIREGRAPH.read_text(encoding="utf-8")) if WIREGRAPH.exists() else {}

    result["wiregraph_phase"] = graph.get("phase")
    result["wiregraph_certified"] = graph.get("certified") is True

    result["checks"]["wiregraph_exists"] = WIREGRAPH.exists()
    result["checks"]["wiregraph_certified"] = graph.get("certified") is True
    result["checks"]["trace_steps_present"] = len(TRACE_STEPS) > 0
    result["checks"]["all_runtime_disabled"] = all(step["runtime_enabled"] is False for step in TRACE_STEPS)
    result["checks"]["all_writes_disabled"] = all(step["writes_enabled"] is False for step in TRACE_STEPS)
    result["checks"]["strategy_gate_locked"] = any(step["name"] == "strategy_rule_enablement_gate" and step["status"] == "locked" for step in TRACE_STEPS)
    result["checks"]["risk_gate_locked"] = any(step["name"] == "risk_gate" and step["status"] == "locked" for step in TRACE_STEPS)
    result["checks"]["trade_simulation_gate_locked"] = any(step["name"] == "trade_simulation_gate" and step["status"] == "locked" for step in TRACE_STEPS)
    result["checks"]["broker_disabled"] = any(step["name"] == "broker_execution" and step["status"] == "disabled" for step in TRACE_STEPS)
    result["checks"]["live_disabled"] = any(step["name"] == "live_execution" and step["status"] == "disabled" for step in TRACE_STEPS)
    result["checks"]["all_safety_locks_false"] = all(v is False for v in locks.values())

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\\nWROTE: {OUT}")

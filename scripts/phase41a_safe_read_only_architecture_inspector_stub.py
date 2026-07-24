#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX_DIR = ROOT / "backend/app/stacks/strategy_candidate_sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

INSPECTOR = SANDBOX_DIR / "safe_read_only_architecture_inspector.py"

OUT_DIR = ROOT / "runtime/strategy_candidate_sandbox"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT = OUT_DIR / "41A_safe_read_only_architecture_inspector_stub_latest.json"

PHASE = "41A_SAFE_READ_ONLY_ARCHITECTURE_INSPECTOR_STUB"

INSPECTOR.write_text('''from __future__ import annotations

from typing import Any


READ_ONLY_LOCKS = {
    "runtime_enabled": False,
    "writes_enabled": False,
    "source_mutation_enabled": False,
    "registry_write_enabled": False,
    "learning_enabled": False,
    "promotion_enabled": False,
    "broker_execution_enabled": False,
    "live_execution_enabled": False,
}


def inspect_architecture_artifacts(
    wiregraph: dict[str, Any],
    runtime_trace: dict[str, Any],
) -> dict[str, Any]:
    graph_nodes = wiregraph.get("nodes", []) if isinstance(wiregraph, dict) else []
    graph_edges = wiregraph.get("edges", []) if isinstance(wiregraph, dict) else []
    trace_steps = runtime_trace.get("trace_steps", []) if isinstance(runtime_trace, dict) else []

    return {
        "status": "read_only_architecture_inspection_complete",
        "inspection_mode": "read_only_no_runtime_no_writes",
        "wiregraph_phase": wiregraph.get("phase") if isinstance(wiregraph, dict) else None,
        "runtime_trace_phase": runtime_trace.get("phase") if isinstance(runtime_trace, dict) else None,
        "wiregraph_certified": wiregraph.get("certified") is True if isinstance(wiregraph, dict) else False,
        "runtime_trace_certified": runtime_trace.get("certified") is True if isinstance(runtime_trace, dict) else False,
        "node_count": len(graph_nodes) if isinstance(graph_nodes, list) else 0,
        "edge_count": len(graph_edges) if isinstance(graph_edges, list) else 0,
        "trace_step_count": len(trace_steps) if isinstance(trace_steps, list) else 0,
        "gate_presence": {
            "strategy_gate": "Strategy Rule Enablement Gate Locked" in graph_nodes,
            "risk_gate": "Risk Gate Locked" in graph_nodes,
            "trade_simulation_gate": "Trade Simulation Enablement Gate Locked" in graph_nodes,
            "broker_disabled": "Broker Execution Disabled" in graph_nodes,
            "live_disabled": "Live Execution Disabled" in graph_nodes,
        },
        "runtime_trace_locks": {
            "all_runtime_disabled": all(
                step.get("runtime_enabled") is False
                for step in trace_steps
                if isinstance(step, dict)
            ),
            "all_writes_disabled": all(
                step.get("writes_enabled") is False
                for step in trace_steps
                if isinstance(step, dict)
            ),
        },
        "read_only_locks": READ_ONLY_LOCKS.copy(),
    }


def validate_architecture_inspection(payload: dict[str, Any]) -> dict[str, Any]:
    gates = payload.get("gate_presence", {}) if isinstance(payload, dict) else {}
    trace_locks = payload.get("runtime_trace_locks", {}) if isinstance(payload, dict) else {}

    checks = {
        "payload_is_dict": isinstance(payload, dict),
        "status_ok": payload.get("status") == "read_only_architecture_inspection_complete",
        "inspection_mode_read_only": payload.get("inspection_mode") == "read_only_no_runtime_no_writes",
        "wiregraph_certified": payload.get("wiregraph_certified") is True,
        "runtime_trace_certified": payload.get("runtime_trace_certified") is True,
        "node_count_gt_zero": payload.get("node_count", 0) > 0,
        "edge_count_gt_zero": payload.get("edge_count", 0) > 0,
        "trace_step_count_gt_zero": payload.get("trace_step_count", 0) > 0,
        "strategy_gate_present": gates.get("strategy_gate") is True,
        "risk_gate_present": gates.get("risk_gate") is True,
        "trade_simulation_gate_present": gates.get("trade_simulation_gate") is True,
        "broker_disabled_present": gates.get("broker_disabled") is True,
        "live_disabled_present": gates.get("live_disabled") is True,
        "all_runtime_disabled": trace_locks.get("all_runtime_disabled") is True,
        "all_writes_disabled": trace_locks.get("all_writes_disabled") is True,
        "all_read_only_locks_false": all(v is False for v in payload.get("read_only_locks", {}).values()),
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
    "created_file": str(INSPECTOR),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    import py_compile
    py_compile.compile(str(INSPECTOR), doraise=True)

    from backend.app.stacks.strategy_candidate_sandbox.safe_read_only_architecture_inspector import (
        inspect_architecture_artifacts,
        validate_architecture_inspection,
    )

    wiregraph_path = OUT_DIR / "39A_master_sandbox_gate_wiregraph_latest.json"
    trace_path = OUT_DIR / "40A_sandbox_runtime_dependency_trace_stub_latest.json"

    wiregraph = json.loads(wiregraph_path.read_text(encoding="utf-8"))
    runtime_trace = json.loads(trace_path.read_text(encoding="utf-8"))

    inspection = inspect_architecture_artifacts(wiregraph, runtime_trace)
    validation = validate_architecture_inspection(inspection)

    result["inspection"] = inspection
    result["validation"] = validation

    result["checks"]["inspector_file_exists"] = INSPECTOR.exists()
    result["checks"]["inspector_compiles"] = True
    result["checks"]["wiregraph_source_exists"] = wiregraph_path.exists()
    result["checks"]["runtime_trace_source_exists"] = trace_path.exists()
    result["checks"]["validation_certified"] = validation.get("certified") is True
    result["checks"]["inspection_read_only"] = inspection.get("inspection_mode") == "read_only_no_runtime_no_writes"
    result["checks"]["all_read_only_locks_false"] = all(v is False for v in inspection.get("read_only_locks", {}).values())

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\\nWROTE: {OUT}")

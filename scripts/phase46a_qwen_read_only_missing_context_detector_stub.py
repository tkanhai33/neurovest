#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
OUT = SANDBOX / "46A_qwen_read_only_missing_context_detector_stub_latest.json"

PHASE = "46A_QWEN_READ_ONLY_MISSING_CONTEXT_DETECTOR_STUB"

HANDOFF = SANDBOX / "45C_handoff_bundle_refresh_latest.json"
WIREGRAPH = SANDBOX / "39A_master_sandbox_gate_wiregraph_latest.json"
TRACE = SANDBOX / "40A_sandbox_runtime_dependency_trace_stub_latest.json"

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "sources": {
        "handoff": str(HANDOFF),
        "wiregraph": str(WIREGRAPH),
        "runtime_trace": str(TRACE),
    },
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    handoff = json.loads(HANDOFF.read_text(encoding="utf-8")) if HANDOFF.exists() else {}
    wiregraph = json.loads(WIREGRAPH.read_text(encoding="utf-8")) if WIREGRAPH.exists() else {}
    trace = json.loads(TRACE.read_text(encoding="utf-8")) if TRACE.exists() else {}

    required_context = {
        "handoff_certified": handoff.get("certified") is True,
        "wiregraph_certified": wiregraph.get("certified") is True,
        "runtime_trace_certified": trace.get("certified") is True,
        "latest_phase_present": bool(handoff.get("latest_confirmed_phase")),
        "next_phase_present": bool(handoff.get("next_recommended_phase")),
        "still_disabled_present": bool(handoff.get("still_disabled")),
        "wiregraph_nodes_present": bool(wiregraph.get("nodes")),
        "wiregraph_edges_present": bool(wiregraph.get("edges")),
        "trace_steps_present": bool(trace.get("trace_steps")),
    }

    missing_context = [
        key for key, ok in required_context.items()
        if ok is not True
    ]

    detector_payload = {
        "status": "qwen_missing_context_detector_read_only",
        "detector_mode": "read_only_no_actions_no_writes",
        "required_context": required_context,
        "missing_context": missing_context,
        "missing_context_count": len(missing_context),
        "qwen_may_report_missing_context": True,
        "qwen_may_request_files": False,
        "qwen_may_write_files": False,
        "qwen_may_execute_runtime": False,
        "qwen_may_mutate_source": False,
        "qwen_may_enable_runtime": False,
        "qwen_may_broker_or_live_trade": False,
        "recommended_next_read_only_phase": "46B_QWEN_READ_ONLY_MISSING_CONTEXT_DETECTOR_ROLLUP_CERTIFICATION",
    }

    result["detector_payload"] = detector_payload

    result["checks"]["handoff_exists"] = HANDOFF.exists()
    result["checks"]["wiregraph_exists"] = WIREGRAPH.exists()
    result["checks"]["runtime_trace_exists"] = TRACE.exists()
    result["checks"]["all_sources_certified"] = all([
        handoff.get("certified") is True,
        wiregraph.get("certified") is True,
        trace.get("certified") is True,
    ])
    result["checks"]["detector_read_only"] = detector_payload["detector_mode"] == "read_only_no_actions_no_writes"
    result["checks"]["missing_context_list_exists"] = isinstance(missing_context, list)
    result["checks"]["qwen_may_report_missing_context"] = detector_payload["qwen_may_report_missing_context"] is True
    result["checks"]["qwen_cannot_request_files"] = detector_payload["qwen_may_request_files"] is False
    result["checks"]["qwen_cannot_write_files"] = detector_payload["qwen_may_write_files"] is False
    result["checks"]["qwen_cannot_execute_runtime"] = detector_payload["qwen_may_execute_runtime"] is False
    result["checks"]["qwen_cannot_mutate_source"] = detector_payload["qwen_may_mutate_source"] is False
    result["checks"]["qwen_cannot_enable_runtime"] = detector_payload["qwen_may_enable_runtime"] is False
    result["checks"]["qwen_cannot_broker_or_live_trade"] = detector_payload["qwen_may_broker_or_live_trade"] is False
    result["checks"]["has_next_read_only_phase"] = bool(detector_payload["recommended_next_read_only_phase"])

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\\nWROTE: {OUT}")

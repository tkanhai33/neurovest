#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "42B_qwen_read_only_architecture_context_rollup_certification_latest.json"
PHASE = "42B_QWEN_READ_ONLY_ARCHITECTURE_CONTEXT_ROLLUP_CERTIFICATION"

ARTIFACT = SANDBOX / "42A_qwen_read_only_architecture_context_stub_latest.json"

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "artifact": str(ARTIFACT),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8")) if ARTIFACT.exists() else {}
    context = data.get("context", {}) if isinstance(data.get("context"), dict) else {}
    validation = data.get("validation", {}) if isinstance(data.get("validation"), dict) else {}
    locks = context.get("qwen_context_locks", {}) if isinstance(context.get("qwen_context_locks"), dict) else {}

    result["source_phase"] = data.get("phase")
    result["source_certified"] = data.get("certified") is True
    result["context_summary"] = {
        "status": context.get("status"),
        "context_mode": context.get("context_mode"),
        "handoff_phase": context.get("handoff_phase"),
        "inspection_phase": context.get("inspection_phase"),
        "stage": context.get("stage"),
        "latest_confirmed_phase": context.get("latest_confirmed_phase"),
        "allowed_outputs": context.get("qwen_allowed_outputs", []),
        "forbidden_outputs": context.get("qwen_forbidden_outputs", []),
    }

    result["checks"]["artifact_exists"] = ARTIFACT.exists()
    result["checks"]["source_certified"] = data.get("certified") is True
    result["checks"]["validation_certified"] = validation.get("certified") is True
    result["checks"]["context_status_ok"] = context.get("status") == "qwen_read_only_architecture_context_ready"
    result["checks"]["context_mode_read_only"] = context.get("context_mode") == "read_only_architecture_context_no_actions"
    result["checks"]["handoff_certified"] = context.get("handoff_certified") is True
    result["checks"]["inspection_certified"] = context.get("inspection_certified") is True

    result["checks"]["qwen_can_read_architecture"] = locks.get("qwen_can_read_architecture") is True
    result["checks"]["qwen_cannot_write_files"] = locks.get("qwen_can_write_files") is False
    result["checks"]["qwen_cannot_execute_runtime"] = locks.get("qwen_can_execute_runtime") is False
    result["checks"]["qwen_cannot_mutate_source"] = locks.get("qwen_can_mutate_source") is False
    result["checks"]["qwen_cannot_enable_strategy_rules"] = locks.get("qwen_can_enable_strategy_rules") is False
    result["checks"]["qwen_cannot_enable_trade_simulation"] = locks.get("qwen_can_enable_trade_simulation") is False
    result["checks"]["qwen_cannot_enable_learning"] = locks.get("qwen_can_enable_learning") is False
    result["checks"]["qwen_cannot_enable_promotion"] = locks.get("qwen_can_enable_promotion") is False
    result["checks"]["qwen_cannot_place_broker_orders"] = locks.get("qwen_can_place_broker_orders") is False
    result["checks"]["qwen_cannot_live_trade"] = locks.get("qwen_can_live_trade") is False

    result["pipeline_summary"] = {
        "from": "42A_QWEN_READ_ONLY_ARCHITECTURE_CONTEXT_STUB",
        "to": "42B_QWEN_READ_ONLY_ARCHITECTURE_CONTEXT_ROLLUP_CERTIFICATION",
        "certified_capability": [
            "Qwen read-only architecture context exists",
            "Qwen can read certified architecture context",
            "Qwen cannot write files",
            "Qwen cannot execute runtime",
            "Qwen cannot mutate source",
            "Qwen cannot enable strategy rules or simulation",
            "Qwen cannot broker trade or live trade",
        ],
        "current_behavior": [
            "Qwen may summarize architecture",
            "Qwen may explain locked gates",
            "Qwen may identify missing context",
            "Qwen may recommend read-only next phase",
            "Qwen cannot perform actions",
        ],
        "next_recommended_phase": "42C_HANDOFF_BUNDLE_REFRESH",
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

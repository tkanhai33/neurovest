#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "46B_qwen_read_only_missing_context_detector_rollup_certification_latest.json"
PHASE = "46B_QWEN_READ_ONLY_MISSING_CONTEXT_DETECTOR_ROLLUP_CERTIFICATION"

ARTIFACT = SANDBOX / "46A_qwen_read_only_missing_context_detector_stub_latest.json"

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
    detector = data.get("detector_payload", {}) if isinstance(data.get("detector_payload"), dict) else {}

    result["source_phase"] = data.get("phase")
    result["source_certified"] = data.get("certified") is True
    result["detector_summary"] = {
        "status": detector.get("status"),
        "detector_mode": detector.get("detector_mode"),
        "missing_context": detector.get("missing_context", []),
        "missing_context_count": detector.get("missing_context_count"),
        "recommended_next_read_only_phase": detector.get("recommended_next_read_only_phase"),
    }

    result["checks"]["artifact_exists"] = ARTIFACT.exists()
    result["checks"]["source_certified"] = data.get("certified") is True
    result["checks"]["status_ok"] = detector.get("status") == "qwen_missing_context_detector_read_only"
    result["checks"]["detector_read_only"] = detector.get("detector_mode") == "read_only_no_actions_no_writes"
    result["checks"]["missing_context_is_list"] = isinstance(detector.get("missing_context"), list)
    result["checks"]["missing_context_count_matches"] = detector.get("missing_context_count") == len(detector.get("missing_context", []))
    result["checks"]["no_missing_context"] = detector.get("missing_context_count") == 0
    result["checks"]["qwen_may_report_missing_context"] = detector.get("qwen_may_report_missing_context") is True
    result["checks"]["qwen_cannot_request_files"] = detector.get("qwen_may_request_files") is False
    result["checks"]["qwen_cannot_write_files"] = detector.get("qwen_may_write_files") is False
    result["checks"]["qwen_cannot_execute_runtime"] = detector.get("qwen_may_execute_runtime") is False
    result["checks"]["qwen_cannot_mutate_source"] = detector.get("qwen_may_mutate_source") is False
    result["checks"]["qwen_cannot_enable_runtime"] = detector.get("qwen_may_enable_runtime") is False
    result["checks"]["qwen_cannot_broker_or_live_trade"] = detector.get("qwen_may_broker_or_live_trade") is False
    result["checks"]["has_next_read_only_phase"] = bool(detector.get("recommended_next_read_only_phase"))

    result["pipeline_summary"] = {
        "from": "46A_QWEN_READ_ONLY_MISSING_CONTEXT_DETECTOR_STUB",
        "to": "46B_QWEN_READ_ONLY_MISSING_CONTEXT_DETECTOR_ROLLUP_CERTIFICATION",
        "certified_capability": [
            "Qwen missing-context detector exists",
            "detector is read-only",
            "missing context list is valid",
            "no missing context currently detected",
            "Qwen may report missing context only",
            "Qwen cannot request files, write, execute, mutate source, or trade",
        ],
        "current_behavior": [
            "read-only missing-context inspection only",
            "no actions",
            "no writes",
            "no runtime",
            "no source mutation",
            "no broker/live execution",
        ],
        "next_recommended_phase": "46C_HANDOFF_BUNDLE_REFRESH",
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

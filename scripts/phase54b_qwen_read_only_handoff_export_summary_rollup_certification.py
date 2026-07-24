#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "54B_qwen_read_only_handoff_export_summary_rollup_certification_latest.json"

PHASE = "54B_QWEN_READ_ONLY_HANDOFF_EXPORT_SUMMARY_ROLLUP_CERTIFICATION"

ARTIFACT = SANDBOX / "54A_qwen_read_only_handoff_export_summary_stub_latest.json"

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "artifact": str(ARTIFACT),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    data = (
        json.loads(ARTIFACT.read_text(encoding="utf-8"))
        if ARTIFACT.exists()
        else {}
    )

    summary = (
        data.get("export_summary_payload", {})
        if isinstance(data.get("export_summary_payload"), dict)
        else {}
    )

    snapshot = (
        summary.get("export_snapshot", {})
        if isinstance(summary.get("export_snapshot"), dict)
        else {}
    )

    result["source_phase"] = data.get("phase")
    result["source_certified"] = data.get("certified") is True

    result["export_summary"] = {
        "status": summary.get("status"),
        "export_mode": summary.get("export_mode"),
        "stage": snapshot.get("stage"),
        "latest_confirmed_phase": snapshot.get(
            "latest_confirmed_phase"
        ),
        "allowed_export_sections": summary.get(
            "allowed_export_sections",
            [],
        ),
        "forbidden_export_actions": summary.get(
            "forbidden_export_actions",
            [],
        ),
        "recommended_next_read_only_phase": summary.get(
            "recommended_next_read_only_phase"
        ),
    }

    result["checks"]["artifact_exists"] = ARTIFACT.exists()

    result["checks"]["source_certified"] = (
        data.get("certified") is True
    )

    result["checks"]["status_ok"] = (
        summary.get("status")
        == "qwen_read_only_handoff_export_summary_ready"
    )

    result["checks"]["export_mode_read_only"] = (
        summary.get("export_mode")
        == "read_only_summary_export_only"
    )

    result["checks"]["handoff_certified"] = (
        summary.get("handoff_certified") is True
    )

    result["checks"]["snapshot_present"] = (
        len(snapshot) > 0
    )

    result["checks"]["export_read_allowed"] = (
        summary.get("export_read_allowed") is True
    )

    result["checks"]["export_write_blocked"] = (
        summary.get("export_write_allowed") is False
    )

    result["checks"]["allowed_sections_present"] = (
        len(summary.get("allowed_export_sections", [])) > 0
    )

    result["checks"]["forbidden_actions_present"] = (
        len(summary.get("forbidden_export_actions", [])) > 0
    )

    result["checks"]["actions_not_allowed"] = (
        summary.get("actions_allowed") is False
    )

    result["checks"]["writes_not_allowed"] = (
        summary.get("writes_allowed") is False
    )

    result["checks"]["runtime_not_allowed"] = (
        summary.get("runtime_allowed") is False
    )

    result["checks"]["shell_execution_not_allowed"] = (
        summary.get("shell_execution_allowed") is False
    )

    result["checks"]["source_mutation_not_allowed"] = (
        summary.get("source_mutation_allowed") is False
    )

    result["checks"]["broker_or_live_not_allowed"] = (
        summary.get("broker_or_live_allowed") is False
    )

    result["checks"]["recursive_execution_not_allowed"] = (
        summary.get("recursive_execution_allowed") is False
    )

    result["checks"]["autonomous_phase_execution_not_allowed"] = (
        summary.get("autonomous_phase_execution_allowed") is False
    )

    result["checks"]["critical_safety_locks_false"] = all(
        value is False
        for value in snapshot.get(
            "critical_safety_locks",
            {},
        ).values()
    )

    result["checks"]["has_next_read_only_phase"] = bool(
        summary.get("recommended_next_read_only_phase")
    )

    result["pipeline_summary"] = {
        "from":
            "54A_QWEN_READ_ONLY_HANDOFF_EXPORT_SUMMARY_STUB",

        "to":
            "54B_QWEN_READ_ONLY_HANDOFF_EXPORT_SUMMARY_ROLLUP_CERTIFICATION",

        "certified_capability": [
            "Qwen read-only handoff export exists",
            "export snapshot remains controlled",
            "export sections are defined",
            "forbidden export actions remain blocked",
            "read-only export boundary preserved",
            "critical safety locks remain false",
        ],

        "current_behavior": [
            "Qwen may export read-only architecture summaries",
            "Qwen may export certified capability state",
            "Qwen may export disabled capability state",
            "Qwen may export safety lock state",
            "Qwen may not export mutation or execution paths",
        ],

        "next_recommended_phase":
            "54C_HANDOFF_BUNDLE_REFRESH",
    }

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })


OUT.write_text(
    json.dumps(result, indent=2),
    encoding="utf-8",
)

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")

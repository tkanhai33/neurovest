#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "research_repository_row_exclusion_policy/118F_research_repository_row_exclusion_policy_latest.json"
FULL_EXPORT = ARCH / "research_repository_full_anomaly_export/118C_research_repository_full_anomaly_export_latest.json"

OUT_DIR = ARCH / "research_repository_warning_policy"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "118G_research_repository_warning_policy_latest.json"
OUT_TXT = OUT_DIR / "118G_research_repository_warning_policy_latest.txt"

PHASE = "118G_RESEARCH_REPOSITORY_WARNING_POLICY"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source = read_json(SOURCE)
export = read_json(FULL_EXPORT)
reason_counts = export.get("reason_counts", {})

warning_count = reason_counts.get("close_outside_high_low_range", 0)
review_count = reason_counts.get("daily_return_out_of_bounds", 0)

warning_policy = {
    "policy_id": "RESEARCH_REPOSITORY_WARNING_POLICY_V1",
    "mode": "WARNING_POLICY_ONLY_NO_DATA_MODIFICATION",
    "warnings": {
        "close_outside_high_low_range": {
            "count": warning_count,
            "severity": "WARNING",
            "likely_cause": "adjusted/unadjusted OHLC provider semantics",
            "training_action": "ALLOW_WITH_COLUMN_SEMANTICS_TAG",
            "exclude_from_training": False,
            "requires_source_csv_modification": False,
        },
        "daily_return_out_of_bounds": {
            "count": review_count,
            "severity": "REVIEW",
            "training_action": "ALLOW_ONLY_AFTER_REPLAY_BOUNDARY_AND_CORPORATE_ACTION_GUARD",
            "exclude_from_training": False,
            "requires_source_csv_modification": False,
        },
    },
    "global_policy": {
        "source_csv_modification_allowed": False,
        "row_deletion_allowed": False,
        "approved_for_training": False,
        "database_writes_allowed": False,
        "training_execution_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "full_export_exists": FULL_EXPORT.exists(),
    "warning_count_4799": warning_count == 4799,
    "review_count_1": review_count == 1,
    "warning_policy_present": bool(warning_policy),
    "warnings_do_not_delete_rows": all(
        item["requires_source_csv_modification"] is False
        for item in warning_policy["warnings"].values()
    ),
    "approved_for_training_false": warning_policy["global_policy"]["approved_for_training"] is False,
    "db_write_blocked": warning_policy["global_policy"]["database_writes_allowed"] is False,
    "training_blocked": warning_policy["global_policy"]["training_execution_enabled"] is False,
    "broker_live_blocked": (
        warning_policy["global_policy"]["broker_execution_enabled"] is False
        and warning_policy["global_policy"]["live_execution_enabled"] is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "warning_policy": warning_policy,
    "checks": checks,
    "recommended_next_phase": "118H_RESEARCH_REPOSITORY_TRAINING_APPROVAL_PREVIEW",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"warning_count: {warning_count}",
        f"review_count: {review_count}",
        "source_csv_modification_allowed: False",
        "approved_for_training: False",
        "",
        "Warning policy created.",
        "Warnings are allowed with semantics tags, not deleted.",
        "No DB writes. No training. No broker/live.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "warning_count": warning_count,
    "review_count": review_count,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

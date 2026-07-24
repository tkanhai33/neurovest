#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "research_repository_full_anomaly_export/118C_research_repository_full_anomaly_export_latest.json"

OUT_DIR = ARCH / "research_repository_anomaly_classification_policy"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "118D_research_repository_anomaly_classification_policy_latest.json"
OUT_TXT = OUT_DIR / "118D_research_repository_anomaly_classification_policy_latest.txt"

PHASE = "118D_RESEARCH_REPOSITORY_ANOMALY_CLASSIFICATION_POLICY"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source = read_json(SOURCE)
reason_counts = source.get("reason_counts", {})

classification_policy = {
    "policy_id": "RESEARCH_REPOSITORY_ANOMALY_CLASSIFICATION_POLICY_V1",
    "mode": "CLASSIFICATION_ONLY_NO_DATA_MODIFICATION",
    "rules": {
        "close_outside_high_low_range": {
            "severity": "WARNING",
            "likely_cause": "adjusted/unadjusted OHLC mismatch or asset-class-specific provider semantics",
            "training_action": "ALLOW_AFTER_COLUMN_SEMANTICS_POLICY",
            "requires_row_deletion": False,
            "requires_provider_retry": False,
        },
        "price_out_of_bounds": {
            "severity": "BLOCKER",
            "likely_cause": "zero/invalid price from provider",
            "training_action": "EXCLUDE_ROW_UNTIL_FIXED",
            "requires_row_deletion": False,
            "requires_provider_retry": True,
        },
        "not_finite_number": {
            "severity": "BLOCKER",
            "likely_cause": "NaN/infinite/missing numeric field",
            "training_action": "EXCLUDE_ROW_UNTIL_FIXED",
            "requires_row_deletion": False,
            "requires_provider_retry": True,
        },
        "low_greater_than_high": {
            "severity": "BLOCKER",
            "likely_cause": "corrupt OHLC row",
            "training_action": "EXCLUDE_ROW_UNTIL_FIXED",
            "requires_row_deletion": False,
            "requires_provider_retry": True,
        },
        "daily_return_out_of_bounds": {
            "severity": "REVIEW",
            "likely_cause": "corporate action, provider discontinuity, or asset-specific behavior",
            "training_action": "ROUTE_TO_CORPORATE_ACTION_OR_RETURN_POLICY",
            "requires_row_deletion": False,
            "requires_provider_retry": False,
        },
    },
    "global_policy": {
        "data_modification_allowed": False,
        "row_deletion_allowed": False,
        "normalization_executed": False,
        "approved_for_training": False,
        "database_writes_allowed": False,
        "training_execution_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
}

blocker_count = (
    reason_counts.get("price_out_of_bounds", 0)
    + reason_counts.get("not_finite_number", 0)
    + reason_counts.get("low_greater_than_high", 0)
)

warning_count = reason_counts.get("close_outside_high_low_range", 0)
review_count = reason_counts.get("daily_return_out_of_bounds", 0)

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "policy_id_present": bool(classification_policy["policy_id"]),
    "reason_counts_present": bool(reason_counts),
    "all_known_reasons_classified": all(
        reason in classification_policy["rules"]
        for reason in reason_counts.keys()
    ),
    "blockers_identified": blocker_count == 6,
    "warnings_identified": warning_count == 4799,
    "review_items_identified": review_count == 1,
    "data_modification_blocked": classification_policy["global_policy"]["data_modification_allowed"] is False,
    "approved_for_training_false": classification_policy["global_policy"]["approved_for_training"] is False,
    "db_write_blocked": classification_policy["global_policy"]["database_writes_allowed"] is False,
    "training_blocked": classification_policy["global_policy"]["training_execution_enabled"] is False,
    "broker_live_blocked": (
        classification_policy["global_policy"]["broker_execution_enabled"] is False
        and classification_policy["global_policy"]["live_execution_enabled"] is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "source_full_export": str(SOURCE),
    "reason_counts": reason_counts,
    "classification_summary": {
        "warning_count": warning_count,
        "review_count": review_count,
        "blocker_count": blocker_count,
        "training_approval_blocked": True,
    },
    "classification_policy": classification_policy,
    "checks": checks,
    "recommended_next_phase": "118E_RESEARCH_REPOSITORY_BLOCKER_ROW_INSPECTION",
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
        f"blocker_count: {blocker_count}",
        "approved_for_training: False",
        "",
        "Anomaly classification policy created.",
        "Warnings do not automatically block repository use.",
        "Blocker rows must be inspected before training approval.",
        "No data modification. No DB writes. No broker/live.",
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
    "blocker_count": blocker_count,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

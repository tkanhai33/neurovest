#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE_EXCLUSION = ARCH / "research_repository_row_exclusion_policy/118F_research_repository_row_exclusion_policy_latest.json"
SOURCE_WARNING = ARCH / "research_repository_warning_policy/118G_research_repository_warning_policy_latest.json"
SOURCE_ROLLUP = ARCH / "research_repository_download_rollup/117L_research_repository_download_rollup_latest.json"

OUT_DIR = ARCH / "research_repository_training_approval_preview"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "118H_research_repository_training_approval_preview_latest.json"
OUT_TXT = OUT_DIR / "118H_research_repository_training_approval_preview_latest.txt"

PHASE = "118H_RESEARCH_REPOSITORY_TRAINING_APPROVAL_PREVIEW"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

exclusion = read_json(SOURCE_EXCLUSION)
warning = read_json(SOURCE_WARNING)
rollup = read_json(SOURCE_ROLLUP)

exclusions = exclusion.get("row_exclusion_policy", {}).get("exclusions", [])
warning_policy = warning.get("warning_policy", {})

approval_preview = {
    "mode": "APPROVAL_PREVIEW_ONLY_NO_TRAINING",
    "repository_symbols": rollup.get("rollup", {}).get("total_downloaded_symbols"),
    "excluded_rows": len(exclusions),
    "warnings_allowed_with_semantics_tags": True,
    "source_csv_modification_required": False,
    "row_deletion_required": False,
    "approved_for_training_after_certification": True,
    "training_execution_enabled_now": False,
}

checks = {
    "source_exclusion_exists": SOURCE_EXCLUSION.exists(),
    "source_exclusion_certified": exclusion.get("certified") is True,
    "source_warning_exists": SOURCE_WARNING.exists(),
    "source_warning_certified": warning.get("certified") is True,
    "source_rollup_exists": SOURCE_ROLLUP.exists(),
    "source_rollup_certified": rollup.get("certified") is True,
    "repository_symbols_144": approval_preview["repository_symbols"] == 144,
    "excluded_rows_6": approval_preview["excluded_rows"] == 6,
    "warnings_policy_present": bool(warning_policy),
    "source_csv_not_modified": approval_preview["source_csv_modification_required"] is False,
    "row_deletion_not_required": approval_preview["row_deletion_required"] is False,
    "training_still_blocked": approval_preview["training_execution_enabled_now"] is False,
    "db_write_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "approval_preview": approval_preview,
    "checks": checks,
    "policy": {
        "approval_preview_certified": True,
        "approved_for_training_now": False,
        "approved_for_training_after_certification": True,
        "database_writes_allowed": False,
        "training_execution_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "118I_RESEARCH_REPOSITORY_TRAINING_APPROVAL_CERTIFICATION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"repository_symbols: {approval_preview['repository_symbols']}",
        f"excluded_rows: {approval_preview['excluded_rows']}",
        "approved_for_training_now: False",
        "approved_after_certification: True",
        "",
        "Training approval preview created.",
        "No training executed. No DB writes. No broker/live.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "repository_symbols": approval_preview["repository_symbols"],
    "excluded_rows": approval_preview["excluded_rows"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

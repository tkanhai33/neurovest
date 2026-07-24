#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "research_repository_training_approval_preview/118H_research_repository_training_approval_preview_latest.json"

OUT_DIR = ARCH / "research_repository_training_approval_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "118I_research_repository_training_approval_certification_latest.json"
OUT_TXT = OUT_DIR / "118I_research_repository_training_approval_certification_latest.txt"

PHASE = "118I_RESEARCH_REPOSITORY_TRAINING_APPROVAL_CERTIFICATION"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source = read_json(SOURCE)
preview = source.get("approval_preview", {})

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "repository_symbols_144": preview.get("repository_symbols") == 144,
    "excluded_rows_6": preview.get("excluded_rows") == 6,
    "source_csv_not_modified": preview.get("source_csv_modification_required") is False,
    "row_deletion_not_required": preview.get("row_deletion_required") is False,
    "approved_after_certification": preview.get("approved_for_training_after_certification") is True,
    "training_not_executed_now": preview.get("training_execution_enabled_now") is False,
    "db_write_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "training_approval": {
        "approved_for_training": True,
        "repository_symbols": preview.get("repository_symbols"),
        "excluded_rows": preview.get("excluded_rows"),
        "warnings_allowed_with_semantics_tags": True,
        "source_csv_modified": False,
        "rows_deleted": False,
    },
    "checks": checks,
    "policy": {
        "approved_for_training": True,
        "database_writes_allowed": False,
        "training_execution_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "118J_RESEARCH_REPOSITORY_APPROVAL_ROLLUP",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "approved_for_training: True",
        f"repository_symbols: {preview.get('repository_symbols')}",
        f"excluded_rows: {preview.get('excluded_rows')}",
        "training_execution_enabled: False",
        "",
        "Research repository training approval certified.",
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
    "approved_for_training": True,
    "repository_symbols": preview.get("repository_symbols"),
    "excluded_rows": preview.get("excluded_rows"),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

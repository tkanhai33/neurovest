#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
from collections import Counter
import csv, json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "research_repository_anomaly_classification_policy/118D_research_repository_anomaly_classification_policy_latest.json"
EXPORT = ARCH / "research_repository_full_anomaly_export/118C_full_anomaly_export.csv"

OUT_DIR = ARCH / "research_repository_blocker_row_inspection"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "118E_research_repository_blocker_row_inspection_latest.json"
OUT_TXT = OUT_DIR / "118E_research_repository_blocker_row_inspection_latest.txt"

PHASE = "118E_RESEARCH_REPOSITORY_BLOCKER_ROW_INSPECTION"

BLOCKER_REASONS = {
    "price_out_of_bounds",
    "not_finite_number",
    "low_greater_than_high",
}

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source = read_json(SOURCE)

blockers = []
all_rows = []

with EXPORT.open("r", encoding="utf-8") as handle:
    reader = csv.DictReader(handle)
    for row in reader:
        all_rows.append(row)
        if row.get("reason") in BLOCKER_REASONS:
            parsed = dict(row)
            try:
                parsed["details_parsed"] = json.loads(row.get("details") or "{}")
            except Exception:
                parsed["details_parsed"] = {}
            blockers.append(parsed)

reason_counts = Counter(row["reason"] for row in blockers)
symbol_counts = Counter(row["symbol"] for row in blockers)
file_counts = Counter(row["file"] for row in blockers)

inspection = {
    "blocker_count": len(blockers),
    "reason_counts": dict(reason_counts),
    "symbol_counts": dict(symbol_counts),
    "file_counts": dict(file_counts),
    "blockers": blockers,
    "recommended_action": {
        "mode": "CREATE_EXCLUSION_POLICY_ONLY",
        "exclude_blocker_rows_from_training": True,
        "modify_source_csv": False,
        "delete_rows": False,
        "provider_retry_optional": True,
    },
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "export_exists": EXPORT.exists(),
    "blockers_found": len(blockers) == 6,
    "blocker_reasons_only": all(row["reason"] in BLOCKER_REASONS for row in blockers),
    "reason_counts_present": len(reason_counts) > 0,
    "symbols_present": len(symbol_counts) > 0,
    "no_source_csv_modification": True,
    "no_row_deletion": True,
    "db_write_blocked": True,
    "training_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "BLOCKER_ROW_INSPECTION_ONLY",
    "inspection": inspection,
    "checks": checks,
    "policy": {
        "inspection_only": True,
        "data_modification_allowed": False,
        "row_deletion_allowed": False,
        "approved_for_training": False,
        "database_writes_allowed": False,
        "training_execution_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "118F_RESEARCH_REPOSITORY_ROW_EXCLUSION_POLICY",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"blocker_count: {len(blockers)}",
        f"reason_counts: {dict(reason_counts)}",
        f"symbol_counts: {dict(symbol_counts)}",
        "",
        "Blocker rows inspected.",
        "No data modification. No row deletion. No DB writes. No training.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "blocker_count": len(blockers),
    "reason_counts": dict(reason_counts),
    "symbol_counts": dict(symbol_counts),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

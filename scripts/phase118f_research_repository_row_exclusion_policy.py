#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "research_repository_blocker_row_inspection/118E_research_repository_blocker_row_inspection_latest.json"

OUT_DIR = ARCH / "research_repository_row_exclusion_policy"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "118F_research_repository_row_exclusion_policy_latest.json"
OUT_TXT = OUT_DIR / "118F_research_repository_row_exclusion_policy_latest.txt"

PHASE = "118F_RESEARCH_REPOSITORY_ROW_EXCLUSION_POLICY"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source = read_json(SOURCE)
blockers = source.get("inspection", {}).get("blockers", [])

exclusions = []
for b in blockers:
    exclusions.append({
        "file": b.get("file"),
        "line": b.get("line"),
        "asset_group": b.get("asset_group"),
        "symbol": b.get("symbol"),
        "date": b.get("date"),
        "reason": b.get("reason"),
        "exclude_from_training": True,
        "modify_source_csv": False,
        "delete_row": False,
    })

policy = {
    "policy_id": "RESEARCH_REPOSITORY_ROW_EXCLUSION_POLICY_V1",
    "mode": "EXCLUSION_POLICY_ONLY_NO_DATA_MODIFICATION",
    "exclusion_count": len(exclusions),
    "exclusions": exclusions,
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
    "exclusion_count_6": len(exclusions) == 6,
    "all_excluded_from_training": all(e["exclude_from_training"] is True for e in exclusions),
    "no_source_csv_modification": all(e["modify_source_csv"] is False for e in exclusions),
    "no_row_deletion": all(e["delete_row"] is False for e in exclusions),
    "approved_for_training_false": policy["global_policy"]["approved_for_training"] is False,
    "db_write_blocked": policy["global_policy"]["database_writes_allowed"] is False,
    "training_blocked": policy["global_policy"]["training_execution_enabled"] is False,
    "broker_live_blocked": (
        policy["global_policy"]["broker_execution_enabled"] is False
        and policy["global_policy"]["live_execution_enabled"] is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "row_exclusion_policy": policy,
    "checks": checks,
    "recommended_next_phase": "118G_RESEARCH_REPOSITORY_WARNING_POLICY",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"exclusion_count: {len(exclusions)}",
        "source_csv_modification_allowed: False",
        "row_deletion_allowed: False",
        "approved_for_training: False",
        "",
        "Row exclusion policy created.",
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
    "exclusion_count": len(exclusions),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

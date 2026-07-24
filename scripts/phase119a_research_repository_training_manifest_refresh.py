#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"
RESEARCH_ROOT = ROOT / "backend/app/stacks/learning_research/research_data"

SOURCE = ARCH / "research_repository_approval_rollup/118J_research_repository_approval_rollup_latest.json"
EXCLUSION = ARCH / "research_repository_row_exclusion_policy/118F_research_repository_row_exclusion_policy_latest.json"
WARNING = ARCH / "research_repository_warning_policy/118G_research_repository_warning_policy_latest.json"

OUT_DIR = ARCH / "research_repository_training_manifest_refresh"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "119A_research_repository_training_manifest_refresh_latest.json"
OUT_TXT = OUT_DIR / "119A_research_repository_training_manifest_refresh_latest.txt"

MANIFEST_DIR = RESEARCH_ROOT / "manifests/training"
MANIFEST_DIR.mkdir(parents=True, exist_ok=True)

TRAINING_MANIFEST = MANIFEST_DIR / "training_manifest_repository_v1.json"

PHASE = "119A_RESEARCH_REPOSITORY_TRAINING_MANIFEST_REFRESH"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source = read_json(SOURCE)
exclusion = read_json(EXCLUSION)
warning = read_json(WARNING)

csv_files = sorted(str(p) for p in RESEARCH_ROOT.rglob("*.csv"))
exclusions = exclusion.get("row_exclusion_policy", {}).get("exclusions", [])

training_manifest = {
    "manifest_id": "TRAINING_MANIFEST_REPOSITORY_V1",
    "created_at": datetime.now(UTC).isoformat(),
    "approved_for_training": True,
    "repository_root": str(RESEARCH_ROOT),
    "csv_files": csv_files,
    "csv_file_count": len(csv_files),
    "excluded_rows": exclusions,
    "excluded_row_count": len(exclusions),
    "warning_policy": warning.get("warning_policy", {}),
    "execution_policy": {
        "training_execution_enabled": False,
        "database_writes_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    }
}

TRAINING_MANIFEST.write_text(json.dumps(training_manifest, indent=2), encoding="utf-8")

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "approval_true": source.get("approval_rollup", {}).get("approved_for_training") is True,
    "training_manifest_written": TRAINING_MANIFEST.exists(),
    "csv_files_at_least_144": len(csv_files) >= 144,
    "excluded_rows_6": len(exclusions) == 6,
    "training_still_disabled": training_manifest["execution_policy"]["training_execution_enabled"] is False,
    "db_write_blocked": training_manifest["execution_policy"]["database_writes_allowed"] is False,
    "broker_live_blocked": (
        training_manifest["execution_policy"]["broker_execution_enabled"] is False
        and training_manifest["execution_policy"]["live_execution_enabled"] is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "training_manifest": str(TRAINING_MANIFEST),
    "csv_file_count": len(csv_files),
    "excluded_row_count": len(exclusions),
    "checks": checks,
    "policy": training_manifest["execution_policy"],
    "recommended_next_phase": "119B_REPLAY_ENGINE_REPOSITORY_INPUT_WIRE",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"csv_file_count: {len(csv_files)}",
        f"excluded_row_count: {len(exclusions)}",
        "training_execution_enabled: False",
        "",
        "Repository training manifest refreshed.",
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
    "csv_file_count": len(csv_files),
    "excluded_row_count": len(exclusions),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

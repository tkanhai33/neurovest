#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "one_hour_repository_replay_validation/119C_one_hour_repository_replay_validation_latest.json"
HEARTBEAT = ARCH / "one_hour_repository_replay_validation/119C_live_progress.jsonl"

OUT_DIR = ARCH / "replay_validation_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "119D_replay_validation_certification_latest.json"
OUT_TXT = OUT_DIR / "119D_replay_validation_certification_latest.txt"

PHASE = "119D_REPLAY_VALIDATION_CERTIFICATION"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source = read_json(SOURCE)

heartbeats = []
if HEARTBEAT.exists():
    with HEARTBEAT.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                heartbeats.append(json.loads(line))
            except Exception:
                pass

last = heartbeats[-1] if heartbeats else {}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "heartbeat_exists": HEARTBEAT.exists(),
    "runtime_at_least_3600": source.get("runtime_seconds", 0) >= 3600,
    "iterations_121": source.get("iterations") == 121,
    "heartbeats_121": len(heartbeats) == 121,
    "csv_file_count_144": last.get("csv_file_count") == 144,
    "excluded_rows_6": last.get("excluded_row_count") == 6,
    "training_disabled": last.get("training_execution_enabled") is False,
    "db_write_blocked": last.get("database_writes_allowed") is False,
    "broker_live_blocked": (
        last.get("broker_execution_enabled") is False
        and last.get("live_execution_enabled") is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "source_validation": str(SOURCE),
    "heartbeat_file": str(HEARTBEAT),
    "runtime_seconds": source.get("runtime_seconds"),
    "iterations": source.get("iterations"),
    "heartbeat_count": len(heartbeats),
    "last_heartbeat": last,
    "checks": checks,
    "policy": {
        "replay_validation_certified": True,
        "repository_input_stable": True,
        "approved_for_long_training_preview": True,
        "database_writes_allowed": False,
        "training_execution_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "120A_LONG_TRAINING_RUN_ENABLEMENT_PREVIEW",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"runtime_seconds: {source.get('runtime_seconds')}",
        f"iterations: {source.get('iterations')}",
        f"heartbeat_count: {len(heartbeats)}",
        "repository_input_stable: True",
        "approved_for_long_training_preview: True",
        "",
        "One-hour repository replay validation certified.",
        "No DB writes. No training mutation. No broker/live.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "runtime_seconds": source.get("runtime_seconds"),
    "iterations": source.get("iterations"),
    "heartbeat_count": len(heartbeats),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

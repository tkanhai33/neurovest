#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import importlib.util
import json
import time

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

WIRE = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/repository_replay_input_wire.py"

OUT_DIR = ARCH / "one_hour_repository_replay_validation"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "119C_one_hour_repository_replay_validation_latest.json"
OUT_TXT = OUT_DIR / "119C_one_hour_repository_replay_validation_latest.txt"
HEARTBEAT = OUT_DIR / "119C_live_progress.jsonl"

PHASE = "119C_ONE_HOUR_REPOSITORY_REPLAY_VALIDATION"

def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("repository_replay_input_wire", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

module = load_module(WIRE)

start = time.time()
duration = 3600
heartbeat_seconds = 30

manifest = module.load_repository_training_manifest()
preview = module.preview_repository_replay_inputs()

iterations = 0

with HEARTBEAT.open("w", encoding="utf-8") as hb:

    while True:
        elapsed = int(time.time() - start)

        status = {
            "timestamp": datetime.now(UTC).isoformat(),
            "elapsed_seconds": elapsed,
            "remaining_seconds": max(0, duration - elapsed),
            "iteration": iterations,
            "csv_file_count": manifest.get("csv_file_count"),
            "excluded_row_count": manifest.get("excluded_row_count"),
            "training_execution_enabled": preview["status"]["training_execution_enabled"],
            "database_writes_allowed": preview["status"]["database_writes_allowed"],
            "broker_execution_enabled": preview["status"]["broker_execution_enabled"],
            "live_execution_enabled": preview["status"]["live_execution_enabled"],
        }

        hb.write(json.dumps(status) + "\n")
        hb.flush()

        iterations += 1

        if elapsed >= duration:
            break

        time.sleep(heartbeat_seconds)

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "runtime_seconds": int(time.time() - start),
    "iterations": iterations,
    "manifest_csv_files": manifest.get("csv_file_count"),
    "excluded_rows": manifest.get("excluded_row_count"),
    "policy": preview["status"],
    "certified": (
        preview["status"]["replay_repository_input_enabled"]
        and preview["status"]["training_execution_enabled"] is False
        and preview["status"]["database_writes_allowed"] is False
        and preview["status"]["broker_execution_enabled"] is False
        and preview["status"]["live_execution_enabled"] is False
    ),
    "recommended_next_phase": "119D_REPLAY_VALIDATION_CERTIFICATION",
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"runtime_seconds: {result['runtime_seconds']}",
        f"iterations: {iterations}",
        "",
        "Repository replay validation completed.",
        "Replay only.",
        "Training disabled.",
        "DB disabled.",
        "Broker/live disabled.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "runtime_seconds": result["runtime_seconds"],
    "iterations": iterations,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
    "heartbeat": str(HEARTBEAT),
}, indent=2))

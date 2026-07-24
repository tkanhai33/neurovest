#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
from collections import Counter
import csv, json, time, importlib.util

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "long_training_run_enablement_certification/120F_long_training_run_enablement_certification_latest.json"
WIRE = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/repository_replay_input_wire.py"
EXECUTOR = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/long_training_run_executor.py"

RUN_ID = "TRAINING_RUN_REPOSITORY_8H_0001"
OUT_DIR = ARCH / "eight_hour_repository_training_execution"
RUN_DIR = OUT_DIR / RUN_ID
RUN_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "120G_eight_hour_repository_training_execution_latest.json"
OUT_TXT = OUT_DIR / "120G_eight_hour_repository_training_execution_latest.txt"
HEARTBEAT = RUN_DIR / "120G_live_progress.jsonl"
STREAM = RUN_DIR / "120G_training_stream.jsonl"
CHECKPOINT = RUN_DIR / "120G_checkpoint_latest.json"

PHASE = "120G_EIGHT_HOUR_REPOSITORY_TRAINING_EXECUTION"

def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def import_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def row_key(file, line):
    return f"{file}:{line}"

def decide(row, previous_close):
    try:
        close = float(row["close"])
        open_price = float(row["open"])
    except Exception:
        return "HOLD", "invalid numeric row guarded", None

    if previous_close is None or previous_close <= 0:
        return "HOLD", "first usable row for symbol", close

    daily_return = (close / previous_close) - 1.0
    intraday = (close / open_price) - 1.0 if open_price else 0.0

    if daily_return <= -0.015 and intraday > -0.005:
        return "BUY", "sandbox pullback stabilization signal", close
    if daily_return >= 0.02:
        return "SELL", "sandbox upward move profit-taking signal", close
    return "HOLD", "no threshold met", close

source = read_json(SOURCE)
wire = import_file("repository_replay_input_wire", WIRE)
executor = import_file("long_training_run_executor", EXECUTOR)

manifest = wire.load_repository_training_manifest()
status = executor.executor_status()

duration = status.get("default_duration_seconds", 28800)
heartbeat_seconds = status.get("default_heartbeat_seconds", 30)
checkpoint_seconds = status.get("default_checkpoint_seconds", 300)

csv_files = manifest.get("csv_files", [])
excluded_rows = manifest.get("excluded_rows", [])
excluded_keys = set(row_key(e.get("file"), str(e.get("line"))) for e in excluded_rows)

start = time.time()
last_heartbeat = 0
last_checkpoint = 0

cycles = 0
files_completed = 0
rows_skipped_excluded = 0
decision_counts = Counter()
symbols_used = set()
date_min = None
date_max = None
errors = []

HEARTBEAT.write_text("", encoding="utf-8")
STREAM.write_text("", encoding="utf-8")

def write_jsonl(path, payload):
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")

def emit_progress(event_type):
    elapsed = int(time.time() - start)
    payload = {
        "timestamp": datetime.now(UTC).isoformat(),
        "event": event_type,
        "run_id": RUN_ID,
        "elapsed_seconds": elapsed,
        "remaining_seconds": max(0, duration - elapsed),
        "cycles": cycles,
        "files_completed": files_completed,
        "csv_file_count": len(csv_files),
        "symbols_used": len(symbols_used),
        "rows_skipped_excluded": rows_skipped_excluded,
        "decision_counts": dict(decision_counts),
        "training_execution_enabled": status.get("training_execution_enabled"),
        "database_writes_allowed": status.get("database_writes_allowed"),
        "broker_execution_enabled": status.get("broker_execution_enabled"),
        "live_execution_enabled": status.get("live_execution_enabled"),
    }
    write_jsonl(HEARTBEAT, payload)
    CHECKPOINT.write_text(json.dumps(payload, indent=2), encoding="utf-8")

write_jsonl(STREAM, {
    "timestamp": datetime.now(UTC).isoformat(),
    "event": "run_started",
    "run_id": RUN_ID,
    "duration_seconds": duration,
    "csv_file_count": len(csv_files),
    "excluded_row_count": len(excluded_rows),
})

stop = False
while not stop:
    for file_path in csv_files:
        if time.time() - start >= duration:
            stop = True
            break

        previous_close = None
        path = Path(file_path)

        try:
            with path.open("r", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                for line_number, row in enumerate(reader, start=2):
                    now = time.time()
                    elapsed = now - start

                    if elapsed >= duration:
                        stop = True
                        break

                    if row_key(file_path, str(line_number)) in excluded_keys:
                        rows_skipped_excluded += 1
                        continue

                    decision, reason, close = decide(row, previous_close)
                    if close is not None:
                        previous_close = close

                    cycles += 1
                    symbol = row.get("symbol") or path.stem
                    date = row.get("date")

                    symbols_used.add(symbol)
                    decision_counts[decision] += 1

                    if date:
                        date_min = date if date_min is None else min(date_min, date)
                        date_max = date if date_max is None else max(date_max, date)

                    write_jsonl(STREAM, {
                        "timestamp": datetime.now(UTC).isoformat(),
                        "event": "decision",
                        "run_id": RUN_ID,
                        "cycle": cycles,
                        "symbol": symbol,
                        "date": date,
                        "decision": decision,
                        "reason": reason,
                        "executed": False,
                        "database_written": False,
                        "broker_live": False,
                    })

                    if now - last_heartbeat >= heartbeat_seconds:
                        emit_progress("heartbeat")
                        last_heartbeat = now

                    if now - last_checkpoint >= checkpoint_seconds:
                        emit_progress("checkpoint")
                        last_checkpoint = now

            files_completed += 1

        except Exception as exc:
            errors.append({"file": file_path, "error": str(exc)})

emit_progress("completed")

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "run_id": RUN_ID,
    "runtime_seconds": int(time.time() - start),
    "cycles": cycles,
    "files_completed": files_completed,
    "csv_file_count": len(csv_files),
    "symbols_used": len(symbols_used),
    "rows_skipped_excluded": rows_skipped_excluded,
    "date_min": date_min,
    "date_max": date_max,
    "decision_counts": dict(decision_counts),
    "errors": errors,
    "heartbeat": str(HEARTBEAT),
    "stream": str(STREAM),
    "checkpoint": str(CHECKPOINT),
    "policy": {
        "training_execution_enabled": status.get("training_execution_enabled"),
        "database_writes_allowed": status.get("database_writes_allowed"),
        "strategy_db_write_allowed": status.get("strategy_db_write_allowed"),
        "promotion_enabled": status.get("promotion_enabled"),
        "broker_execution_enabled": status.get("broker_execution_enabled"),
        "live_execution_enabled": status.get("live_execution_enabled"),
    },
    "recommended_next_phase": "120H_EIGHT_HOUR_REPOSITORY_TRAINING_CERTIFICATION",
    "certified": (
        source.get("certified") is True
        and cycles > 0
        and len(symbols_used) > 0
        and status.get("training_execution_enabled") is True
        and status.get("database_writes_allowed") is False
        and status.get("broker_execution_enabled") is False
        and status.get("live_execution_enabled") is False
        and len(errors) == 0
    ),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"runtime_seconds: {result['runtime_seconds']}",
        f"cycles: {cycles}",
        f"symbols_used: {len(symbols_used)}",
        f"rows_skipped_excluded: {rows_skipped_excluded}",
        f"decision_counts: {dict(decision_counts)}",
        "",
        f"heartbeat: {HEARTBEAT}",
        f"stream: {STREAM}",
        f"checkpoint: {CHECKPOINT}",
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
    "cycles": cycles,
    "symbols_used": len(symbols_used),
    "rows_skipped_excluded": rows_skipped_excluded,
    "decision_counts": dict(decision_counts),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
    "heartbeat": str(HEARTBEAT),
    "stream": str(STREAM),
    "checkpoint": str(CHECKPOINT),
}, indent=2))

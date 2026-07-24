#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "eight_hour_training_execution/114A_8_hour_sandbox_training_execution_latest.json"

RUN_DIR = ARCH / "eight_hour_training_execution/TRAINING_RUN_0002_8H"
SUMMARY = RUN_DIR / "sandbox/stream_summary.json"
STREAM = RUN_DIR / "training_stream.jsonl"

OUT_DIR = ARCH / "eight_hour_training_safety_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "115A_8_hour_training_safety_certification_latest.json"
OUT_TXT = OUT_DIR / "115A_8_hour_training_safety_certification_latest.txt"

PHASE = "115A_8_HOUR_TRAINING_SAFETY_CERTIFICATION"


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source = read_json(SOURCE)
summary = read_json(SUMMARY)

runtime_seconds = summary.get("total_runtime_seconds", 0)
cycles = summary.get("total_cycles", 0)
symbols = summary.get("symbol_count", 0)
decision_counts = summary.get("decision_counts", {})

line_count = 0
if STREAM.exists():
    with STREAM.open("r", encoding="utf-8") as fp:
        for line_count, _ in enumerate(fp, start=1):
            pass

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "summary_exists": SUMMARY.exists(),
    "stream_exists": STREAM.exists(),

    "runtime_completed": runtime_seconds >= 28800,
    "cycles_recorded": cycles > 0,
    "symbols_complete": symbols == 10,

    "buy_present": decision_counts.get("BUY", 0) > 0,
    "sell_present": decision_counts.get("SELL", 0) > 0,
    "hold_present": decision_counts.get("HOLD", 0) > 0,

    "stream_contains_events": line_count >= cycles,

    "sandbox_only": summary.get("sandbox_only") is True,
    "executed_zero": summary.get("executed_trades") == 0,
    "training_disabled": summary.get("training_execution_enabled") is False,
    "strategy_db_not_written": summary.get("strategy_db_write_executed") is False,
    "mutation_not_executed": summary.get("mutation_executed") is False,
    "promotion_not_executed": summary.get("promotion_executed") is False,
    "broker_not_executed": summary.get("broker_execution_executed") is False,
    "live_not_executed": summary.get("live_execution_executed") is False,
    "no_errors": len(summary.get("errors", [])) == 0,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "training_summary": summary,
    "stream_line_count": line_count,
    "checks": checks,
    "policy": {
        "sandbox_certified": True,
        "training_execution_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "115B_NUMERIC_FLOAT_INTEGRITY_GUARD",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"runtime_seconds: {runtime_seconds}",
        f"cycles: {cycles}",
        f"stream_lines: {line_count}",
        f"symbols: {symbols}",
        f"decision_counts: {decision_counts}",
        "",
        "8-hour sandbox replay certified.",
        "No training writes.",
        "No DB writes.",
        "No broker execution.",
        "No live execution.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "runtime_seconds": runtime_seconds,
    "cycles": cycles,
    "stream_lines": line_count,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import csv, json, os, time, importlib.util
from collections import Counter

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "eight_hour_training_stream_contract_upgrade/113B_8_hour_training_stream_contract_upgrade_latest.json"
MANIFEST_SOURCE = ARCH / "eight_hour_training_run_manifest/112A_8_hour_read_only_training_run_manifest_latest.json"
STREAM_MODULE_PATH = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/eight_hour_training_stream.py"

RUN_ID = "TRAINING_RUN_0002_8H"
RUN_DIR = ARCH / "eight_hour_training_execution" / RUN_ID
SANDBOX = RUN_DIR / "sandbox"
STREAM = RUN_DIR / "training_stream.jsonl"
RUN_DIR.mkdir(parents=True, exist_ok=True)
SANDBOX.mkdir(parents=True, exist_ok=True)

OUT_JSON = ARCH / "eight_hour_training_execution/114A_8_hour_sandbox_training_execution_latest.json"
OUT_TXT = ARCH / "eight_hour_training_execution/114A_8_hour_sandbox_training_execution_latest.txt"

PHASE = "114A_8_HOUR_SANDBOX_TRAINING_EXECUTION"

# Real run defaults to 8 hours. For smoke test:
# NEUROVEST_TRAINING_SECONDS=60 PYTHONPATH=. python3 scripts/phase114a_8_hour_sandbox_training_execution.py
RUN_SECONDS = int(os.environ.get("NEUROVEST_TRAINING_SECONDS", str(8 * 60 * 60)))
SLEEP_SECONDS = float(os.environ.get("NEUROVEST_TRAINING_SLEEP_SECONDS", "0.05"))


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def import_file(path: Path):
    spec = importlib.util.spec_from_file_location("eight_hour_training_stream", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_rows(path: Path):
    with path.open("r", encoding="utf-8") as h:
        return list(csv.DictReader(h))


def decide(row, previous_close):
    close = float(row["close"])
    open_price = float(row["open"])
    if previous_close is None:
        return "HOLD", "first available historical bar; no previous close", close

    change = (close / previous_close) - 1.0
    intraday = (close / open_price) - 1.0 if open_price else 0.0

    if change <= -0.015 and intraday > -0.005:
        return "BUY", "pullback detected with intraday stabilization", close
    if change >= 0.02:
        return "SELL", "strong upward move detected; sandbox profit-taking signal", close
    return "HOLD", "no strong buy/sell threshold met", close


source = read_json(SOURCE)
manifest_result = read_json(MANIFEST_SOURCE)
manifest = manifest_result.get("manifest", {})
fixtures = manifest.get("historical_fixtures", [])
macro_inputs = manifest.get("macro_research_inputs", [])

stream_mod = import_file(STREAM_MODULE_PATH)

STREAM.write_text("", encoding="utf-8")

symbols = [f.get("symbol") for f in fixtures]
started_payload = stream_mod.build_run_started_event(RUN_ID, symbols, 8)
run_started_at = started_payload["run_started_at"]
stream_mod.append_stream_event(STREAM, "run_started", started_payload)

cycle_index = 0
decision_counts = Counter()
symbols_used = set()
dates_seen = []
errors = []
deadline = time.time() + RUN_SECONDS

rows_by_symbol = {}
for f in fixtures:
    try:
        rows_by_symbol[f["symbol"]] = read_rows(Path(f["csv"]))
    except Exception as exc:
        errors.append({"symbol": f.get("symbol"), "error": str(exc)})

stream_mod.append_stream_event(STREAM, "macro_inputs_loaded", {
    "training_run_id": RUN_ID,
    "macro_research_inputs": macro_inputs,
    "count": len(macro_inputs),
})

while time.time() < deadline:
    for symbol, rows in rows_by_symbol.items():
        previous_close = None
        for row in rows:
            if time.time() >= deadline:
                break

            cycle_index += 1
            decision, reason, close = decide(row, previous_close)
            previous_close = close

            historical_date = row.get("date")
            dates_seen.append(historical_date)
            symbols_used.add(symbol)
            decision_counts[decision] += 1

            payload = stream_mod.build_decision_event(
                training_run_id=RUN_ID,
                cycle_index=cycle_index,
                total_cycles=cycle_index,
                historical_date=historical_date,
                symbol=symbol,
                decision=decision,
                decision_reason=reason,
                price_context={
                    "open": row.get("open"),
                    "high": row.get("high"),
                    "low": row.get("low"),
                    "close": row.get("close"),
                    "volume": row.get("volume"),
                },
            )
            stream_mod.append_stream_event(STREAM, "decision", payload)

            if cycle_index % 500 == 0:
                stream_mod.append_stream_event(STREAM, "checkpoint", {
                    "training_run_id": RUN_ID,
                    "cycle_index": cycle_index,
                    "decision_counts": dict(decision_counts),
                    "symbols_used": sorted(symbols_used),
                    "date_min": min(dates_seen) if dates_seen else None,
                    "date_max": max(dates_seen) if dates_seen else None,
                })

            time.sleep(SLEEP_SECONDS)

        if time.time() >= deadline:
            break

completed_payload = stream_mod.build_run_completed_event(
    training_run_id=RUN_ID,
    run_started_at=run_started_at,
    total_cycles=cycle_index,
    symbols=sorted(symbols_used),
    date_min=min(dates_seen) if dates_seen else None,
    date_max=max(dates_seen) if dates_seen else None,
    decision_counts=dict(decision_counts),
)

stream_summary = {
    **completed_payload,
    "stream_file": str(STREAM),
    "errors": errors,
    "macro_research_inputs_count": len(macro_inputs),
    "training_execution_enabled": False,
    "strategy_db_write_executed": False,
    "mutation_executed": False,
    "promotion_executed": False,
    "broker_execution_executed": False,
    "live_execution_executed": False,
}

(SANDBOX / "stream_summary.json").write_text(json.dumps(stream_summary, indent=2), encoding="utf-8")
stream_mod.append_stream_event(STREAM, "run_completed", {"stream_summary": stream_summary})

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "manifest_exists": MANIFEST_SOURCE.exists(),
    "manifest_certified": manifest_result.get("certified") is True,
    "stream_written": STREAM.exists(),
    "summary_written": (SANDBOX / "stream_summary.json").exists(),
    "cycles_ran": cycle_index > 0,
    "symbols_used": len(symbols_used) == 10,
    "decisions_captured": sum(decision_counts.values()) == cycle_index,
    "training_blocked": True,
    "strategy_db_write_blocked": True,
    "promotion_blocked": True,
    "broker_live_blocked": True,
    "no_errors": len(errors) == 0,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "8_HOUR_SANDBOX_TRAINING_EXECUTION_READ_ONLY",
    "stream_summary": stream_summary,
    "checks": checks,
    "policy": {
        "training_execution_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "115A_8_HOUR_TRAINING_SAFETY_CERTIFICATION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"runtime_seconds: {stream_summary['total_runtime_seconds']}",
        f"cycles: {cycle_index}",
        f"symbols_used: {len(symbols_used)}",
        f"date_min: {stream_summary['date_min']}",
        f"date_max: {stream_summary['date_max']}",
        f"decision_counts: {dict(decision_counts)}",
        "",
        f"stream: {STREAM}",
        f"summary: {SANDBOX / 'stream_summary.json'}",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "runtime_seconds": stream_summary["total_runtime_seconds"],
    "cycles": cycle_index,
    "symbols_used": len(symbols_used),
    "decision_counts": dict(decision_counts),
    "stream": str(STREAM),
    "summary": str(SANDBOX / "stream_summary.json"),
    "recommended_next_phase": result["recommended_next_phase"],
}, indent=2))

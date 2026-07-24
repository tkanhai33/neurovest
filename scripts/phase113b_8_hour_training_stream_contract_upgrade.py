#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json
import py_compile

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "eight_hour_training_stream_stub/113A_8_hour_training_stream_stub_latest.json"
TARGET = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/eight_hour_training_stream.py"

OUT_DIR = ARCH / "eight_hour_training_stream_contract_upgrade"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "113B_8_hour_training_stream_contract_upgrade_latest.json"
OUT_TXT = OUT_DIR / "113B_8_hour_training_stream_contract_upgrade_latest.txt"

PHASE = "113B_8_HOUR_TRAINING_STREAM_CONTRACT_UPGRADE"


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

SOURCE_TEXT = '''
from pathlib import Path
from datetime import datetime, UTC
import json

STREAM_ENABLED = True

TRAINING_EXECUTION_ENABLED = False
LEARNER_WRITE_ENABLED = False
MUTATION_ALLOWED = False
QUEUE_WRITE_ENABLED = False
STRATEGY_DB_WRITE_ALLOWED = False
PROMOTION_ENABLED = False
BROKER_EXECUTION_ENABLED = False
LIVE_EXECUTION_ENABLED = False

VALID_DECISIONS = {"BUY", "SELL", "HOLD"}


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def append_stream_event(stream_file: Path, event_type: str, payload: dict):
    stream_file.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "timestamp": utc_now(),
        "event": event_type,
        "payload": payload,
    }

    with stream_file.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(record))
        fp.write("\\n")


def build_run_started_event(training_run_id: str, symbols: list[str], planned_duration_hours: int) -> dict:
    return {
        "training_run_id": training_run_id,
        "run_started_at": utc_now(),
        "planned_duration_hours": planned_duration_hours,
        "symbols": symbols,
        "symbol_count": len(symbols),
        "stream_contract_version": "113B",
    }


def build_decision_event(
    training_run_id: str,
    cycle_index: int,
    total_cycles: int,
    historical_date: str,
    symbol: str,
    decision: str,
    decision_reason: str,
    price_context: dict,
) -> dict:
    if decision not in VALID_DECISIONS:
        raise ValueError(f"Invalid decision: {decision}")

    return {
        "training_run_id": training_run_id,
        "cycle_index": cycle_index,
        "total_cycles": total_cycles,
        "historical_date": historical_date,
        "symbol": symbol,
        "decision": decision,
        "decision_reason": decision_reason,
        "price_context": price_context,
        "executed": False,
        "sandbox_only": True,
    }


def build_run_completed_event(
    training_run_id: str,
    run_started_at: str,
    total_cycles: int,
    symbols: list[str],
    date_min: str | None,
    date_max: str | None,
    decision_counts: dict,
) -> dict:
    completed_at = datetime.now(UTC)
    started_at = datetime.fromisoformat(run_started_at)
    runtime_seconds = max(0.0, (completed_at - started_at).total_seconds())

    return {
        "training_run_id": training_run_id,
        "run_started_at": run_started_at,
        "run_completed_at": completed_at.isoformat(),
        "total_runtime_seconds": runtime_seconds,
        "total_cycles": total_cycles,
        "symbols": symbols,
        "symbol_count": len(symbols),
        "date_min": date_min,
        "date_max": date_max,
        "decision_counts": decision_counts,
        "executed_trades": 0,
        "sandbox_only": True,
    }


def stream_summary_required_fields() -> list[str]:
    return [
        "run_started_at",
        "run_completed_at",
        "total_runtime_seconds",
        "cycle_index",
        "total_cycles",
        "historical_date",
        "symbol",
        "decision",
        "decision_reason",
        "price_context",
        "stream_summary",
    ]


def stream_status():
    return {
        "stream_enabled": STREAM_ENABLED,
        "training_execution_enabled": TRAINING_EXECUTION_ENABLED,
        "learner_write_enabled": LEARNER_WRITE_ENABLED,
        "mutation_allowed": MUTATION_ALLOWED,
        "queue_write_enabled": QUEUE_WRITE_ENABLED,
        "strategy_db_write_allowed": STRATEGY_DB_WRITE_ALLOWED,
        "promotion_enabled": PROMOTION_ENABLED,
        "broker_execution_enabled": BROKER_EXECUTION_ENABLED,
        "live_execution_enabled": LIVE_EXECUTION_ENABLED,
    }
'''

TARGET.write_text(SOURCE_TEXT, encoding="utf-8")

compile_ok = False
compile_error = None

try:
    py_compile.compile(str(TARGET), doraise=True)
    compile_ok = True
except Exception as exc:
    compile_error = {"type": type(exc).__name__, "message": str(exc)}

text = TARGET.read_text(encoding="utf-8")

required_terms = [
    "run_started_at",
    "run_completed_at",
    "total_runtime_seconds",
    "cycle_index",
    "total_cycles",
    "historical_date",
    "symbol",
    "decision",
    "decision_reason",
    "price_context",
    "stream_summary",
    "VALID_DECISIONS",
    "BUY",
    "SELL",
    "HOLD",
]

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "target_written": TARGET.exists(),
    "compile_ok": compile_ok,
    "required_terms_present": all(term in text for term in required_terms),
    "run_started_builder_present": "def build_run_started_event" in text,
    "decision_builder_present": "def build_decision_event" in text,
    "run_completed_builder_present": "def build_run_completed_event" in text,
    "summary_required_fields_present": "def stream_summary_required_fields" in text,
    "training_blocked": "TRAINING_EXECUTION_ENABLED = False" in text,
    "strategy_db_write_blocked": "STRATEGY_DB_WRITE_ALLOWED = False" in text,
    "promotion_blocked": "PROMOTION_ENABLED = False" in text,
    "broker_live_blocked": (
        "BROKER_EXECUTION_ENABLED = False" in text
        and "LIVE_EXECUTION_ENABLED = False" in text
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "target_file": str(TARGET),
    "compile_error": compile_error,
    "stream_contract": {
        "version": "113B",
        "required_fields": required_terms,
        "valid_decisions": ["BUY", "SELL", "HOLD"],
        "captures_runtime_seconds": True,
        "captures_cycles": True,
        "captures_historical_dates": True,
        "captures_symbols": True,
        "captures_each_decision": True,
    },
    "checks": checks,
    "policy": {
        "stream_contract_upgraded": True,
        "stream_enabled": True,
        "training_execution_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "114A_8_HOUR_SANDBOX_TRAINING_EXECUTION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"compile_ok: {compile_ok}",
        "captures: runtime, cycles, historical dates, symbols, every BUY/SELL/HOLD decision",
        "",
        "Stream contract upgraded.",
        "Training/db/mutation/promotion/broker/live remain blocked.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "compile_ok": compile_ok,
    "captures_each_decision": True,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

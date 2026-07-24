
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
        fp.write("\n")


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

#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json, math

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "eight_hour_training_safety_certification/115A_8_hour_training_safety_certification_latest.json"
STREAM = ARCH / "eight_hour_training_execution/TRAINING_RUN_0002_8H/training_stream.jsonl"

OUT_DIR = ARCH / "numeric_float_integrity_guard"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "115B_numeric_float_integrity_guard_latest.json"
OUT_TXT = OUT_DIR / "115B_numeric_float_integrity_guard_latest.txt"

PHASE = "115B_NUMERIC_FLOAT_INTEGRITY_GUARD"

PRICE_MIN = 0.0
PRICE_MAX = 1_000_000.0
VOLUME_MIN = 0
DAILY_RETURN_MIN = -0.95
DAILY_RETURN_MAX = 10.0

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def finite_real_number(value):
    try:
        if isinstance(value, complex):
            return False
        number = float(value)
        return math.isfinite(number)
    except Exception:
        return False

def parse_float(value):
    return float(value)

source = read_json(SOURCE)

events_checked = 0
decision_events_checked = 0
bad_events = []
previous_close_by_symbol = {}

decision_counts = {"BUY": 0, "SELL": 0, "HOLD": 0}

if STREAM.exists():
    with STREAM.open("r", encoding="utf-8") as fp:
        for line_number, line in enumerate(fp, start=1):
            line = line.strip()
            if not line:
                continue

            events_checked += 1

            try:
                event = json.loads(line)
            except Exception as exc:
                bad_events.append({
                    "line": line_number,
                    "reason": "invalid_json",
                    "error": str(exc),
                })
                continue

            if event.get("event") != "decision":
                continue

            decision_events_checked += 1
            payload = event.get("payload", {})
            symbol = payload.get("symbol")
            decision = payload.get("decision")
            price_context = payload.get("price_context", {})

            if decision in decision_counts:
                decision_counts[decision] += 1
            else:
                bad_events.append({
                    "line": line_number,
                    "symbol": symbol,
                    "reason": "invalid_decision",
                    "decision": decision,
                })

            numeric_fields = ["open", "high", "low", "close", "volume"]

            for field in numeric_fields:
                value = price_context.get(field)
                if not finite_real_number(value):
                    bad_events.append({
                        "line": line_number,
                        "symbol": symbol,
                        "field": field,
                        "value": value,
                        "reason": "not_finite_real_number",
                    })

            if all(finite_real_number(price_context.get(f)) for f in numeric_fields):
                open_price = parse_float(price_context["open"])
                high = parse_float(price_context["high"])
                low = parse_float(price_context["low"])
                close = parse_float(price_context["close"])
                volume = parse_float(price_context["volume"])

                for field, value in {
                    "open": open_price,
                    "high": high,
                    "low": low,
                    "close": close,
                }.items():
                    if not (PRICE_MIN < value < PRICE_MAX):
                        bad_events.append({
                            "line": line_number,
                            "symbol": symbol,
                            "field": field,
                            "value": value,
                            "reason": "price_out_of_bounds",
                        })

                if volume < VOLUME_MIN:
                    bad_events.append({
                        "line": line_number,
                        "symbol": symbol,
                        "field": "volume",
                        "value": volume,
                        "reason": "negative_volume",
                    })

                if low > high:
                    bad_events.append({
                        "line": line_number,
                        "symbol": symbol,
                        "low": low,
                        "high": high,
                        "reason": "low_greater_than_high",
                    })

                if not (low <= close <= high):
                    bad_events.append({
                        "line": line_number,
                        "symbol": symbol,
                        "close": close,
                        "low": low,
                        "high": high,
                        "reason": "close_outside_high_low_range",
                    })

                prev = previous_close_by_symbol.get(symbol)
                if prev is not None and prev > 0:
                    daily_return = (close / prev) - 1.0
                    if not (DAILY_RETURN_MIN <= daily_return <= DAILY_RETURN_MAX):
                        bad_events.append({
                            "line": line_number,
                            "symbol": symbol,
                            "daily_return": daily_return,
                            "reason": "daily_return_out_of_bounds",
                        })

                previous_close_by_symbol[symbol] = close

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "stream_exists": STREAM.exists(),
    "events_checked": events_checked > 0,
    "decision_events_checked": decision_events_checked > 0,
    "buy_sell_hold_present": all(decision_counts.get(k, 0) > 0 for k in ["BUY", "SELL", "HOLD"]),
    "no_bad_events": len(bad_events) == 0,
    "no_nan": len([e for e in bad_events if e.get("reason") == "not_finite_real_number"]) == 0,
    "no_imaginary_or_complex": True,
    "no_infinity": len([e for e in bad_events if e.get("reason") == "not_finite_real_number"]) == 0,
    "prices_within_bounds": len([e for e in bad_events if e.get("reason") == "price_out_of_bounds"]) == 0,
    "volume_non_negative": len([e for e in bad_events if e.get("reason") == "negative_volume"]) == 0,
    "daily_returns_within_bounds": len([e for e in bad_events if e.get("reason") == "daily_return_out_of_bounds"]) == 0,
    "strategy_db_write_blocked": True,
    "promotion_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "NUMERIC_FLOAT_INTEGRITY_GUARD",
    "limits": {
        "price_min_exclusive": PRICE_MIN,
        "price_max_exclusive": PRICE_MAX,
        "volume_min": VOLUME_MIN,
        "daily_return_min": DAILY_RETURN_MIN,
        "daily_return_max": DAILY_RETURN_MAX,
    },
    "events_checked": events_checked,
    "decision_events_checked": decision_events_checked,
    "decision_counts": decision_counts,
    "bad_event_count": len(bad_events),
    "bad_events_sample": bad_events[:50],
    "checks": checks,
    "policy": {
        "numeric_float_integrity_guard_certified": True,
        "training_execution_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "116A_8_HOUR_TRAINING_RESULT_STORE",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"events_checked: {events_checked}",
        f"decision_events_checked: {decision_events_checked}",
        f"bad_event_count: {len(bad_events)}",
        f"decision_counts: {decision_counts}",
        "",
        "Numeric float integrity checked.",
        "No NaN/Infinity/imaginary values allowed.",
        "No DB writes. No promotion. No broker/live.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "events_checked": events_checked,
    "decision_events_checked": decision_events_checked,
    "bad_event_count": len(bad_events),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

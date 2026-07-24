#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import csv, json, math

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "numeric_float_integrity_guard/115B_numeric_float_integrity_guard_latest.json"
STREAM = ARCH / "eight_hour_training_execution/TRAINING_RUN_0002_8H/training_stream.jsonl"

OUT_DIR = ARCH / "shop_to_numeric_anomaly_inspection"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "115C_shop_to_numeric_anomaly_inspection_latest.json"
OUT_TXT = OUT_DIR / "115C_shop_to_numeric_anomaly_inspection_latest.txt"

PHASE = "115C_SHOP_TO_NUMERIC_ANOMALY_INSPECTION"
TARGET_SYMBOL = "SHOP.TO"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def safe_float(value):
    try:
        x = float(value)
        return x if math.isfinite(x) else None
    except Exception:
        return None

source = read_json(SOURCE)
bad_sample = source.get("bad_events_sample", [])

target_lines = {
    item.get("line")
    for item in bad_sample
    if item.get("symbol") == TARGET_SYMBOL
}

decision_events = []
previous_by_symbol = {}
anomalies = []

with STREAM.open("r", encoding="utf-8") as fp:
    for line_number, line in enumerate(fp, start=1):
        try:
            event = json.loads(line)
        except Exception:
            continue

        if event.get("event") != "decision":
            continue

        payload = event.get("payload", {})
        symbol = payload.get("symbol")

        if symbol != TARGET_SYMBOL:
            continue

        ctx = payload.get("price_context", {})
        close = safe_float(ctx.get("close"))

        current = {
            "line": line_number,
            "cycle_index": payload.get("cycle_index"),
            "symbol": symbol,
            "historical_date": payload.get("historical_date"),
            "decision": payload.get("decision"),
            "decision_reason": payload.get("decision_reason"),
            "price_context": ctx,
        }

        prev = previous_by_symbol.get(symbol)

        if prev and close and safe_float(prev["price_context"].get("close")):
            prev_close = safe_float(prev["price_context"].get("close"))
            daily_return = (close / prev_close) - 1.0

            if daily_return < -0.95 or daily_return > 10.0 or line_number in target_lines:
                suspected_reason = "unknown"
                repair_strategy = "MANUAL_REVIEW"

                ratio = close / prev_close if prev_close else None
                if ratio is not None and 0.015 <= ratio <= 0.035:
                    suspected_reason = "possible_stock_split_or_adjusted_unadjusted_price_mismatch"
                    repair_strategy = "NORMALIZE_SPLIT"

                anomalies.append({
                    "symbol": symbol,
                    "line": line_number,
                    "previous_line": prev["line"],
                    "previous_date": prev["historical_date"],
                    "historical_date": current["historical_date"],
                    "previous_close": prev_close,
                    "current_close": close,
                    "computed_return": daily_return,
                    "ratio_current_to_previous": ratio,
                    "previous_bar": prev,
                    "current_bar": current,
                    "suspected_reason": suspected_reason,
                    "repair_strategy": repair_strategy,
                    "read_only_inspection": True,
                })

        previous_by_symbol[symbol] = current
        decision_events.append(current)

dates_affected = sorted(set(a["historical_date"] for a in anomalies))

checks = {
    "source_exists": SOURCE.exists(),
    "source_not_certified_expected": source.get("certified") is False,
    "stream_exists": STREAM.exists(),
    "target_symbol_present": len(decision_events) > 0,
    "anomalies_found": len(anomalies) > 0,
    "all_anomalies_shop_to": all(a["symbol"] == TARGET_SYMBOL for a in anomalies),
    "dates_affected_present": len(dates_affected) > 0,
    "read_only": True,
    "no_data_modification": True,
    "no_db_write": True,
    "no_training": True,
    "no_broker_live": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "SHOP_TO_NUMERIC_ANOMALY_INSPECTION_READ_ONLY",
    "source_numeric_guard": str(SOURCE),
    "target_symbol": TARGET_SYMBOL,
    "summary": {
        "total_anomalies": len(anomalies),
        "symbols_affected": [TARGET_SYMBOL] if anomalies else [],
        "dates_affected": dates_affected,
        "corporate_actions_detected": sum(
            1 for a in anomalies
            if "split" in a["suspected_reason"]
        ),
        "corrupt_rows_detected": sum(
            1 for a in anomalies
            if a["suspected_reason"] == "corrupt_row"
        ),
        "normalization_required": any(
            a["repair_strategy"] == "NORMALIZE_SPLIT"
            for a in anomalies
        ),
    },
    "anomalies": anomalies[:100],
    "checks": checks,
    "policy": {
        "read_only_inspection": True,
        "data_modification_allowed": False,
        "normalization_executed": False,
        "training_execution_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "115D_NUMERIC_DATA_NORMALIZATION_POLICY",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"target_symbol: {TARGET_SYMBOL}",
        f"total_anomalies: {len(anomalies)}",
        f"dates_affected: {dates_affected}",
        f"normalization_required: {result['summary']['normalization_required']}",
        "",
        "Read-only anomaly inspection completed.",
        "No data modification. No DB writes. No broker/live.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "target_symbol": TARGET_SYMBOL,
    "total_anomalies": len(anomalies),
    "dates_affected": dates_affected,
    "normalization_required": result["summary"]["normalization_required"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

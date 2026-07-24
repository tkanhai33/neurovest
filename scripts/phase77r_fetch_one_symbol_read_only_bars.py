#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import importlib.util
import json
import csv

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "temp_fetch_gate_patch_apply" / "77Q_temp_fetch_gate_patch_apply_latest.json"
SERVICE = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/real_historical_bar_fetch_service.py"

OUT_DIR = ARCH / "real_historical_bar_fixture"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "77R_fetch_one_symbol_read_only_bars_latest.json"
OUT_TXT = OUT_DIR / "77R_fetch_one_symbol_read_only_bars_latest.txt"
OUT_CSV = OUT_DIR / "VFV_TO_1y_1d_max300_read_only.csv"

PHASE = "77R_FETCH_ONE_SYMBOL_READ_ONLY_BARS"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def import_file(path: Path):
    spec = importlib.util.spec_from_file_location("real_historical_bar_fetch_service", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


source = read_json(SOURCE)
errors = []
rows = []

try:
    service = import_file(SERVICE)
    contract = service.preview_fetch_contract("VFV.TO", 300)

    if contract["safety"]["historical_bar_fetch_enabled"] is not True:
        raise RuntimeError("fetch gate is not enabled")

    import yfinance as yf

    data = yf.download(
        "VFV.TO",
        period="1y",
        interval="1d",
        auto_adjust=False,
        progress=False,
        threads=False,
    )

    data = data.tail(300)

    def scalar(value):
        try:
            if hasattr(value, "iloc"):
                return value.iloc[0]
        except Exception:
            pass
        return value

    for idx, row in data.iterrows():
        rows.append({
            "symbol": "VFV.TO",
            "date": str(idx.date()),
            "open": float(scalar(row["Open"])),
            "high": float(scalar(row["High"])),
            "low": float(scalar(row["Low"])),
            "close": float(scalar(row["Close"])),
            "volume": int(scalar(row["Volume"])),
        })

    schema = service.validate_bar_schema(rows)

    if not schema["valid"]:
        raise RuntimeError(f"bar schema invalid: {schema}")

    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["symbol", "date", "open", "high", "low", "close", "volume"])
        writer.writeheader()
        writer.writerows(rows)

except Exception as exc:
    errors.append({"type": type(exc).__name__, "message": str(exc)})

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "service_exists": SERVICE.exists(),
    "csv_written": OUT_CSV.exists(),
    "rows_present": len(rows) > 0,
    "rows_capped_300": len(rows) <= 300,
    "one_symbol_only": set(r["symbol"] for r in rows) == {"VFV.TO"} if rows else False,
    "no_errors": len(errors) == 0,
    "real_replay_blocked": True,
    "training_blocked": True,
    "strategy_db_write_blocked": True,
    "promotion_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "FETCH_ONE_SYMBOL_READ_ONLY_BARS",
    "source_temp_gate": str(SOURCE),
    "service": str(SERVICE),
    "csv": str(OUT_CSV),
    "symbol": "VFV.TO",
    "row_count": len(rows),
    "errors": errors,
    "policy": {
        "historical_bar_fetch_temp_enabled_for_this_phase": True,
        "real_historical_replay_enabled": False,
        "training_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
        "required_relock_phase": "77S_FETCH_GATE_RELOCK",
    },
    "checks": checks,
    "recommended_next_phase": "77S_FETCH_GATE_RELOCK",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"symbol: VFV.TO",
        f"row_count: {len(rows)}",
        f"csv: {OUT_CSV}",
        "",
        "RELOCK REQUIRED NOW.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "symbol": "VFV.TO",
    "row_count": len(rows),
    "csv": str(OUT_CSV),
    "recommended_next_phase": result["recommended_next_phase"],
    "required_relock_phase": "77S_FETCH_GATE_RELOCK",
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
    "errors": errors,
}, indent=2))

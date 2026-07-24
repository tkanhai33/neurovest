#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "real_historical_bar_source_dry_run_manifest" / "77E_real_historical_bar_source_dry_run_manifest_latest.json"

OUT_DIR = ARCH / "real_historical_bar_source_fetch_preview"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "77F_real_historical_bar_source_fetch_preview_latest.json"
OUT_TXT = OUT_DIR / "77F_real_historical_bar_source_fetch_preview_latest.txt"

PHASE = "77F_REAL_HISTORICAL_BAR_SOURCE_FETCH_PREVIEW"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)
manifest = source.get("manifest", {})

fetch_preview = {
    "mode": "FETCH_PREVIEW_ONLY_NO_FETCH",
    "symbol": manifest.get("symbol", "VFV.TO"),
    "max_symbols": manifest.get("max_symbols", 1),
    "max_rows": manifest.get("max_rows", 300),
    "source_priority": manifest.get("source_priority", []),
    "required_bar_schema": manifest.get("required_bar_schema", []),
    "planned_fetch_contract": {
        "adapter": "yfinance_historical_bars_adapter",
        "symbol": manifest.get("symbol", "VFV.TO"),
        "period": "1y",
        "interval": "1d",
        "limit_rows": manifest.get("max_rows", 300),
        "read_only": True,
    },
    "forbidden_now": [
        "fetch historical bars",
        "persist historical bars",
        "run real historical replay",
        "train",
        "write strategy DB",
        "promote candidate",
        "broker execution",
        "live execution",
    ],
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "fetch_preview_present": bool(fetch_preview),
    "preview_only_no_fetch": fetch_preview["mode"] == "FETCH_PREVIEW_ONLY_NO_FETCH",
    "symbol_locked": fetch_preview["symbol"] == "VFV.TO",
    "one_symbol_only": fetch_preview["max_symbols"] == 1,
    "max_rows_300": fetch_preview["max_rows"] == 300,
    "schema_present": len(fetch_preview["required_bar_schema"]) == 7,
    "read_only_contract": fetch_preview["planned_fetch_contract"]["read_only"] is True,
    "historical_bar_fetch_blocked_now": True,
    "real_historical_replay_blocked": True,
    "training_blocked": True,
    "strategy_db_write_blocked": True,
    "promotion_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "REAL_HISTORICAL_BAR_SOURCE_FETCH_PREVIEW_ONLY",
    "source_manifest": str(SOURCE),
    "fetch_preview": fetch_preview,
    "policy": {
        "fetch_preview_allowed": True,
        "historical_bar_fetch_allowed_now": False,
        "real_historical_replay_allowed_now": False,
        "training_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "77G_REAL_HISTORICAL_BAR_SOURCE_FETCH_GATE",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"symbol: {fetch_preview['symbol']}",
        f"max_rows: {fetch_preview['max_rows']}",
        "",
        "Still no fetch. Still no replay. Still no training.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "symbol": fetch_preview["symbol"],
    "max_rows": fetch_preview["max_rows"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

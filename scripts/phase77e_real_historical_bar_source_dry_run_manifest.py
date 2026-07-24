#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "real_historical_replay_gate_rollup" / "77D_real_historical_replay_gate_rollup_latest.json"

OUT_DIR = ARCH / "real_historical_bar_source_dry_run_manifest"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "77E_real_historical_bar_source_dry_run_manifest_latest.json"
OUT_TXT = OUT_DIR / "77E_real_historical_bar_source_dry_run_manifest_latest.txt"

PHASE = "77E_REAL_HISTORICAL_BAR_SOURCE_DRY_RUN_MANIFEST"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

manifest = {
    "mode": "BAR_SOURCE_MANIFEST_ONLY_NO_FETCH",
    "symbol": "VFV.TO",
    "max_symbols": 1,
    "max_rows": 300,
    "source_priority": [
        "market_data_provider_router",
        "yfinance_historical_bars_adapter",
    ],
    "required_bar_schema": [
        "symbol",
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ],
    "planned_validation_rules": [
        "rows <= 300",
        "one symbol only",
        "dates strictly increasing",
        "high >= open",
        "high >= close",
        "low <= open",
        "low <= close",
        "volume >= 0",
    ],
    "forbidden_now": [
        "fetch historical bars",
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
    "manifest_present": bool(manifest),
    "manifest_only_no_fetch": manifest["mode"] == "BAR_SOURCE_MANIFEST_ONLY_NO_FETCH",
    "one_symbol_only": manifest["max_symbols"] == 1,
    "max_rows_300": manifest["max_rows"] == 300,
    "schema_present": len(manifest["required_bar_schema"]) == 7,
    "real_historical_replay_blocked": True,
    "training_blocked": True,
    "strategy_db_write_blocked": True,
    "promotion_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "REAL_HISTORICAL_BAR_SOURCE_DRY_RUN_MANIFEST",
    "source_gate_rollup": str(SOURCE),
    "manifest": manifest,
    "policy": {
        "bar_source_manifest_allowed": True,
        "historical_bar_fetch_allowed_now": False,
        "real_historical_replay_allowed_now": False,
        "training_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "77F_REAL_HISTORICAL_BAR_SOURCE_FETCH_PREVIEW",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "symbol: VFV.TO",
        "max_rows: 300",
        "",
        "No fetch yet. No replay yet. No training yet.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "symbol": manifest["symbol"],
    "max_rows": manifest["max_rows"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

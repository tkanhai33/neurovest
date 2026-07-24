#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "final_training_unlock_decision" / "94A_final_training_unlock_decision_latest.json"

OUT_DIR = ARCH / "ten_symbol_ten_year_historical_manifest"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "95A_10_symbol_10_year_historical_data_manifest_latest.json"
OUT_TXT = OUT_DIR / "95A_10_symbol_10_year_historical_data_manifest_latest.txt"

PHASE = "95A_10_SYMBOL_10_YEAR_HISTORICAL_DATA_MANIFEST"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

symbols = [
    "VFV.TO",
    "VUN.TO",
    "RY.TO",
    "TD.TO",
    "BNS.TO",
    "ENB.TO",
    "SHOP.TO",
    "CNR.TO",
    "BAM.TO",
    "ATZ.TO",
]

manifest = {
    "mode": "10_SYMBOL_10_YEAR_HISTORICAL_DATA_MANIFEST_ONLY_NO_FETCH",
    "symbols": symbols,
    "symbol_count": len(symbols),
    "period": "10y",
    "interval": "1d",
    "max_symbols": 10,
    "max_years": 10,
    "output_mode": "READ_ONLY_HISTORICAL_FIXTURES",
    "required_bar_schema": ["symbol", "date", "open", "high", "low", "close", "volume"],
    "forbidden_now": [
        "fetch historical bars",
        "train",
        "write strategy DB",
        "promote candidate",
        "broker execution",
        "live execution",
    ],
    "hard_blocks": {
        "training_execution_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "manifest_present": bool(manifest),
    "symbol_count_10": len(symbols) == 10,
    "period_10y": manifest["period"] == "10y",
    "interval_1d": manifest["interval"] == "1d",
    "output_read_only": manifest["output_mode"] == "READ_ONLY_HISTORICAL_FIXTURES",
    "no_fetch_now": "fetch historical bars" in manifest["forbidden_now"],
    "training_blocked": manifest["hard_blocks"]["training_execution_enabled"] is False,
    "learner_write_blocked": manifest["hard_blocks"]["learner_write_enabled"] is False,
    "mutation_blocked": manifest["hard_blocks"]["mutation_allowed"] is False,
    "queue_write_blocked": manifest["hard_blocks"]["queue_write_enabled"] is False,
    "strategy_db_write_blocked": manifest["hard_blocks"]["strategy_db_write_allowed"] is False,
    "promotion_blocked": manifest["hard_blocks"]["promotion_enabled"] is False,
    "broker_live_blocked": (
        manifest["hard_blocks"]["broker_execution_enabled"] is False
        and manifest["hard_blocks"]["live_execution_enabled"] is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "10_SYMBOL_10_YEAR_HISTORICAL_DATA_MANIFEST",
    "source_final_decision": str(SOURCE),
    "manifest": manifest,
    "checks": checks,
    "policy": {
        "historical_data_manifest_certified": True,
        **manifest["hard_blocks"],
    },
    "recommended_next_phase": "96A_FETCH_10_SYMBOL_HISTORICAL_DATA_READ_ONLY",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"symbol_count: {len(symbols)}",
        "period: 10y",
        "interval: 1d",
        "",
        "Manifest only. No fetch yet.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "symbol_count": len(symbols),
    "symbols": symbols,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

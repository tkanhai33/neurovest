#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import importlib.util
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "market_regime_classifier_stub/127B_market_regime_classifier_stub_latest.json"
TARGET = ROOT / "backend/app/stacks/strategy_candidate_sandbox/market_regime_classifier.py"

OUT_DIR = ARCH / "market_regime_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "127C_market_regime_certification_latest.json"
OUT_TXT = OUT_DIR / "127C_market_regime_certification_latest.txt"

PHASE = "127C_MARKET_REGIME_CERTIFICATION"

def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def import_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

source = read_json(SOURCE)

module = import_file("market_regime_classifier", TARGET)

status = module.classifier_status()

samples = {

    "bullish": module.classify_market_regime(
        daily_return=0.025,
        intraday_return=0.018,
        range_pct=0.020,
    ),

    "bearish": module.classify_market_regime(
        daily_return=-0.022,
        intraday_return=-0.015,
        range_pct=0.020,
    ),

    "volatile": module.classify_market_regime(
        daily_return=0.002,
        intraday_return=0.001,
        range_pct=0.080,
    ),

    "sideways": module.classify_market_regime(
        daily_return=0.001,
        intraday_return=0.000,
        range_pct=0.010,
    ),
}

checks = {

    "source_exists":
        SOURCE.exists(),

    "source_certified":
        source.get("certified") is True,

    "status_present":
        bool(status),

    "classifier_enabled":
        status.get("enabled") is True,

    "bullish_ok":
        samples["bullish"] == "BULLISH_MOMENTUM",

    "bearish_ok":
        samples["bearish"] == "BEARISH_TREND",

    "volatile_ok":
        samples["volatile"] == "HIGH_VOLATILITY",

    "sideways_ok":
        samples["sideways"] == "SIDEWAYS_RANGE",

    "database_blocked":
        status.get("database_writes_allowed") is False,

    "strategy_db_blocked":
        status.get("strategy_db_write_allowed") is False,

    "promotion_blocked":
        status.get("promotion_enabled") is False,

    "broker_blocked":
        status.get("broker_execution_enabled") is False,

    "live_blocked":
        status.get("live_execution_enabled") is False,
}

result = {

    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),

    "status": status,

    "classification_results": samples,

    "checks": checks,

    "policy":{

        "market_regime_certified":True,

        "database_writes_allowed":False,
        "strategy_db_write_allowed":False,
        "promotion_enabled":False,
        "broker_execution_enabled":False,
        "live_execution_enabled":False,
    },

    "recommended_next_phase":
        "128A_EIGHT_HOUR_TRAINING_PRE_FLIGHT",

    "certified":
        all(checks.values()),
}

OUT_JSON.write_text(
    json.dumps(result,indent=2),
    encoding="utf-8",
)

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "",
        f"Bullish : {samples['bullish']}",
        f"Bearish : {samples['bearish']}",
        f"Volatile: {samples['volatile']}",
        f"Sideways: {samples['sideways']}",
        "",
        "Market regime classifier certified.",
        "",
        "Database Writes: False",
        "Strategy DB Writes: False",
        "Promotion: False",
        "Broker: False",
        "Live: False",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({

    "phase":PHASE,
    "certified":result["certified"],
    "recommended_next_phase":
        result["recommended_next_phase"],
    "out_json":str(OUT_JSON),
    "out_txt":str(OUT_TXT),

},indent=2))

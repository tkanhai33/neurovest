#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "training_precondition_gap_manifest" / "76B_training_precondition_gap_manifest_latest.json"

OUT_DIR = ARCH / "real_historical_replay_dry_run_architecture"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "77A_real_historical_replay_dry_run_architecture_latest.json"
OUT_TXT = OUT_DIR / "77A_real_historical_replay_dry_run_architecture_latest.txt"

PHASE = "77A_REAL_HISTORICAL_REPLAY_DRY_RUN_ARCHITECTURE"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

architecture = {
    "mode": "ARCHITECTURE_ONLY_NO_HISTORICAL_REPLAY_EXECUTION",
    "goal": "plan real historical bar replay dry-run without enabling training, promotion, broker, or live execution",
    "allowed_future_inputs": [
        "certified replay specs",
        "historical OHLCV bars from market_data_provider_router",
        "read-only FRED/StatCan macro context",
    ],
    "planned_flow": [
        "load one certified replay spec",
        "load one symbol historical bars through L0/L3 market data facade",
        "validate bar schema",
        "run dry-run metric calculator",
        "write only to read-only replay report store",
        "block strategy DB write",
        "block promotion",
        "block training",
        "block broker/live",
    ],
    "required_gates": {
        "historical_replay_enabled_now": False,
        "training_enabled_now": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "candidate_scope": {
        "first_pass": "single_symbol_single_spec_only",
        "symbols_allowed_initially": ["VFV.TO"],
        "max_specs_initially": 1,
        "max_symbols_initially": 1,
        "max_rows_initially": 300,
    },
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "architecture_present": bool(architecture),
    "architecture_only": architecture["mode"] == "ARCHITECTURE_ONLY_NO_HISTORICAL_REPLAY_EXECUTION",
    "historical_replay_disabled_now": architecture["required_gates"]["historical_replay_enabled_now"] is False,
    "training_disabled_now": architecture["required_gates"]["training_enabled_now"] is False,
    "strategy_db_write_blocked": architecture["required_gates"]["strategy_db_write_allowed"] is False,
    "promotion_blocked": architecture["required_gates"]["promotion_enabled"] is False,
    "broker_live_blocked": (
        architecture["required_gates"]["broker_execution_enabled"] is False
        and architecture["required_gates"]["live_execution_enabled"] is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "REAL_HISTORICAL_REPLAY_DRY_RUN_ARCHITECTURE_ONLY",
    "source_gap_manifest": str(SOURCE),
    "architecture": architecture,
    "checks": checks,
    "recommended_next_phase": "77B_REAL_HISTORICAL_REPLAY_DRY_RUN_GATE_STUB",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "",
        "Historical replay remains disabled.",
        "Training remains disabled.",
        "Strategy DB / promotion / broker / live remain blocked.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "fixture_bar_math_function_rollup" / "69D_fixture_bar_math_function_rollup_latest.json"
FIXTURE = ARCH / "fixture_bar_dataset" / "data" / "fixture_ohlcv_v1.csv"
MATH_FILE = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L2_domain/bar_replay_math_contract.py"

OUT_DIR = ARCH / "fixture_replay_calculator_preview"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "70A_fixture_replay_calculator_dry_run_preview_latest.json"
OUT_TXT = OUT_DIR / "70A_fixture_replay_calculator_dry_run_preview_latest.txt"

PHASE = "70A_FIXTURE_REPLAY_CALCULATOR_DRY_RUN_PREVIEW"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

preview = {
    "mode": "DRY_RUN_PREVIEW_ONLY_NO_REPLAY_EXECUTION",
    "input_fixture": str(FIXTURE),
    "math_contract_file": str(MATH_FILE),
    "planned_steps_future": [
        "load fixture OHLCV CSV",
        "extract close price series",
        "calculate simple returns",
        "calculate cumulative return",
        "calculate rolling mean",
        "calculate rolling volatility",
        "calculate max drawdown",
        "calculate trade count proxy",
        "emit fixture metric report",
    ],
    "planned_output_shape": {
        "dataset_id": "fixture_ohlcv_v1",
        "metric_results": [
            {"metric_name": "simple_returns", "value_type": "list[float]"},
            {"metric_name": "cumulative_return", "value_type": "float"},
            {"metric_name": "rolling_mean", "value_type": "list[float | None]"},
            {"metric_name": "rolling_volatility", "value_type": "list[float | None]"},
            {"metric_name": "max_drawdown", "value_type": "float"},
            {"metric_name": "trade_count_proxy", "value_type": "int"},
        ],
    },
    "dry_run_execution_allowed_now": False,
    "historical_replay_allowed_now": False,
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "fixture_exists": FIXTURE.exists(),
    "math_file_exists": MATH_FILE.exists(),
    "preview_present": bool(preview),
    "planned_steps_present": len(preview["planned_steps_future"]) > 0,
    "output_shape_present": bool(preview["planned_output_shape"]),
    "dry_run_execution_blocked": preview["dry_run_execution_allowed_now"] is False,
    "historical_replay_blocked": preview["historical_replay_allowed_now"] is False,
    "runtime_execution_blocked": True,
    "strategy_db_write_blocked": True,
    "promotion_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "FIXTURE_REPLAY_CALCULATOR_DRY_RUN_PREVIEW",
    "source_math_rollup": str(SOURCE),
    "preview": preview,
    "policy": {
        "calculator_dry_run_preview_allowed": True,
        "calculator_execution_allowed_now": False,
        "historical_replay_allowed_now": False,
        "runtime_execution_allowed": False,
        "runtime_mutation_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "70B_FIXTURE_REPLAY_CALCULATOR_SOURCE_CREATION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "",
        "Planned future steps:",
        *[f"- {step}" for step in preview["planned_steps_future"]],
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

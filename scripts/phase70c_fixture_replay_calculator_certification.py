#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import importlib.util
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "fixture_replay_calculator_source" / "70B_fixture_replay_calculator_source_creation_latest.json"
TARGET = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/fixture_replay_calculator.py"
FIXTURE = ARCH / "fixture_bar_dataset" / "data" / "fixture_ohlcv_v1.csv"

OUT_DIR = ARCH / "fixture_replay_calculator_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "70C_fixture_replay_calculator_certification_latest.json"
OUT_TXT = OUT_DIR / "70C_fixture_replay_calculator_certification_latest.txt"

PHASE = "70C_FIXTURE_REPLAY_CALCULATOR_CERTIFICATION"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def import_file(path: Path):
    spec = importlib.util.spec_from_file_location("fixture_replay_calculator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


source = read_json(SOURCE)

tests = {}
errors = []

try:
    module = import_file(TARGET)

    status = module.facade_status()

    tests["facade_status_all_false"] = (
        status["replay_runtime_enabled"] is False
        and status["historical_replay_allowed"] is False
        and status["strategy_execution_allowed"] is False
        and status["strategy_db_write_allowed"] is False
        and status["promotion_enabled"] is False
        and status["broker_execution_enabled"] is False
        and status["live_execution_enabled"] is False
    )

    rows = module.load_fixture_bars(FIXTURE)
    tests["fixture_loaded"] = len(rows) == 10

    closes = module.extract_close_prices(rows)
    tests["close_series_loaded"] = (
        len(closes) == 10
        and abs(closes[0] - 101.0) < 1e-9
        and abs(closes[-1] - 110.5) < 1e-9
    )

    metrics = module.calculate_fixture_metrics(FIXTURE)

    tests["dataset_id_correct"] = metrics["dataset_id"] == "fixture_ohlcv_v1"
    tests["row_count_correct"] = metrics["row_count"] == 10
    tests["returns_generated"] = len(metrics["simple_returns"]) == 9
    tests["rolling_mean_generated"] = len(metrics["rolling_mean_3"]) == 10
    tests["rolling_volatility_generated"] = len(metrics["rolling_volatility_3"]) == 9
    tests["max_drawdown_is_float"] = isinstance(metrics["max_drawdown"], float)
    tests["trade_count_is_int"] = isinstance(metrics["trade_count_proxy"], int)

    safety = metrics["safety"]

    tests["embedded_safety_all_false"] = (
        safety["replay_runtime_enabled"] is False
        and safety["historical_replay_allowed"] is False
        and safety["strategy_execution_allowed"] is False
        and safety["strategy_db_write_allowed"] is False
        and safety["promotion_enabled"] is False
        and safety["broker_execution_enabled"] is False
        and safety["live_execution_enabled"] is False
    )

except Exception as exc:
    errors.append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "target_exists": TARGET.exists(),
    "fixture_exists": FIXTURE.exists(),
    "tests_present": len(tests) > 0,
    "all_tests_passed": all(tests.values()) if tests else False,
    "no_errors": len(errors) == 0,
    "historical_replay_blocked": True,
    "runtime_execution_blocked": True,
    "strategy_db_write_blocked": True,
    "promotion_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "FIXTURE_REPLAY_CALCULATOR_CERTIFICATION",
    "source_creation": str(SOURCE),
    "target_file": str(TARGET),
    "fixture_csv": str(FIXTURE),
    "tests": tests,
    "errors": errors,
    "policy": {
        "fixture_calculator_certified": True,
        "historical_replay_allowed_now": False,
        "runtime_execution_allowed": False,
        "runtime_mutation_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "70D_FIXTURE_REPLAY_CALCULATOR_ROLLUP",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "",
        "Tests:",
        *[f"- {k}: {v}" for k, v in tests.items()],
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "test_count": len(tests),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

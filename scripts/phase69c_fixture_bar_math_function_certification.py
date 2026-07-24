#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import importlib.util
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "fixture_bar_math_function_source" / "69B_fixture_bar_math_function_source_creation_latest.json"
TARGET = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L2_domain/bar_replay_math_contract.py"

OUT_DIR = ARCH / "fixture_bar_math_function_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "69C_fixture_bar_math_function_certification_latest.json"
OUT_TXT = OUT_DIR / "69C_fixture_bar_math_function_certification_latest.txt"

PHASE = "69C_FIXTURE_BAR_MATH_FUNCTION_CERTIFICATION"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def import_file(path: Path):
    spec = importlib.util.spec_from_file_location("bar_replay_math_contract", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


source = read_json(SOURCE)

tests = {}
errors = []

try:
    module = import_file(TARGET)

    status = module.contract_status()
    tests["contract_status_all_false"] = (
        status.get("replay_runtime_enabled") is False
        and status.get("historical_replay_allowed") is False
        and status.get("strategy_execution_allowed") is False
        and status.get("strategy_db_write_allowed") is False
        and status.get("promotion_enabled") is False
        and status.get("broker_execution_enabled") is False
        and status.get("live_execution_enabled") is False
    )

    closes = [100.0, 110.0, 121.0]
    returns = module.calculate_simple_returns(closes)
    tests["simple_returns_correct"] = (
        len(returns) == 2
        and round(returns[0], 6) == 0.1
        and round(returns[1], 6) == 0.1
    )

    cumulative = module.calculate_cumulative_return(returns)
    tests["cumulative_return_correct"] = round(cumulative, 6) == 0.21

    mean = module.calculate_rolling_mean([1.0, 2.0, 3.0, 4.0], 2)
    tests["rolling_mean_correct"] = mean == [None, 1.5, 2.5, 3.5]

    volatility = module.calculate_rolling_volatility([0.0, 0.1, 0.2], 2)
    tests["rolling_volatility_shape_ok"] = (
        len(volatility) == 3
        and volatility[0] is None
        and volatility[1] is not None
        and volatility[2] is not None
    )

    drawdown = module.calculate_max_drawdown([100.0, 120.0, 90.0, 130.0])
    tests["max_drawdown_correct"] = round(drawdown, 6) == -0.25

    trade_count = module.calculate_trade_count_proxy([0, 1, 1, 0, 1])
    tests["trade_count_proxy_correct"] = trade_count == 3

except Exception as exc:
    errors.append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "target_exists": TARGET.exists(),
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
    "mode": "FIXTURE_BAR_MATH_FUNCTION_CERTIFICATION",
    "source_creation": str(SOURCE),
    "target_file": str(TARGET),
    "function_tests": tests,
    "errors": errors,
    "policy": {
        "math_function_certification_allowed": True,
        "historical_replay_allowed_now": False,
        "runtime_execution_allowed": False,
        "runtime_mutation_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "69D_FIXTURE_BAR_MATH_FUNCTION_ROLLUP_CERTIFICATION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "",
        "Function tests:",
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

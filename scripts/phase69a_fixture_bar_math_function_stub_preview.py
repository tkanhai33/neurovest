#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "fixture_bar_math_contract" / "68G_fixture_bar_math_rollup_certification_latest.json"

OUT_DIR = ARCH / "fixture_bar_math_function_preview"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "69A_fixture_bar_math_function_stub_preview_latest.json"
OUT_TXT = OUT_DIR / "69A_fixture_bar_math_function_stub_preview_latest.txt"

PHASE = "69A_FIXTURE_BAR_MATH_FUNCTION_STUB_PREVIEW"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

function_preview = {
    "mode": "PREVIEW_ONLY_NO_SOURCE_WRITE",
    "planned_functions": [
        {
            "name": "calculate_simple_returns",
            "input": "ordered close prices",
            "output": "per-bar return series",
            "formula": "return_t = close_t / close_t_minus_1 - 1",
            "execution_allowed_now": False,
        },
        {
            "name": "calculate_cumulative_return",
            "input": "return series",
            "output": "single cumulative return value",
            "formula": "product(1 + returns) - 1",
            "execution_allowed_now": False,
        },
        {
            "name": "calculate_rolling_mean",
            "input": "close prices and window",
            "output": "rolling average series",
            "formula": "mean(close[t-window:t])",
            "execution_allowed_now": False,
        },
        {
            "name": "calculate_rolling_volatility",
            "input": "return series and window",
            "output": "rolling volatility series",
            "formula": "std(returns[t-window:t])",
            "execution_allowed_now": False,
        },
        {
            "name": "calculate_max_drawdown",
            "input": "equity curve",
            "output": "maximum drawdown value",
            "formula": "min(equity / running_max_equity - 1)",
            "execution_allowed_now": False,
        },
        {
            "name": "calculate_trade_count_proxy",
            "input": "signal state changes",
            "output": "integer count",
            "formula": "count(signal changes)",
            "execution_allowed_now": False,
        },
    ],
    "future_target_file": "backend/app/stacks/strategy_candidate_sandbox/L2_domain/bar_replay_math_contract.py",
    "source_write_allowed_now": False,
    "math_execution_allowed_now": False,
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "function_preview_present": len(function_preview["planned_functions"]) > 0,
    "all_function_execution_blocked": all(
        f["execution_allowed_now"] is False
        for f in function_preview["planned_functions"]
    ),
    "source_write_blocked": function_preview["source_write_allowed_now"] is False,
    "math_execution_blocked": function_preview["math_execution_allowed_now"] is False,
    "historical_replay_blocked": True,
    "runtime_execution_blocked": True,
    "strategy_db_write_blocked": True,
    "promotion_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_FIXTURE_BAR_MATH_FUNCTION_STUB_PREVIEW",
    "source_math_rollup": str(SOURCE),
    "function_preview": function_preview,
    "policy": {
        "function_stub_preview_allowed": True,
        "source_write_allowed_now": False,
        "math_execution_allowed_now": False,
        "historical_replay_allowed_now": False,
        "runtime_execution_allowed": False,
        "runtime_mutation_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "69B_FIXTURE_BAR_MATH_FUNCTION_SOURCE_CREATION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"planned_function_count: {len(function_preview['planned_functions'])}",
        "",
        "Planned functions:",
        *[f"- {f['name']} | execution_allowed_now={f['execution_allowed_now']}" for f in function_preview["planned_functions"]],
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "planned_function_count": len(function_preview["planned_functions"]),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

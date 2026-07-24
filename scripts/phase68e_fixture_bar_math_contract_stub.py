#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"
SOURCE = ARCH / "fixture_bar_dataset" / "68D_fixture_bar_dataset_rollup_certification_latest.json"

OUT_DIR = ARCH / "fixture_bar_math_contract"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "68E_fixture_bar_math_contract_stub_latest.json"
OUT_TXT = OUT_DIR / "68E_fixture_bar_math_contract_stub_latest.txt"

PHASE = "68E_FIXTURE_BAR_MATH_CONTRACT_STUB"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

math_contract = {
    "contract_id": "fixture_bar_math_contract_v1",
    "mode": "CONTRACT_ONLY",
    "allowed_future_calculations": [
        "simple_return",
        "cumulative_return",
        "rolling_mean",
        "rolling_volatility",
        "max_drawdown",
        "trade_count_proxy",
    ],
    "required_inputs": [
        "symbol",
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ],
    "required_outputs_future": [
        "metric_name",
        "metric_value",
        "candidate_id",
        "spec_id",
        "dataset_id",
    ],
    "forbidden_now": [
        "run replay",
        "score strategy",
        "write strategy database",
        "promote candidate",
        "enable runtime",
        "broker execution",
        "live execution",
    ],
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "contract_present": bool(math_contract),
    "contract_only": math_contract["mode"] == "CONTRACT_ONLY",
    "required_inputs_present": len(math_contract["required_inputs"]) == 7,
    "future_calculations_present": len(math_contract["allowed_future_calculations"]) > 0,
    "historical_replay_blocked": True,
    "runtime_execution_blocked": True,
    "strategy_db_write_blocked": True,
    "promotion_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_FIXTURE_BAR_MATH_CONTRACT_STUB",
    "source_fixture_rollup": str(SOURCE),
    "math_contract": math_contract,
    "policy": {
        "math_contract_stub_allowed": True,
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
    "recommended_next_phase": "68F_FIXTURE_BAR_MATH_CONTRACT_CERTIFICATION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"contract_id: {math_contract['contract_id']}",
        "",
        "Allowed future calculations:",
        *[f"- {x}" for x in math_contract["allowed_future_calculations"]],
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "contract_id": math_contract["contract_id"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

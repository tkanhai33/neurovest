#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "fixture_bar_math_contract" / "68E_fixture_bar_math_contract_stub_latest.json"

OUT_DIR = ARCH / "fixture_bar_math_contract"
OUT_JSON = OUT_DIR / "68F_fixture_bar_math_contract_certification_latest.json"
OUT_TXT = OUT_DIR / "68F_fixture_bar_math_contract_certification_latest.txt"

PHASE = "68F_FIXTURE_BAR_MATH_CONTRACT_CERTIFICATION"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)
contract = source.get("math_contract", {})

required_calcs = {
    "simple_return",
    "cumulative_return",
    "rolling_mean",
    "rolling_volatility",
    "max_drawdown",
    "trade_count_proxy",
}

required_inputs = {
    "symbol",
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume",
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "contract_present": bool(contract),
    "contract_only": contract.get("mode") == "CONTRACT_ONLY",
    "required_calculations_present": required_calcs.issubset(set(contract.get("allowed_future_calculations", []))),
    "required_inputs_present": required_inputs.issubset(set(contract.get("required_inputs", []))),
    "math_execution_blocked": source.get("policy", {}).get("math_execution_allowed_now") is False,
    "historical_replay_blocked": source.get("policy", {}).get("historical_replay_allowed_now") is False,
    "runtime_execution_blocked": source.get("policy", {}).get("runtime_execution_allowed") is False,
    "strategy_db_write_blocked": source.get("policy", {}).get("strategy_db_write_allowed") is False,
    "promotion_blocked": source.get("policy", {}).get("promotion_enabled") is False,
    "broker_live_blocked": (
        source.get("policy", {}).get("broker_execution_enabled") is False
        and source.get("policy", {}).get("live_execution_enabled") is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "FIXTURE_BAR_MATH_CONTRACT_CERTIFICATION",
    "source_contract": str(SOURCE),
    "contract_id": contract.get("contract_id"),
    "checks": checks,
    "policy": {
        "fixture_bar_math_contract_certified": True,
        "math_execution_allowed_now": False,
        "historical_replay_allowed_now": False,
        "runtime_execution_allowed": False,
        "runtime_mutation_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "68G_FIXTURE_BAR_MATH_ROLLUP_CERTIFICATION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"contract_id: {result['contract_id']}",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "contract_id": result["contract_id"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

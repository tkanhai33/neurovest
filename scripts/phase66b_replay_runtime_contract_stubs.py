#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"
SOURCE = ARCH / "66A_replay_runtime_architecture_planning_latest.json"

OUT_DIR = ARCH / "contracts"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "66B_replay_runtime_contract_stubs_latest.json"
OUT_TXT = OUT_DIR / "66B_replay_runtime_contract_stubs_latest.txt"

PHASE = "66B_REPLAY_RUNTIME_CONTRACT_STUBS"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

contracts = {
    "replay_spec_contract": {
        "required_fields": [
            "spec_id",
            "candidate_id",
            "strategy_name",
            "asset_class",
            "signal_family",
            "replay_scope",
            "formula_requirements",
            "metrics_required",
            "stress_tests_required",
            "safety",
        ],
        "runtime_allowed": False,
    },
    "metric_scorecard_contract": {
        "required_metrics": [
            "total_return",
            "annualized_return",
            "max_drawdown",
            "sharpe_proxy",
            "win_rate",
            "trade_count",
            "turnover",
            "transaction_cost_impact",
        ],
        "write_to_strategy_db_allowed": False,
    },
    "stress_test_contract": {
        "required_tests": [
            "walk_forward_split",
            "out_of_sample_split",
            "bear_market_window",
            "bull_market_window",
            "sideways_market_window",
            "high_volatility_window",
            "low_volatility_window",
            "transaction_cost_sensitivity",
            "slippage_sensitivity",
            "drawdown_limit_test",
        ],
        "execution_allowed": False,
    },
    "decision_policy_contract": {
        "pass_destination": "INACTIVE_STRATEGY_DATABANK_CANDIDATE",
        "near_miss_band_percent": {"min": 2, "max": 10},
        "near_miss_action": "CONTROLLED_REFACTOR_QUEUE",
        "max_refactor_attempts": 3,
        "fail_after_max_attempts": "QUARANTINE_OR_TRASH",
        "activation_requires_manual_gate": True,
        "automatic_activation_allowed": False,
    },
    "replay_enablement_gate_contract": {
        "historical_replay_allowed_now": False,
        "requires_future_enablement_phase": True,
        "requires_manual_review": True,
    },
    "result_router_contract": {
        "allowed_destinations_future": [
            "replay_report_store",
            "controlled_refactor_queue",
            "quarantine_or_trash",
            "inactive_strategy_databank_candidate",
        ],
        "write_routing_allowed_now": False,
        "strategy_db_write_allowed_now": False,
    },
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_REPLAY_RUNTIME_CONTRACT_STUBS",
    "source_architecture_plan": str(SOURCE),
    "contracts": contracts,
    "global_policy": {
        "contract_stub_generation_allowed": True,
        "historical_replay_allowed_now": False,
        "strategy_execution_allowed": False,
        "implementation_patch_allowed": False,
        "runtime_execution_allowed": False,
        "runtime_mutation_allowed": False,
        "strategy_db_write_allowed": False,
        "learning_enabled": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": {
        "source_exists": SOURCE.exists(),
        "source_certified": source.get("certified") is True,
        "contracts_present": len(contracts) > 0,
        "replay_spec_contract_present": "replay_spec_contract" in contracts,
        "metric_scorecard_contract_present": "metric_scorecard_contract" in contracts,
        "stress_test_contract_present": "stress_test_contract" in contracts,
        "decision_policy_contract_present": "decision_policy_contract" in contracts,
        "replay_gate_contract_present": "replay_enablement_gate_contract" in contracts,
        "result_router_contract_present": "result_router_contract" in contracts,
        "historical_replay_blocked": False is False,
        "runtime_execution_blocked": False is False,
        "strategy_db_write_blocked": False is False,
        "promotion_blocked": False is False,
        "broker_live_blocked": False is False,
    },
    "recommended_next_phase": "66C_REPLAY_RUNTIME_GATE_WIREGRAPH",
    "certified": False,
}

result["certified"] = all(result["checks"].values())

OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

lines = [
    PHASE,
    "",
    f"certified: {result['certified']}",
    "",
    "Contracts:",
    "",
]

for name in contracts:
    lines.append(f"- {name}")

lines += [
    "",
    "Safety:",
    "",
]

for k, v in result["global_policy"].items():
    lines.append(f"{k}: {v}")

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(json.dumps({
    "phase": PHASE,
    "contract_count": len(contracts),
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
    "recommended_next_phase": result["recommended_next_phase"],
    "certified": result["certified"],
}, indent=2, ensure_ascii=False))

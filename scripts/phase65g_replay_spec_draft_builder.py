#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
BASE = ROOT / "runtime" / "research_library" / "strategy_sources" / "151_trading_strategies"

FORMULAS = BASE / "formula_signal_requirements"
SPECS = BASE / "replay_specs"

SOURCE = FORMULAS / "65F_formula_and_signal_requirement_extractor_latest.json"

OUT_JSON = SPECS / "65G_replay_spec_draft_builder_latest.json"
OUT_TXT = SPECS / "65G_replay_spec_draft_builder_latest.txt"

PHASE = "65G_REPLAY_SPEC_DRAFT_BUILDER"

SPECS.mkdir(parents=True, exist_ok=True)


def default_symbols(asset_class: str) -> list[str]:
    if asset_class == "stocks":
        return ["RY.TO", "TD.TO", "SHOP.TO", "CNR.TO", "ATZ.TO"]
    if asset_class == "etf":
        return ["VFV.TO", "VUN.TO", "QQC.TO"]
    if asset_class == "indexes":
        return ["^GSPTSE", "^GSPC", "^IXIC"]
    if asset_class == "commodities":
        return ["GC=F", "CL=F"]
    if asset_class == "futures":
        return ["ES=F", "NQ=F"]
    if asset_class == "foreign_exchange":
        return ["CADUSD=X", "USDCAD=X"]
    if asset_class == "cryptocurrencies":
        return ["BTC-CAD", "ETH-CAD"]
    if asset_class == "global_macro":
        return ["VFV.TO", "VUN.TO", "XBB.TO"]
    return ["VFV.TO", "VUN.TO"]


def metrics_for_family(family: str) -> list[str]:
    base = [
        "total_return",
        "annualized_return",
        "max_drawdown",
        "sharpe_proxy",
        "win_rate",
        "trade_count",
        "turnover",
        "transaction_cost_impact",
    ]

    if family in {"momentum", "trend_following"}:
        base += ["trend_capture_ratio", "whipsaw_rate"]
    elif family == "mean_reversion":
        base += ["mean_reversion_hit_rate", "average_reversion_time"]
    elif family == "value_factor":
        base += ["factor_spread_return", "rank_stability"]
    elif family == "volatility":
        base += ["volatility_regime_sensitivity", "tail_loss_proxy"]
    elif family in {"arbitrage", "statistical_arbitrage"}:
        base += ["spread_convergence_rate", "spread_breakdown_rate"]
    elif family == "carry":
        base += ["carry_return_component", "rate_sensitivity"]

    return sorted(set(base))


def stress_tests(record: dict) -> list[str]:
    tests = [
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
    ]

    family = record.get("signal_family")

    if family in {"momentum", "trend_following"}:
        tests += ["trend_break_test", "false_breakout_test"]
    if family == "mean_reversion":
        tests += ["regime_shift_failure_test", "persistent_trend_against_signal_test"]
    if family in {"arbitrage", "statistical_arbitrage"}:
        tests += ["spread_widening_test", "correlation_break_test"]
    if family == "carry":
        tests += ["rate_shock_test", "currency_shock_test"]

    return sorted(set(tests))


source = json.loads(SOURCE.read_text(encoding="utf-8")) if SOURCE.exists() else {}
records = source.get("records", [])

specs = []

for record in records:
    spec_id = f"REPLAY_SPEC_{record['candidate_id']}"

    spec = {
        "spec_id": spec_id,
        "candidate_id": record.get("candidate_id"),
        "strategy_name": record.get("strategy_name"),
        "source_page": record.get("source_page"),
        "asset_class": record.get("asset_class"),
        "signal_family": record.get("signal_family"),

        "replay_scope": {
            "mode": "DRAFT_ONLY",
            "historical_replay_allowed_now": False,
            "default_period": "10y",
            "default_interval": "1d",
            "minimum_candles": 200,
            "symbols": default_symbols(record.get("asset_class")),
            "data_sources": [
                "yfinance_historical_bars",
                "market_data_provider_router",
            ],
        },

        "formula_requirements": record.get("formula_requirements", []),
        "indicator_requirements": record.get("indicator_requirements", []),
        "market_data_requirements": record.get("market_data_requirements", []),

        "metrics_required": metrics_for_family(record.get("signal_family")),
        "stress_tests_required": stress_tests(record),

        "decision_policy_preview": {
            "pass_destination": "INACTIVE_STRATEGY_DATABANK_CANDIDATE",
            "near_miss_band_percent": {
                "min": 2,
                "max": 10,
            },
            "near_miss_action": "CONTROLLED_REFACTOR_QUEUE",
            "max_refactor_attempts": 3,
            "fail_after_max_attempts": "QUARANTINE_OR_TRASH",
            "activation_requires_manual_gate": True,
        },

        "safety": {
            "draft_only": True,
            "historical_replay_allowed_now": False,
            "strategy_execution_allowed": False,
            "implementation_patch_allowed": False,
            "runtime_execution_allowed": False,
            "runtime_mutation_allowed": False,
            "learning_enabled": False,
            "promotion_enabled": False,
            "broker_execution_enabled": False,
            "live_execution_enabled": False,
        },
    }

    (SPECS / f"{spec_id}.json").write_text(
        json.dumps(spec, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    specs.append(spec)

summary = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_REPLAY_SPEC_DRAFT_BUILDER",
    "source_formula_requirements": str(SOURCE),
    "input_record_count": len(records),
    "replay_spec_count": len(specs),
    "spec_files": [
        f"{spec['spec_id']}.json"
        for spec in specs
    ],
    "global_policy": {
        "replay_spec_draft_allowed": True,
        "historical_replay_allowed_now": False,
        "strategy_execution_allowed": False,
        "implementation_patch_allowed": False,
        "runtime_execution_allowed": False,
        "runtime_mutation_allowed": False,
        "learning_enabled": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": {
        "source_exists": SOURCE.exists(),
        "source_certified": source.get("certified") is True,
        "records_present": len(records) > 0,
        "specs_created_for_all_records": len(specs) == len(records) and len(specs) > 0,
        "all_specs_draft_only": all(spec["safety"]["draft_only"] is True for spec in specs),
        "all_replay_disabled_now": all(spec["safety"]["historical_replay_allowed_now"] is False for spec in specs),
        "all_execution_blocked": all(spec["safety"]["strategy_execution_allowed"] is False for spec in specs),
        "all_promotion_blocked": all(spec["safety"]["promotion_enabled"] is False for spec in specs),
        "all_broker_live_blocked": all(
            spec["safety"]["broker_execution_enabled"] is False
            and spec["safety"]["live_execution_enabled"] is False
            for spec in specs
        ),
    },
    "recommended_next_phase": "65H_REPLAY_SPEC_ROLLUP_CERTIFICATION",
    "certified": False,
}

summary["certified"] = all(summary["checks"].values())

OUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

lines = [
    PHASE,
    "",
    f"certified: {summary['certified']}",
    f"replay_spec_count: {summary['replay_spec_count']}",
    "",
    "Replay Specs:",
    "",
]

for spec in specs:
    lines.append(
        f"- {spec['spec_id']} | {spec['strategy_name']} | "
        f"{spec['signal_family']} | {','.join(spec['replay_scope']['symbols'])}"
    )

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(json.dumps({
    "phase": PHASE,
    "replay_spec_count": len(specs),
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
    "recommended_next_phase": summary["recommended_next_phase"],
    "certified": summary["certified"],
}, indent=2, ensure_ascii=False))

#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
from collections import Counter
import json

ROOT = Path(".").resolve()
BASE = ROOT / "runtime" / "research_library" / "strategy_sources" / "151_trading_strategies"

PLANS = BASE / "replay_plans"
CANDIDATES = BASE / "candidates"
FORMULAS = BASE / "formula_signal_requirements"

SOURCE = PLANS / "65E_historical_replay_matching_plan_latest.json"

OUT_JSON = FORMULAS / "65F_formula_and_signal_requirement_extractor_latest.json"
OUT_TXT = FORMULAS / "65F_formula_and_signal_requirement_extractor_latest.txt"

PHASE = "65F_FORMULA_AND_SIGNAL_REQUIREMENT_EXTRACTOR"

FORMULAS.mkdir(parents=True, exist_ok=True)


def formula_needs(strategy_name: str, indicators: list[str], data_req: list[str]) -> list[str]:
    low = strategy_name.lower()
    needs = []

    if "momentum" in low or "momentum" in indicators:
        needs += ["return_window", "ranking_score", "lookback_period"]
    if "moving average" in low or "moving_average" in indicators:
        needs += ["short_ma", "long_ma", "ma_crossover_rule"]
    if "mean-reversion" in low or "mean_reversion" in indicators or "contrarian" in low:
        needs += ["z_score", "rolling_mean", "rolling_std", "reversion_threshold"]
    if "value" in low or "value_factor" in indicators:
        needs += ["valuation_metric", "relative_rank"]
    if "volatility" in low or "volatility" in indicators:
        needs += ["rolling_volatility", "volatility_rank"]
    if "pairs" in low or "pair_spread" in indicators:
        needs += ["spread", "hedge_ratio", "cointegration_or_correlation_check"]
    if "arbitrage" in low or "arbitrage_spread" in indicators:
        needs += ["spread_measure", "fair_value_model", "transaction_cost_buffer"]
    if "trend following" in low or "trend_following" in indicators:
        needs += ["trend_filter", "breakout_or_ma_signal"]

    if not needs and "historical_price_bars" in data_req:
        needs += ["price_return", "lookback_period", "signal_threshold"]

    return sorted(set(needs))


def signal_family(strategy_name: str, indicators: list[str]) -> str:
    low = strategy_name.lower()

    if "momentum" in low:
        return "momentum"
    if "moving average" in low or "trend following" in low:
        return "trend_following"
    if "mean-reversion" in low or "contrarian" in low:
        return "mean_reversion"
    if "value" in low:
        return "value_factor"
    if "volatility" in low:
        return "volatility"
    if "pairs" in low:
        return "statistical_arbitrage"
    if "arbitrage" in low:
        return "arbitrage"
    if indicators:
        return indicators[0]
    return "generic_price_signal"


def replay_spec_readiness(plan: dict, needs: list[str]) -> str:
    if plan.get("replay_feasibility") != "REPLAY_PLANNABLE_WITH_HISTORICAL_BARS":
        return "NOT_READY_NON_BAR_OR_PARTIAL"
    if not needs:
        return "NEEDS_MANUAL_FORMULA_REVIEW"
    return "READY_FOR_REPLAY_SPEC_DRAFT"


source = json.loads(SOURCE.read_text(encoding="utf-8")) if SOURCE.exists() else {}
plans = source.get("plans", [])

records = []
family_counter = Counter()
readiness_counter = Counter()
need_counter = Counter()

for plan in plans:
    if plan.get("replay_feasibility") != "REPLAY_PLANNABLE_WITH_HISTORICAL_BARS":
        continue

    strategy_name = plan.get("strategy_name", "")
    indicators = plan.get("indicator_requirements", [])
    data_req = plan.get("market_data_requirements", [])

    needs = formula_needs(strategy_name, indicators, data_req)
    family = signal_family(strategy_name, indicators)
    readiness = replay_spec_readiness(plan, needs)

    family_counter[family] += 1
    readiness_counter[readiness] += 1
    need_counter.update(needs)

    record = {
        "candidate_id": plan.get("candidate_id"),
        "strategy_name": strategy_name,
        "asset_class": plan.get("asset_class"),
        "source_page": plan.get("source_page"),
        "signal_family": family,
        "indicator_requirements": indicators,
        "market_data_requirements": data_req,
        "formula_requirements": needs,
        "minimum_replay_inputs": sorted(set([
            "symbol",
            "date",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ] + data_req)),
        "required_tests": plan.get("required_tests", []),
        "replay_spec_readiness": readiness,
        "manual_review_required": True,
        "safety": {
            "formula_extraction_only": True,
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

    records.append(record)

summary = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_FORMULA_AND_SIGNAL_REQUIREMENT_EXTRACTION",
    "source_plan": str(SOURCE),
    "input_plan_count": len(plans),
    "bar_replay_candidate_count": len(records),
    "signal_family_counts": dict(family_counter),
    "readiness_counts": dict(readiness_counter),
    "formula_requirement_counts": dict(need_counter),
    "records": records,
    "global_policy": {
        "formula_extraction_allowed": True,
        "signal_requirement_mapping_allowed": True,
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
        "source_plan_exists": SOURCE.exists(),
        "source_plan_certified": source.get("certified") is True,
        "records_created": len(records) > 0,
        "only_bar_replay_candidates_processed": all(
            r["replay_spec_readiness"] in {
                "READY_FOR_REPLAY_SPEC_DRAFT",
                "NEEDS_MANUAL_FORMULA_REVIEW",
            }
            for r in records
        ),
        "all_manual_review_required": all(r["manual_review_required"] is True for r in records),
        "all_replay_disabled_now": all(r["safety"]["historical_replay_allowed_now"] is False for r in records),
        "all_execution_blocked": all(r["safety"]["strategy_execution_allowed"] is False for r in records),
        "all_promotion_blocked": all(r["safety"]["promotion_enabled"] is False for r in records),
        "all_broker_live_blocked": all(
            r["safety"]["broker_execution_enabled"] is False
            and r["safety"]["live_execution_enabled"] is False
            for r in records
        ),
    },
    "recommended_next_phase": "65G_REPLAY_SPEC_DRAFT_BUILDER",
    "certified": False,
}

summary["certified"] = all(summary["checks"].values())

OUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

lines = [
    PHASE,
    "",
    f"certified: {summary['certified']}",
    f"bar_replay_candidate_count: {len(records)}",
    "",
    "Signal Family Counts:",
]

for key, value in summary["signal_family_counts"].items():
    lines.append(f"- {key}: {value}")

lines += ["", "Replay Spec Ready Candidates:", ""]

for r in records:
    lines.append(
        f"- {r['candidate_id']} | {r['strategy_name']} | "
        f"{r['signal_family']} | {r['replay_spec_readiness']}"
    )

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(json.dumps({
    "phase": PHASE,
    "bar_replay_candidate_count": len(records),
    "signal_family_counts": dict(family_counter),
    "readiness_counts": dict(readiness_counter),
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
    "recommended_next_phase": summary["recommended_next_phase"],
    "certified": summary["certified"],
}, indent=2, ensure_ascii=False))

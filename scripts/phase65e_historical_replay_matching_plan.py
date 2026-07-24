#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
from collections import Counter, defaultdict
import json

ROOT = Path(".").resolve()
BASE = ROOT / "runtime" / "research_library" / "strategy_sources" / "151_trading_strategies"
CANDIDATES = BASE / "candidates"
PLANS = BASE / "replay_plans"

SOURCE = CANDIDATES / "65D_research_candidate_registry_latest.json"

OUT_JSON = PLANS / "65E_historical_replay_matching_plan_latest.json"
OUT_TXT = PLANS / "65E_historical_replay_matching_plan_latest.txt"

PHASE = "65E_HISTORICAL_REPLAY_MATCHING_PLAN"

PLANS.mkdir(parents=True, exist_ok=True)


def replay_feasibility(candidate: dict) -> str:
    requirements = set(candidate.get("market_data_requirements", []))
    asset = candidate.get("asset_class")

    if "options_chain" in requirements:
        return "BLOCKED_REQUIRES_OPTIONS_CHAIN"
    if "interest_rate_curve" in requirements:
        return "PARTIAL_REQUIRES_RATE_CURVE"
    if "volatility_data" in requirements and asset in {"options", "volatility"}:
        return "PARTIAL_REQUIRES_VOLATILITY_SOURCE"
    if asset in {"stocks", "etf", "indexes", "commodities", "futures", "foreign_exchange", "cryptocurrencies", "global_macro"}:
        return "REPLAY_PLANNABLE_WITH_HISTORICAL_BARS"
    return "RESEARCH_ONLY_UNMAPPED"


def replay_data_sources(candidate: dict) -> list[str]:
    requirements = set(candidate.get("market_data_requirements", []))
    asset = candidate.get("asset_class")
    sources = []

    if "historical_price_bars" in requirements:
        sources.extend([
            "yfinance_historical_bars",
            "market_data_provider_router",
        ])

    if "macro_indicators" in requirements or asset == "global_macro":
        sources.extend([
            "FRED_API_READ_ONLY",
            "STATCAN_READ_ONLY",
        ])

    if "interest_rate_curve" in requirements:
        sources.extend([
            "FRED_API_READ_ONLY",
            "BANK_OF_CANADA_FUTURE_READ_ONLY",
        ])

    if "volatility_data" in requirements:
        sources.extend([
            "yfinance_volatility_proxy",
            "future_options_or_vix_provider",
        ])

    if "options_chain" in requirements:
        sources.append("OPTIONS_CHAIN_PROVIDER_REQUIRED_FUTURE")

    if "text_or_sentiment_data" in requirements:
        sources.append("RESEARCH_TEXT_SENTIMENT_INDEX_REQUIRED_FUTURE")

    return sorted(set(sources))


def required_tests(candidate: dict) -> list[str]:
    tests = [
        "historical_replay",
        "transaction_cost_test",
        "drawdown_test",
        "walk_forward_split",
        "out_of_sample_split",
        "regime_split",
    ]

    if candidate.get("implementation_complexity") == "HIGH":
        tests.append("manual_formula_review")
        tests.append("implementation_risk_review")

    if "options_chain" in candidate.get("market_data_requirements", []):
        tests.append("options_specific_risk_review")

    if candidate.get("asset_class") in {"fx", "foreign_exchange", "futures", "commodities"}:
        tests.append("market_specific_liquidity_review")

    return sorted(set(tests))


def next_status(feasibility: str) -> str:
    if feasibility == "REPLAY_PLANNABLE_WITH_HISTORICAL_BARS":
        return "AWAITING_REPLAY_SPEC"
    if feasibility.startswith("PARTIAL"):
        return "AWAITING_DATA_SOURCE_MAPPING"
    if feasibility.startswith("BLOCKED"):
        return "BLOCKED_BY_DATA_REQUIREMENT"
    return "RESEARCH_ONLY"


registry = json.loads(SOURCE.read_text(encoding="utf-8")) if SOURCE.exists() else {}
candidates = registry.get("candidates", [])

plans = []
feasibility_counter = Counter()
asset_counter = Counter()
source_counter = Counter()

for candidate in candidates:
    feasibility = replay_feasibility(candidate)
    sources = replay_data_sources(candidate)
    tests = required_tests(candidate)

    feasibility_counter[feasibility] += 1
    asset_counter[candidate.get("asset_class", "unknown")] += 1
    source_counter.update(sources)

    plan = {
        "candidate_id": candidate.get("candidate_id"),
        "strategy_name": candidate.get("strategy_name"),
        "source_page": candidate.get("source_page"),
        "asset_class": candidate.get("asset_class"),
        "implementation_complexity": candidate.get("implementation_complexity"),
        "indicator_requirements": candidate.get("indicator_requirements", []),
        "market_data_requirements": candidate.get("market_data_requirements", []),
        "replay_feasibility": feasibility,
        "candidate_replay_status": next_status(feasibility),
        "proposed_read_only_sources": sources,
        "required_tests": tests,
        "refactor_policy_preview": {
            "near_miss_band_percent": {
                "min": 2,
                "max": 10
            },
            "max_refactor_attempts": 3,
            "after_3_failed_attempts": "QUARANTINE_OR_TRASH",
            "passing_result_destination": "INACTIVE_STRATEGY_DATABANK_CANDIDATE",
            "activation_requires_manual_gate": True
        },
        "safety": {
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

    plans.append(plan)

summary = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_HISTORICAL_REPLAY_MATCHING_PLAN",
    "source_registry": str(SOURCE),
    "candidate_count": len(candidates),
    "plan_count": len(plans),
    "feasibility_counts": dict(feasibility_counter),
    "asset_counts": dict(asset_counter),
    "proposed_source_counts": dict(source_counter),
    "plans": plans,
    "global_policy": {
        "replay_planning_allowed": True,
        "historical_replay_allowed_now": False,
        "candidate_generation_allowed": False,
        "strategy_execution_allowed": False,
        "implementation_patch_allowed": False,
        "runtime_execution_allowed": False,
        "runtime_mutation_allowed": False,
        "learning_enabled": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
        "passing_result_destination": "inactive_strategy_databank_candidate_only",
        "activation_requires_manual_gate": True,
        "near_miss_refactor_band_percent": "2_to_10",
        "max_refactor_attempts": 3,
    },
    "checks": {
        "source_registry_exists": SOURCE.exists(),
        "source_registry_certified": registry.get("certified") is True,
        "candidates_present": len(candidates) > 0,
        "plans_created_for_all_candidates": len(plans) == len(candidates) and len(plans) > 0,
        "has_replay_plannable_candidates": feasibility_counter.get("REPLAY_PLANNABLE_WITH_HISTORICAL_BARS", 0) > 0,
        "all_replay_disabled_now": all(p["safety"]["historical_replay_allowed_now"] is False for p in plans),
        "all_execution_blocked": all(p["safety"]["strategy_execution_allowed"] is False for p in plans),
        "all_promotion_blocked": all(p["safety"]["promotion_enabled"] is False for p in plans),
        "all_broker_live_blocked": all(
            p["safety"]["broker_execution_enabled"] is False
            and p["safety"]["live_execution_enabled"] is False
            for p in plans
        ),
    },
    "recommended_next_phase": "65F_FORMULA_AND_SIGNAL_REQUIREMENT_EXTRACTOR",
    "certified": False,
}

summary["certified"] = all(summary["checks"].values())

OUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

lines = [
    PHASE,
    "",
    f"certified: {summary['certified']}",
    f"candidate_count: {summary['candidate_count']}",
    f"plan_count: {summary['plan_count']}",
    "",
    "Feasibility Counts:",
]

for key, value in summary["feasibility_counts"].items():
    lines.append(f"- {key}: {value}")

lines.extend([
    "",
    "Replay-Plannable Candidates Sample:",
    "",
])

for plan in plans:
    if plan["replay_feasibility"] == "REPLAY_PLANNABLE_WITH_HISTORICAL_BARS":
        lines.append(f"- {plan['candidate_id']} | {plan['strategy_name']} | {plan['asset_class']}")
        if len(lines) > 80:
            break

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(json.dumps({
    "phase": PHASE,
    "candidate_count": len(candidates),
    "plan_count": len(plans),
    "feasibility_counts": dict(feasibility_counter),
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
    "recommended_next_phase": summary["recommended_next_phase"],
    "certified": summary["certified"],
}, indent=2, ensure_ascii=False))

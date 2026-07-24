#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json
import re

ROOT = Path(".").resolve()
BASE = ROOT / "runtime" / "research_library" / "strategy_sources" / "151_trading_strategies"
INDEX = BASE / "index"
CANDIDATES = BASE / "candidates"

SOURCE = INDEX / "65C_strategy_source_index_latest.json"

OUT_REGISTRY = CANDIDATES / "65D_research_candidate_registry_latest.json"
OUT_MANIFEST = CANDIDATES / "65D_candidate_manifest_latest.json"
OUT_TXT = CANDIDATES / "65D_candidate_extraction_latest.txt"

PHASE = "65D_RESEARCH_CANDIDATE_EXTRACTION_CONTROLLER"

CANDIDATES.mkdir(parents=True, exist_ok=True)


def slug(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def clean_strategy_name(line: str) -> dict:
    section = None
    page = None

    section_match = re.match(r"^([0-9]+(?:\.[0-9]+)*)\s+Strategy:\s+(.+)$", line)
    if section_match:
        section = section_match.group(1)
        raw = section_match.group(2)
    else:
        raw = line

    page_match = re.search(r"\s+([0-9]{1,4})$", raw)
    if page_match:
        page = int(page_match.group(1))
        raw = raw[:page_match.start()]

    raw = re.sub(r"\.{2,}", " ", raw)
    raw = " ".join(raw.replace("ﬁ", "fi").replace("ﬂ", "fl").split())

    return {
        "section": section,
        "name": raw,
        "page": page,
    }


def infer_asset_class(category: str, name: str) -> str:
    if category == "fx":
        return "foreign_exchange"
    if category == "etfs":
        return "etf"
    return category


def infer_data_requirements(asset_class: str, name: str) -> list[str]:
    low = name.lower()
    req = ["historical_price_bars"]

    if any(x in low for x in ["volume", "market-making", "liquidity"]):
        req.append("volume")
    if any(x in low for x in ["volatility", "vix", "variance", "gamma", "implied"]):
        req.append("volatility_data")
    if any(x in low for x in ["option", "call", "put", "straddle", "strangle", "butterfly", "condor"]):
        req.append("options_chain")
    if any(x in low for x in ["yield", "bond", "duration", "curve", "swap"]):
        req.append("interest_rate_curve")
    if any(x in low for x in ["macro", "inflation", "economic"]):
        req.append("macro_indicators")
    if any(x in low for x in ["sentiment", "news"]):
        req.append("text_or_sentiment_data")

    return sorted(set(req))


def infer_indicators(name: str) -> list[str]:
    low = name.lower()
    indicators = []

    if "momentum" in low:
        indicators.append("momentum")
    if "moving average" in low or "ma filter" in low:
        indicators.append("moving_average")
    if "mean-reversion" in low or "contrarian" in low:
        indicators.append("mean_reversion")
    if "volatility" in low or "low-volatility" in low:
        indicators.append("volatility")
    if "value" in low:
        indicators.append("value_factor")
    if "carry" in low:
        indicators.append("carry")
    if "trend following" in low:
        indicators.append("trend_following")
    if "pairs" in low:
        indicators.append("pair_spread")
    if "arbitrage" in low:
        indicators.append("arbitrage_spread")

    return sorted(set(indicators))


def infer_complexity(asset_class: str, requirements: list[str]) -> str:
    if "options_chain" in requirements or asset_class in {
        "options", "structured_assets", "convertibles", "tax_arbitrage"
    }:
        return "HIGH"
    if "interest_rate_curve" in requirements or "volatility_data" in requirements:
        return "MEDIUM"
    return "LOW"


source = json.loads(SOURCE.read_text(encoding="utf-8")) if SOURCE.exists() else {}
profile = source.get("source_profile", {})
categories = profile.get("strategy_categories", {})

candidates = []
counter = 1

for category, lines in categories.items():
    for line in lines:
        parsed = clean_strategy_name(line)
        name = parsed["name"]
        asset_class = infer_asset_class(category, name)
        data_req = infer_data_requirements(asset_class, name)
        indicators = infer_indicators(name)
        complexity = infer_complexity(asset_class, data_req)

        candidate_id = f"SSRN_3247865_{counter:03d}_{slug(name)[:40]}"

        candidate = {
            "candidate_id": candidate_id,
            "candidate_version": 1,
            "status": "RESEARCH_EXTRACTED_UNVERIFIED",
            "strategy_name": name,
            "source_document": "151 Trading Strategies",
            "source_id": profile.get("source_id"),
            "source_section": parsed["section"],
            "source_page": parsed["page"],
            "source_category": category,
            "asset_class": asset_class,
            "market_type": "unknown",
            "summary": None,
            "mathematical_model": None,
            "indicator_requirements": indicators,
            "market_data_requirements": data_req,
            "risk_constraints": [
                "requires_risk_review",
                "requires_drawdown_test",
                "requires_transaction_cost_test",
                "requires_regime_test",
            ],
            "execution_requirements": [],
            "assumptions": [],
            "research_confidence": "UNASSESSED",
            "implementation_complexity": complexity,
            "implementation_state": "NOT_IMPLEMENTED",
            "replay_state": "NOT_REPLAYED",
            "promotion_state": "NOT_ELIGIBLE",
            "requires_human_review": True,
            "lineage": {
                "parent_source": "ssrn_3247865",
                "extraction_phase": PHASE,
                "attempt_number": 0,
                "parent_candidate_id": None,
            },
            "safety": {
                "candidate_generation_complete": True,
                "historical_replay_allowed": False,
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

        (CANDIDATES / f"{candidate_id}.json").write_text(
            json.dumps(candidate, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        candidates.append(candidate)
        counter += 1

manifest = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_RESEARCH_CANDIDATE_EXTRACTION",
    "source_index": str(SOURCE),
    "candidate_count": len(candidates),
    "candidate_files": [
        f"{c['candidate_id']}.json"
        for c in candidates
    ],
    "safety_policy": {
        "historical_replay_allowed": False,
        "strategy_execution_allowed": False,
        "implementation_patch_allowed": False,
        "runtime_execution_allowed": False,
        "runtime_mutation_allowed": False,
        "learning_enabled": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "65E_HISTORICAL_REPLAY_MATCHING_PLAN",
    "certified": len(candidates) > 0,
}

registry = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "source": "151 Trading Strategies",
    "candidate_count": len(candidates),
    "candidates": candidates,
    "checks": {
        "source_index_exists": SOURCE.exists(),
        "source_index_certified": source.get("certified") is True,
        "candidates_extracted": len(candidates) > 0,
        "all_require_human_review": all(c["requires_human_review"] for c in candidates),
        "all_replay_blocked": all(c["safety"]["historical_replay_allowed"] is False for c in candidates),
        "all_execution_blocked": all(c["safety"]["strategy_execution_allowed"] is False for c in candidates),
        "all_promotion_blocked": all(c["safety"]["promotion_enabled"] is False for c in candidates),
        "all_broker_live_blocked": all(
            c["safety"]["broker_execution_enabled"] is False
            and c["safety"]["live_execution_enabled"] is False
            for c in candidates
        ),
    },
    "recommended_next_phase": "65E_HISTORICAL_REPLAY_MATCHING_PLAN",
    "certified": False,
}

registry["certified"] = all(registry["checks"].values())

OUT_REGISTRY.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")
OUT_MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

lines = [
    PHASE,
    "",
    f"certified: {registry['certified']}",
    f"candidate_count: {len(candidates)}",
    "",
    "Extracted Candidates:",
    "",
]

for c in candidates[:120]:
    lines.append(f"- {c['candidate_id']} | {c['strategy_name']} | {c['asset_class']} | {c['implementation_complexity']}")

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(json.dumps({
    "phase": PHASE,
    "candidate_count": len(candidates),
    "out_registry": str(OUT_REGISTRY),
    "out_manifest": str(OUT_MANIFEST),
    "out_txt": str(OUT_TXT),
    "recommended_next_phase": "65E_HISTORICAL_REPLAY_MATCHING_PLAN",
    "certified": registry["certified"],
}, indent=2, ensure_ascii=False))

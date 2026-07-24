#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json
import re

ROOT = Path(".").resolve()
BASE = ROOT / "runtime" / "research_library" / "strategy_sources" / "151_trading_strategies"
RAW = BASE / "raw"
EXTRACTED = BASE / "extracted"
INDEX = BASE / "index"

REGISTRY = BASE / "65B_strategy_source_intake_registry_latest.json"
PDF = RAW / "151_Trading_Strategies_ssrn_3247865.pdf"

OUT_JSON = INDEX / "65C_strategy_source_index_latest.json"
OUT_TXT = INDEX / "65C_strategy_source_index_latest.txt"

PHASE = "65C_STRATEGY_SOURCE_INDEX_BUILDER"

EXTRACTED.mkdir(parents=True, exist_ok=True)
INDEX.mkdir(parents=True, exist_ok=True)

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_STRATEGY_SOURCE_INDEX_BUILDER",
    "source_registry": str(REGISTRY),
    "source_pdf": str(PDF),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8")) if REGISTRY.exists() else {}

    try:
        from pypdf import PdfReader
    except Exception:
        from PyPDF2 import PdfReader

    reader = PdfReader(str(PDF))
    page_count = len(reader.pages)

    # Extract first pages only. Enough for TOC/index map. No full paper dump.
    max_pages = min(12, page_count)
    extracted_pages = []

    for i in range(max_pages):
        text = reader.pages[i].extract_text() or ""
        extracted_pages.append({
            "page": i + 1,
            "text": text[:8000],
        })

    combined = "\n".join(page["text"] for page in extracted_pages)

    strategy_lines = []
    for line in combined.splitlines():
        cleaned = " ".join(line.strip().split())
        if not cleaned:
            continue

        if re.search(r"\bStrategy\s*:", cleaned, flags=re.IGNORECASE):
            strategy_lines.append(cleaned)

    asset_sections = []
    for line in combined.splitlines():
        cleaned = " ".join(line.strip().split())
        if re.match(r"^\d+\s+[A-Z][A-Za-z ,/&()–-]+", cleaned):
            asset_sections.append(cleaned)

    strategy_categories = {
        "options": [],
        "stocks": [],
        "etfs": [],
        "fixed_income": [],
        "indexes": [],
        "volatility": [],
        "fx": [],
        "commodities": [],
        "futures": [],
        "structured_assets": [],
        "convertibles": [],
        "tax_arbitrage": [],
        "misc_assets": [],
        "distressed_assets": [],
        "real_estate": [],
        "cash": [],
        "cryptocurrencies": [],
        "global_macro": [],
    }

    category_keywords = {
        "options": ["call", "put", "straddle", "strangle", "butterfly", "condor", "collar", "spread"],
        "stocks": ["momentum", "value", "low-volatility", "pairs", "mean-reversion", "moving average"],
        "etfs": ["sector", "rotation", "leveraged", "multi-asset"],
        "fixed_income": ["bond", "duration", "yield", "swap", "curve"],
        "indexes": ["index", "cash-and-carry", "dispersion"],
        "volatility": ["vix", "volatility", "variance", "gamma"],
        "fx": ["fx", "foreign exchange", "carry trade"],
        "commodities": ["commodity", "roll yields", "skewness"],
        "futures": ["futures", "calendar spread", "trend following"],
        "structured_assets": ["cdo", "mortgage", "tranche"],
        "convertibles": ["convertible"],
        "tax_arbitrage": ["tax"],
        "misc_assets": ["inflation", "weather", "energy"],
        "distressed_assets": ["distressed"],
        "real_estate": ["real estate"],
        "cash": ["cash", "repo", "liquidity"],
        "cryptocurrencies": ["cryptocurrency", "crypto", "neural", "sentiment"],
        "global_macro": ["macro"],
    }

    for line in strategy_lines:
        low = line.lower()
        placed = False

        for category, keywords in category_keywords.items():
            if any(k in low for k in keywords):
                strategy_categories[category].append(line)
                placed = True
                break

        if not placed:
            strategy_categories.setdefault("uncategorized", []).append(line)

    result["source_profile"] = {
        "title": registry.get("research_source", {}).get("title"),
        "source_id": registry.get("research_source", {}).get("source_id"),
        "page_count": page_count,
        "pages_indexed": max_pages,
        "asset_sections_detected": asset_sections[:60],
        "strategy_line_count": len(strategy_lines),
        "strategy_lines_sample": strategy_lines[:80],
        "strategy_categories": {
            key: value[:80]
            for key, value in strategy_categories.items()
            if value
        },
    }

    result["index_policy"] = {
        "read_allowed": True,
        "summary_allowed": True,
        "indexing_allowed": True,
        "candidate_generation_allowed": False,
        "historical_replay_allowed": False,
        "strategy_execution_allowed": False,
        "implementation_patch_allowed": False,
        "runtime_execution_allowed": False,
        "runtime_mutation_allowed": False,
        "learning_enabled": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    }

    result["checks"]["registry_exists"] = REGISTRY.exists()
    result["checks"]["registry_certified"] = registry.get("certified") is True
    result["checks"]["pdf_exists"] = PDF.exists()
    result["checks"]["pdf_pages_present"] = page_count > 0
    result["checks"]["pages_indexed"] = max_pages > 0
    result["checks"]["strategy_lines_detected"] = len(strategy_lines) > 0
    result["checks"]["asset_sections_detected"] = len(asset_sections) > 0

    result["checks"]["candidate_generation_blocked"] = result["index_policy"]["candidate_generation_allowed"] is False
    result["checks"]["historical_replay_blocked"] = result["index_policy"]["historical_replay_allowed"] is False
    result["checks"]["strategy_execution_blocked"] = result["index_policy"]["strategy_execution_allowed"] is False
    result["checks"]["runtime_execution_blocked"] = result["index_policy"]["runtime_execution_allowed"] is False
    result["checks"]["runtime_mutation_blocked"] = result["index_policy"]["runtime_mutation_allowed"] is False
    result["checks"]["learning_blocked"] = result["index_policy"]["learning_enabled"] is False
    result["checks"]["promotion_blocked"] = result["index_policy"]["promotion_enabled"] is False
    result["checks"]["broker_blocked"] = result["index_policy"]["broker_execution_enabled"] is False
    result["checks"]["live_blocked"] = result["index_policy"]["live_execution_enabled"] is False

    result["recommended_next_phase"] = "65D_STRATEGY_CANDIDATE_EXTRACTION_DRY_RUN"

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

lines = [
    f"{PHASE}",
    "",
    f"certified: {result['certified']}",
    f"source_pdf: {PDF}",
    "",
    "Detected Strategy Lines:",
    "",
]

for item in result.get("source_profile", {}).get("strategy_lines_sample", []):
    lines.append(f"- {item}")

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(json.dumps(result, indent=2, ensure_ascii=False))
print(f"\nWROTE: {OUT_JSON}")
print(f"WROTE: {OUT_TXT}")

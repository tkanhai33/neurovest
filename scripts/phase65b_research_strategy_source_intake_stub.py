#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import hashlib
import json
import shutil

ROOT = Path(".").resolve()

PHASE = "65B_RESEARCH_STRATEGY_SOURCE_INTAKE_STUB"

SSRN_MATCHES = sorted((Path.home() / "Downloads").glob("*3247865*.pdf"))
SOURCE = SSRN_MATCHES[0] if SSRN_MATCHES else Path.home() / "Downloads" / "ssrn-3247865.pdf"

BASE = ROOT / "runtime" / "research_library" / "strategy_sources" / "151_trading_strategies"
RAW = BASE / "raw"
EXTRACTED = BASE / "extracted"
INDEX = BASE / "index"

OUT = BASE / "65B_strategy_source_intake_registry_latest.json"

for folder in [RAW, EXTRACTED, INDEX]:
    folder.mkdir(parents=True, exist_ok=True)


def sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_RESEARCH_STRATEGY_SOURCE_INTAKE",
    "source_file": str(SOURCE),
    "research_source": {
        "source_id": "ssrn_3247865_151_trading_strategies",
        "title": "151 Trading Strategies",
        "authors": [
            "Zura Kakushadze",
            "Juan Andrés Serur"
        ],
        "source_type": "strategy_reference",
        "knowledge_class": "research_library",
        "asset_scope": [
            "stocks",
            "options",
            "fixed_income",
            "futures",
            "etfs",
            "indexes",
            "commodities",
            "foreign_exchange",
            "convertibles",
            "structured_assets",
            "volatility",
            "real_estate",
            "distressed_assets",
            "cash",
            "cryptocurrencies",
            "global_macro",
            "infrastructure"
        ],
        "intended_use": [
            "strategy_concept_reference",
            "formula_reference",
            "research_idea_source",
            "future_candidate_extraction_source",
            "historical_replay_planning_source"
        ],
        "not_intended_for": [
            "direct_strategy_execution",
            "direct_code_generation",
            "live_signal_generation",
            "broker_execution",
            "autonomous_promotion"
        ],
    },
    "copied_files": {},
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    target = RAW / "151_Trading_Strategies_ssrn_3247865.pdf"

    if SOURCE.exists():
        shutil.copy2(SOURCE, target)

    result["copied_files"]["raw_pdf"] = str(target)

    result["file_profile"] = {
        "raw_pdf_exists": target.exists(),
        "raw_pdf_bytes": target.stat().st_size if target.exists() else 0,
        "raw_pdf_sha256": sha256(target),
    }

    result["research_use_policy"] = {
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

        "allowed_next_phases": [
            "65C_STRATEGY_SOURCE_INDEX_BUILDER",
            "65D_STRATEGY_CANDIDATE_EXTRACTION_DRY_RUN",
            "65E_HISTORICAL_REPLAY_MATCHING_PLAN"
        ],
    }

    result["storage_layout"] = {
        "base": str(BASE),
        "raw": str(RAW),
        "extracted": str(EXTRACTED),
        "index": str(INDEX),
        "registry": str(OUT),
    }

    result["checks"]["source_exists"] = SOURCE.exists()
    result["checks"]["raw_pdf_copied"] = target.exists()
    result["checks"]["raw_pdf_nonempty"] = target.exists() and target.stat().st_size > 0
    result["checks"]["sha256_present"] = bool(result["file_profile"]["raw_pdf_sha256"])
    result["checks"]["source_type_strategy_reference"] = result["research_source"]["source_type"] == "strategy_reference"
    result["checks"]["knowledge_class_research_library"] = result["research_source"]["knowledge_class"] == "research_library"

    result["checks"]["read_allowed"] = result["research_use_policy"]["read_allowed"] is True
    result["checks"]["summary_allowed"] = result["research_use_policy"]["summary_allowed"] is True
    result["checks"]["indexing_allowed"] = result["research_use_policy"]["indexing_allowed"] is True

    result["checks"]["candidate_generation_blocked"] = result["research_use_policy"]["candidate_generation_allowed"] is False
    result["checks"]["historical_replay_blocked"] = result["research_use_policy"]["historical_replay_allowed"] is False
    result["checks"]["strategy_execution_blocked"] = result["research_use_policy"]["strategy_execution_allowed"] is False
    result["checks"]["implementation_patch_blocked"] = result["research_use_policy"]["implementation_patch_allowed"] is False
    result["checks"]["runtime_execution_blocked"] = result["research_use_policy"]["runtime_execution_allowed"] is False
    result["checks"]["runtime_mutation_blocked"] = result["research_use_policy"]["runtime_mutation_allowed"] is False
    result["checks"]["learning_blocked"] = result["research_use_policy"]["learning_enabled"] is False
    result["checks"]["promotion_blocked"] = result["research_use_policy"]["promotion_enabled"] is False
    result["checks"]["broker_blocked"] = result["research_use_policy"]["broker_execution_enabled"] is False
    result["checks"]["live_blocked"] = result["research_use_policy"]["live_execution_enabled"] is False

    result["recommended_next_phase"] = "65C_STRATEGY_SOURCE_INDEX_BUILDER"

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps(result, indent=2, ensure_ascii=False))
print(f"\nWROTE: {OUT}")

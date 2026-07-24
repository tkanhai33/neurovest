#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json
import hashlib

ROOT = Path(".").resolve()
LIB = ROOT / "runtime" / "research_library"
STRATEGY_SOURCES = LIB / "strategy_sources"
OUT_DIR = LIB / "master_registry"

OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "65I_research_master_registry_latest.json"
OUT_TXT = OUT_DIR / "65I_research_master_registry_latest.txt"

PHASE = "65I_RESEARCH_MASTER_REGISTRY_BUILDER"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


sources = []

for pdf in sorted(STRATEGY_SOURCES.rglob("raw/*.pdf")):
    source_id = f"RL{len(sources)+1:06d}"

    name = pdf.stem.replace("_", " ").replace("-", " ")

    topics = []
    low = name.lower()

    if "trading" in low or "strategy" in low:
        topics.append("trading_strategies")
    if "machine" in low or "learning" in low or "ai" in low:
        topics.append("machine_learning")
    if "momentum" in low:
        topics.append("momentum")
    if "portfolio" in low:
        topics.append("portfolio")
    if "risk" in low:
        topics.append("risk")
    if "quant" in low:
        topics.append("quantitative_finance")

    if not topics:
        topics.append("research_source_unclassified")

    sources.append({
        "research_id": source_id,
        "title_guess": name,
        "source_type": "pdf_research_source",
        "knowledge_class": "research_library",
        "path": str(pdf),
        "bytes": pdf.stat().st_size,
        "sha256": sha256(pdf),
        "topics_guess": topics,
        "index_state": "NOT_INDEXED_BY_MASTER",
        "candidate_extraction_state": "NOT_EXTRACTED_BY_MASTER",
        "safety": {
            "read_allowed": True,
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
            "live_execution_enabled": False
        }
    })


result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_RESEARCH_MASTER_REGISTRY",
    "library_root": str(LIB),
    "source_count": len(sources),
    "sources": sources,
    "checks": {
        "library_exists": LIB.exists(),
        "strategy_sources_exists": STRATEGY_SOURCES.exists(),
        "sources_found": len(sources) > 0,
        "all_sources_nonempty": all(s["bytes"] > 0 for s in sources),
        "all_sha256_present": all(bool(s["sha256"]) for s in sources),
        "all_runtime_blocked": all(s["safety"]["runtime_execution_allowed"] is False for s in sources),
        "all_execution_blocked": all(s["safety"]["strategy_execution_allowed"] is False for s in sources),
        "all_promotion_blocked": all(s["safety"]["promotion_enabled"] is False for s in sources),
        "all_broker_live_blocked": all(
            s["safety"]["broker_execution_enabled"] is False
            and s["safety"]["live_execution_enabled"] is False
            for s in sources
        ),
    },
    "recommended_next_phase": "65J_UNIVERSAL_RESEARCH_PAPER_INDEXER",
    "certified": False,
}

result["certified"] = all(result["checks"].values())

OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

lines = [
    PHASE,
    "",
    f"certified: {result['certified']}",
    f"source_count: {result['source_count']}",
    "",
    "Sources:",
    "",
]

for s in sources:
    lines.append(f"- {s['research_id']} | {s['title_guess']} | {s['path']}")

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(json.dumps({
    "phase": PHASE,
    "source_count": result["source_count"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
    "recommended_next_phase": result["recommended_next_phase"],
    "certified": result["certified"],
}, indent=2, ensure_ascii=False))

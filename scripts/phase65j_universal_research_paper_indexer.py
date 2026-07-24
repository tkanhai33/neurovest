#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
from collections import Counter
import json
import re

ROOT = Path(".").resolve()
LIB = ROOT / "runtime" / "research_library"
MASTER = LIB / "master_registry" / "65I_research_master_registry_latest.json"
OUT_DIR = LIB / "universal_index"

OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "65J_universal_research_paper_index_latest.json"
OUT_TXT = OUT_DIR / "65J_universal_research_paper_index_latest.txt"

PHASE = "65J_UNIVERSAL_RESEARCH_PAPER_INDEXER"


KEYWORDS = {
    "trading": ["trading", "strategy", "alpha", "signal", "portfolio", "asset pricing"],
    "momentum": ["momentum", "trend following", "relative strength"],
    "value": ["value", "valuation", "book-to-market"],
    "risk": ["risk", "drawdown", "var", "expected shortfall", "volatility"],
    "machine_learning": ["machine learning", "neural", "random forest", "xgboost", "knn", "reinforcement"],
    "statistics": ["regression", "bayesian", "monte carlo", "stochastic", "probability"],
    "macro": ["inflation", "interest rate", "yield curve", "macro", "monetary"],
    "optimization": ["optimization", "convex", "objective function", "constraint"],
    "quantum_physics": ["quantum", "string theory", "physics", "hamiltonian"],
    "fraud_anomaly": ["fraud", "anomaly", "money laundering", "outlier"],
}


def read_pdf_sample(path: Path, max_pages: int = 8) -> dict:
    try:
        try:
            from pypdf import PdfReader
        except Exception:
            from PyPDF2 import PdfReader

        reader = PdfReader(str(path))
        page_count = len(reader.pages)

        pages = []
        for i in range(min(page_count, max_pages)):
            text = reader.pages[i].extract_text() or ""
            pages.append({
                "page": i + 1,
                "text": text[:6000],
            })

        return {
            "ok": True,
            "page_count": page_count,
            "pages_indexed": len(pages),
            "text": "\n".join(p["text"] for p in pages),
            "error": None,
        }

    except Exception as exc:
        return {
            "ok": False,
            "page_count": 0,
            "pages_indexed": 0,
            "text": "",
            "error": {
                "type": type(exc).__name__,
                "message": str(exc),
            },
        }


def guess_title(text: str, fallback: str) -> str:
    lines = [
        " ".join(line.strip().split())
        for line in text.splitlines()
        if len(line.strip()) > 8
    ]

    for line in lines[:20]:
        if len(line) < 180 and not line.lower().startswith(("abstract", "introduction")):
            return line

    return fallback


def topic_scores(text: str) -> dict:
    low = text.lower()
    scores = {}

    for topic, words in KEYWORDS.items():
        scores[topic] = sum(low.count(word) for word in words)

    return scores


def classify(scores: dict) -> list[str]:
    ranked = sorted(
        [(topic, score) for topic, score in scores.items() if score > 0],
        key=lambda x: x[1],
        reverse=True,
    )

    if not ranked:
        return ["unclassified_research"]

    return [topic for topic, _ in ranked[:5]]


def abstract_guess(text: str) -> str | None:
    m = re.search(r"\bAbstract\b(.{200,1800})", text, flags=re.IGNORECASE | re.DOTALL)
    if not m:
        return None

    abstract = " ".join(m.group(1).split())
    return abstract[:1200]


master = json.loads(MASTER.read_text(encoding="utf-8")) if MASTER.exists() else {}
sources = master.get("sources", [])

records = []
topic_counter = Counter()

for source in sources:
    path = Path(source.get("path", ""))
    sample = read_pdf_sample(path)
    text = sample["text"]
    scores = topic_scores(text)
    topics = classify(scores)

    topic_counter.update(topics)

    record = {
        "research_id": source.get("research_id"),
        "source_path": str(path),
        "title_guess": guess_title(text, source.get("title_guess", path.stem)),
        "abstract_guess": abstract_guess(text),
        "page_count": sample["page_count"],
        "pages_indexed": sample["pages_indexed"],
        "topic_scores": scores,
        "topics": topics,
        "index_state": "INDEXED_READ_ONLY" if sample["ok"] else "INDEX_FAILED",
        "sample_error": sample["error"],
        "safety": {
            "index_only": True,
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
        },
    }

    records.append(record)

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_UNIVERSAL_RESEARCH_PAPER_INDEX",
    "source_master_registry": str(MASTER),
    "source_count": len(sources),
    "indexed_count": sum(1 for r in records if r["index_state"] == "INDEXED_READ_ONLY"),
    "failed_count": sum(1 for r in records if r["index_state"] == "INDEX_FAILED"),
    "topic_counts": dict(topic_counter),
    "records": records,
    "global_policy": {
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
    },
    "checks": {
        "master_registry_exists": MASTER.exists(),
        "master_registry_certified": master.get("certified") is True,
        "sources_present": len(sources) > 0,
        "all_sources_processed": len(records) == len(sources) and len(records) > 0,
        "at_least_one_indexed": any(r["index_state"] == "INDEXED_READ_ONLY" for r in records),
        "all_candidate_generation_blocked": all(r["safety"]["candidate_generation_allowed"] is False for r in records),
        "all_replay_blocked": all(r["safety"]["historical_replay_allowed"] is False for r in records),
        "all_execution_blocked": all(r["safety"]["strategy_execution_allowed"] is False for r in records),
        "all_promotion_blocked": all(r["safety"]["promotion_enabled"] is False for r in records),
        "all_broker_live_blocked": all(
            r["safety"]["broker_execution_enabled"] is False
            and r["safety"]["live_execution_enabled"] is False
            for r in records
        ),
    },
    "recommended_next_phase": "65K_RESEARCH_KNOWLEDGE_GRAPH_BUILDER",
    "certified": False,
}

result["certified"] = all(result["checks"].values())

OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

lines = [
    PHASE,
    "",
    f"certified: {result['certified']}",
    f"source_count: {result['source_count']}",
    f"indexed_count: {result['indexed_count']}",
    f"failed_count: {result['failed_count']}",
    "",
    "Topic Counts:",
]

for topic, count in result["topic_counts"].items():
    lines.append(f"- {topic}: {count}")

lines += ["", "Indexed Sources:", ""]

for r in records:
    lines.append(f"- {r['research_id']} | {r['title_guess']} | {', '.join(r['topics'])}")

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(json.dumps({
    "phase": PHASE,
    "source_count": result["source_count"],
    "indexed_count": result["indexed_count"],
    "failed_count": result["failed_count"],
    "topic_counts": result["topic_counts"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
    "recommended_next_phase": result["recommended_next_phase"],
    "certified": result["certified"],
}, indent=2, ensure_ascii=False))

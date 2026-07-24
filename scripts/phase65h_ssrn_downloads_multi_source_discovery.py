#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import hashlib
import json
import shutil
import re

ROOT = Path(".").resolve()
DOWNLOADS = Path.home() / "Downloads"

BASE = ROOT / "runtime" / "research_library" / "strategy_sources"
OUT = BASE / "65H_ssrn_downloads_multi_source_discovery_latest.json"

PHASE = "65H_SSRN_DOWNLOADS_MULTI_SOURCE_DISCOVERY"

BASE.mkdir(parents=True, exist_ok=True)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_name(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    return name.strip("_")


pdfs = sorted(DOWNLOADS.glob("*.pdf"))

ssrn_pdfs = [
    p for p in pdfs
    if "ssrn" in p.name.lower() or re.search(r"\d{6,}", p.name)
]

sources = []

for pdf in ssrn_pdfs:
    stem = safe_name(pdf.stem)
    source_id = f"ssrn_download_{stem}"

    folder = BASE / source_id
    raw = folder / "raw"
    extracted = folder / "extracted"
    index = folder / "index"

    raw.mkdir(parents=True, exist_ok=True)
    extracted.mkdir(parents=True, exist_ok=True)
    index.mkdir(parents=True, exist_ok=True)

    target = raw / pdf.name
    shutil.copy2(pdf, target)

    sources.append({
        "source_id": source_id,
        "original_file": str(pdf),
        "copied_file": str(target),
        "bytes": target.stat().st_size,
        "sha256": sha256(target),
        "source_type": "ssrn_pdf_research_source",
        "knowledge_class": "research_library",
        "status": "DISCOVERED_AND_COPIED_READ_ONLY",
        "safety": {
            "read_allowed": True,
            "indexing_allowed": True,
            "candidate_generation_allowed": False,
            "historical_replay_allowed": False,
            "strategy_execution_allowed": False,
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
    "mode": "READ_ONLY_SSRN_DOWNLOADS_DISCOVERY",
    "downloads_dir": str(DOWNLOADS),
    "pdfs_found": len(pdfs),
    "ssrn_like_pdfs_found": len(ssrn_pdfs),
    "sources": sources,
    "checks": {
        "downloads_exists": DOWNLOADS.exists(),
        "ssrn_sources_found": len(ssrn_pdfs) > 0,
        "sources_copied": len(sources) == len(ssrn_pdfs),
        "all_nonempty": all(s["bytes"] > 0 for s in sources),
        "all_sha256_present": all(bool(s["sha256"]) for s in sources),
        "all_execution_blocked": all(s["safety"]["strategy_execution_allowed"] is False for s in sources),
        "all_runtime_blocked": all(s["safety"]["runtime_execution_allowed"] is False for s in sources),
        "all_broker_live_blocked": all(
            s["safety"]["broker_execution_enabled"] is False
            and s["safety"]["live_execution_enabled"] is False
            for s in sources
        ),
    },
    "recommended_next_phase": "65I_MULTI_SOURCE_INDEX_BUILDER",
    "certified": False,
}

result["certified"] = all(result["checks"].values())

OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps({
    "phase": PHASE,
    "ssrn_like_pdfs_found": len(ssrn_pdfs),
    "out": str(OUT),
    "recommended_next_phase": result["recommended_next_phase"],
    "certified": result["certified"],
}, indent=2))

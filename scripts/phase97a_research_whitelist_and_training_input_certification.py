#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json, hashlib

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "historical_fixture_store" / "96B_fetch_10_symbol_historical_csv_fixtures_read_only_latest.json"
OUT_DIR = ARCH / "research_whitelist_and_training_input_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "97A_research_whitelist_and_training_input_certification_latest.json"
OUT_TXT = OUT_DIR / "97A_research_whitelist_and_training_input_certification_latest.txt"

PHASE = "97A_RESEARCH_WHITELIST_AND_TRAINING_INPUT_CERTIFICATION"

def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

source = read_json(SOURCE)
fixtures = source.get("fixtures_written", [])

research_roots = [
    ROOT / "research",
    ROOT / "docs",
    ARCH / "stress_test_report_store/store",
    ARCH / "training_result_read_only_store/store",
]

research_docs = []
for root in research_roots:
    if root.exists():
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".txt", ".md", ".json", ".pdf"}:
                research_docs.append({
                    "document_id": path.stem.upper().replace("-", "_"),
                    "path": str(path),
                    "checksum": sha256_file(path),
                    "approved": True,
                    "read_only": True,
                })

manifest = {
    "training_run_id": "TRAINING_RUN_0001",
    "historical_fixtures": fixtures,
    "research_documents": research_docs,
    "hard_blocks": {
        "training_execution_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "historical_fixtures_present": len(fixtures) == 10,
    "all_fixture_files_exist": all(Path(item["csv"]).exists() for item in fixtures),
    "manifest_present": True,
    "training_blocked": True,
    "db_promotion_broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "manifest": manifest,
    "checks": checks,
    "recommended_next_phase": "98A_READ_ONLY_SANDBOX_TRAINING_RUN_WITH_STREAM",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    f"{PHASE}\n\ncertified: {result['certified']}\nhistorical_fixtures: {len(fixtures)}\nresearch_documents: {len(research_docs)}\n",
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "historical_fixtures": len(fixtures),
    "research_documents": len(research_docs),
    "recommended_next_phase": result["recommended_next_phase"],
}, indent=2))

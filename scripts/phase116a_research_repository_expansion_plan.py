#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "research_input_whitelist_refresh/111A_research_input_whitelist_refresh_latest.json"

PHASE = "116A_RESEARCH_REPOSITORY_EXPANSION_PLAN"

RESEARCH_ROOT = ROOT / "backend/app/stacks/learning_research/research_data"

DIRECTORIES = [
    "equities/canada/raw",
    "equities/canada/metadata",
    "equities/usa/raw",
    "equities/usa/metadata",
    "etfs/raw",
    "etfs/metadata",
    "indexes/raw",
    "indexes/metadata",
    "corporate_actions/splits",
    "corporate_actions/dividends",
    "corporate_actions/symbol_changes",
    "corporate_actions/metadata",
    "macro/fred_canada/raw",
    "macro/fred_canada/metadata",
    "macro/bank_of_canada/raw",
    "macro/bank_of_canada/metadata",
    "macro/fred_us/raw",
    "macro/fred_us/metadata",
    "fundamentals/earnings",
    "fundamentals/balance_sheets",
    "fundamentals/income_statements",
    "fundamentals/cash_flow",
    "news/raw",
    "news/metadata",
    "sentiment/raw",
    "sentiment/metadata",
    "manifests",
    "postgres_preview",
]

for d in DIRECTORIES:
    (RESEARCH_ROOT / d).mkdir(parents=True, exist_ok=True)

DATASET_MANIFEST_SCHEMA = {
    "schema_version": 1,
    "required_fields": [
        "dataset_id",
        "provider",
        "asset_class",
        "country",
        "symbol",
        "interval",
        "date_range",
        "checksum_sha256",
        "approved",
        "read_only",
        "normalized",
        "training_enabled",
        "created_at",
        "updated_at",
    ]
}

(RESEARCH_ROOT / "manifests" / "dataset_manifest_schema.json").write_text(
    json.dumps(DATASET_MANIFEST_SCHEMA, indent=2),
    encoding="utf-8"
)

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source = read_json(SOURCE)

OUT_DIR = ARCH / "research_repository_expansion_plan"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "116A_research_repository_expansion_plan_latest.json"
OUT_TXT = OUT_DIR / "116A_research_repository_expansion_plan_latest.txt"

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "research_root_exists": RESEARCH_ROOT.exists(),
    "directories_created": all((RESEARCH_ROOT / d).exists() for d in DIRECTORIES),
    "manifest_schema_written": (RESEARCH_ROOT / "manifests/dataset_manifest_schema.json").exists(),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "research_root": str(RESEARCH_ROOT),
    "directories": DIRECTORIES,
    "dataset_manifest_schema": DATASET_MANIFEST_SCHEMA,
    "checks": checks,
    "policy": {
        "repository_expanded": True,
        "downloads_executed": False,
        "database_writes": False,
        "training_execution_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "116B_DATASET_PROVIDER_REGISTRY",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"directories_created: {len(DIRECTORIES)}",
        "downloads_executed: False",
        "",
        "Research repository expanded.",
        "Existing repository preserved.",
        "No datasets downloaded.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "directories_created": len(DIRECTORIES),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

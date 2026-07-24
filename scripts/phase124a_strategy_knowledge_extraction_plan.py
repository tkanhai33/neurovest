#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE_PIPELINE = ARCH / "learning_artifact_pipeline_certification/123C_learning_artifact_pipeline_certification_latest.json"
SOURCE_ARCH = ROOT / "runtime/architecture_intelligence_engine/123_summary.json"

OUT_DIR = ARCH / "strategy_knowledge_extraction_plan"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "124A_strategy_knowledge_extraction_plan_latest.json"
OUT_TXT = OUT_DIR / "124A_strategy_knowledge_extraction_plan_latest.txt"

PHASE = "124A_STRATEGY_KNOWLEDGE_EXTRACTION_PLAN"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

pipeline = read_json(SOURCE_PIPELINE)
arch = read_json(SOURCE_ARCH)

plan = {
    "plan_id": "STRATEGY_KNOWLEDGE_EXTRACTION_PLAN_V1",
    "mode": "PLAN_ONLY_NO_FILES_WRITTEN",
    "purpose": "Convert certified learning artifacts and research strategy indexes into structured strategy knowledge objects.",
    "source_inputs": {
        "learning_artifacts": "Produced by learning_artifact_pipeline.py",
        "research_strategy_indexes": "Produced by existing research indexing phases when available",
        "architecture_summary": str(SOURCE_ARCH),
    },
    "target_file_planned": "backend/app/stacks/strategy_candidate_sandbox/strategy_knowledge_object.py",
    "knowledge_object_keys": [
        "knowledge_id",
        "strategy_name",
        "strategy_family",
        "symbols",
        "asset_classes",
        "indicators",
        "regimes",
        "features",
        "evidence",
        "risk_notes",
        "source_artifacts",
        "confidence",
        "safety_locks",
        "created_at",
    ],
    "extraction_rules": {
        "from_learning_artifact": [
            "features",
            "decision",
            "reward",
            "confidence",
            "symbol",
            "date",
        ],
        "from_research_index": [
            "strategy_name",
            "asset_class",
            "source_document",
            "source_page",
            "indicator_mentions",
            "risk_notes",
        ],
        "no_strategy_execution": True,
        "no_db_write": True,
        "no_promotion": True,
        "no_broker_live": True,
    },
    "safety_locks": {
        "database_writes_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
}

checks = {
    "pipeline_source_exists": SOURCE_PIPELINE.exists(),
    "pipeline_certified": pipeline.get("certified") is True,
    "architecture_source_exists": SOURCE_ARCH.exists(),
    "target_file_planned": bool(plan["target_file_planned"]),
    "knowledge_keys_present": len(plan["knowledge_object_keys"]) >= 10,
    "plan_only": plan["mode"] == "PLAN_ONLY_NO_FILES_WRITTEN",
    "db_write_blocked": plan["safety_locks"]["database_writes_allowed"] is False,
    "strategy_db_write_blocked": plan["safety_locks"]["strategy_db_write_allowed"] is False,
    "promotion_blocked": plan["safety_locks"]["promotion_enabled"] is False,
    "broker_live_blocked": (
        plan["safety_locks"]["broker_execution_enabled"] is False
        and plan["safety_locks"]["live_execution_enabled"] is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "plan": plan,
    "checks": checks,
    "recommended_next_phase": "124B_STRATEGY_KNOWLEDGE_OBJECT_STUB",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "mode: PLAN_ONLY_NO_FILES_WRITTEN",
        "",
        "Planned target:",
        plan["target_file_planned"],
        "",
        "Knowledge object will connect:",
        "- learning artifacts",
        "- research strategy indexes",
        "- symbols",
        "- indicators",
        "- regimes",
        "- evidence",
        "",
        "No DB writes. No promotion. No broker/live.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

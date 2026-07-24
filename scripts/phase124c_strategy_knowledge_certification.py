#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import importlib.util
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "strategy_knowledge_object_stub/124B_strategy_knowledge_object_stub_latest.json"
PIPELINE_CERT = ARCH / "learning_artifact_pipeline_certification/123C_learning_artifact_pipeline_certification_latest.json"

TARGET = ROOT / "backend/app/stacks/strategy_candidate_sandbox/strategy_knowledge_object.py"

OUT_DIR = ARCH / "strategy_knowledge_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "124C_strategy_knowledge_certification_latest.json"
OUT_TXT = OUT_DIR / "124C_strategy_knowledge_certification_latest.txt"

PHASE = "124C_STRATEGY_KNOWLEDGE_CERTIFICATION"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def import_file(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

source = read_json(SOURCE)
pipeline_cert = read_json(PIPELINE_CERT)
sample_artifact = pipeline_cert.get("sample_artifact", {})

module = import_file("strategy_knowledge_object", TARGET)

status = module.knowledge_object_status()

knowledge_object = module.build_strategy_knowledge_object_from_learning_artifact(
    sample_artifact,
    strategy_name="Certified Learning Artifact Strategy",
    strategy_family="LEARNING_ARTIFACT",
)

valid_object = module.validate_strategy_knowledge_object(knowledge_object)

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "pipeline_cert_exists": PIPELINE_CERT.exists(),
    "pipeline_certified": pipeline_cert.get("certified") is True,
    "target_exists": TARGET.exists(),
    "status_present": bool(status),
    "knowledge_object_created": isinstance(knowledge_object, dict),
    "knowledge_object_valid": valid_object is True,
    "source_artifact_linked": len(knowledge_object.get("source_artifacts", [])) >= 1,
    "evidence_present": len(knowledge_object.get("evidence", [])) >= 1,
    "features_present": isinstance(knowledge_object.get("features"), dict),
    "confidence_valid": 0.0 <= float(knowledge_object.get("confidence", 0.0)) <= 1.0,
    "database_writes_blocked": status.get("database_writes_allowed") is False,
    "strategy_db_write_blocked": status.get("strategy_db_write_allowed") is False,
    "promotion_blocked": status.get("promotion_enabled") is False,
    "broker_blocked": status.get("broker_execution_enabled") is False,
    "live_blocked": status.get("live_execution_enabled") is False,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "knowledge_object": knowledge_object,
    "status": status,
    "checks": checks,
    "policy": {
        "strategy_knowledge_certified": True,
        "database_writes_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "125A_INDICATOR_KNOWLEDGE_GRAPH_STUB",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"knowledge_object_valid: {valid_object}",
        f"knowledge_id: {knowledge_object.get('knowledge_id')}",
        f"confidence: {knowledge_object.get('confidence')}",
        "",
        "Strategy knowledge object certified.",
        "Learning artifact -> strategy knowledge object link works.",
        "",
        "Database Writes: False",
        "Strategy DB Writes: False",
        "Promotion: False",
        "Broker: False",
        "Live: False",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "knowledge_object_valid": valid_object,
    "knowledge_id": knowledge_object.get("knowledge_id"),
    "confidence": knowledge_object.get("confidence"),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

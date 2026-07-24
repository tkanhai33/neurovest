#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import importlib.util
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "learning_artifact_pipeline_stub/123B_learning_artifact_pipeline_stub_latest.json"
PIPELINE = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/learning_artifact_pipeline.py"
CONTRACT = ROOT / "backend/app/stacks/strategy_candidate_sandbox/learning_artifact_contract.py"

OUT_DIR = ARCH / "learning_artifact_pipeline_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "123C_learning_artifact_pipeline_certification_latest.json"
OUT_TXT = OUT_DIR / "123C_learning_artifact_pipeline_certification_latest.txt"

PHASE = "123C_LEARNING_ARTIFACT_PIPELINE_CERTIFICATION"

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
pipeline = import_file("learning_artifact_pipeline", PIPELINE)
contract = import_file("learning_artifact_contract", CONTRACT)

sample_row = {
    "symbol": "TEST",
    "date": "2026-07-08",
    "open": 100.0,
    "high": 105.0,
    "low": 99.0,
    "close": 104.0,
    "volume": 1000000,
}

artifact = pipeline.build_learning_artifact(
    run_id="CERT_123C",
    symbol="TEST",
    row=sample_row,
    previous_close=101.0,
    next_close=106.0,
    decision="BUY",
    cycle=1,
)

status = pipeline.pipeline_status()
valid_artifact = contract.validate_learning_artifact_contract(artifact)

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "pipeline_exists": PIPELINE.exists(),
    "contract_exists": CONTRACT.exists(),
    "status_present": bool(status),
    "pipeline_enabled": status.get("pipeline_enabled") is True,
    "artifact_created": isinstance(artifact, dict),
    "artifact_valid": valid_artifact is True,
    "features_present": isinstance(artifact.get("features"), dict),
    "reward_present": artifact.get("reward") is not None,
    "confidence_present": artifact.get("confidence") is not None,
    "database_writes_blocked": status.get("database_writes_allowed") is False,
    "strategy_db_write_blocked": status.get("strategy_db_write_allowed") is False,
    "promotion_blocked": status.get("promotion_enabled") is False,
    "broker_blocked": status.get("broker_execution_enabled") is False,
    "live_blocked": status.get("live_execution_enabled") is False,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "sample_artifact": artifact,
    "pipeline_status": status,
    "checks": checks,
    "policy": {
        "learning_artifact_pipeline_certified": True,
        "database_writes_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "124A_STRATEGY_KNOWLEDGE_EXTRACTION_PLAN",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"artifact_valid: {valid_artifact}",
        f"reward: {artifact.get('reward')}",
        f"confidence: {artifact.get('confidence')}",
        "",
        "Pipeline certified:",
        "Replay Row -> Features -> Reward -> Learning Artifact",
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
    "artifact_valid": valid_artifact,
    "reward": artifact.get("reward"),
    "confidence": artifact.get("confidence"),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

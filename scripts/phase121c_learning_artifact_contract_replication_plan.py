#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "contract_shape_inspection/121B_contract_shape_inspection_latest.json"

OUT_DIR = ARCH / "learning_artifact_contract_replication_plan"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "121C_learning_artifact_contract_replication_plan_latest.json"
OUT_TXT = OUT_DIR / "121C_learning_artifact_contract_replication_plan_latest.txt"

PHASE = "121C_LEARNING_ARTIFACT_CONTRACT_REPLICATION_PLAN"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source = read_json(SOURCE)
shapes = source.get("high_value_shapes", [])

replication_sources = [
    "backend/app/stacks/strategy_candidate_sandbox/replay_metrics_contract.py",
    "backend/app/stacks/strategy_candidate_sandbox/trade_simulation_contract.py",
    "backend/app/stacks/strategy_candidate_sandbox/candidate_scorecard_from_replay_metrics.py",
    "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/training_read_only_learner.py",
    "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/eight_hour_training_stream.py",
]

found = {
    path: any(shape.get("path") == path for shape in shapes)
    for path in replication_sources
}

plan = {
    "plan_id": "LEARNING_ARTIFACT_CONTRACT_REPLICATION_PLAN_V1",
    "mode": "PLAN_ONLY_NO_FILES_WRITTEN",
    "replicate_style_from": replication_sources,
    "target_files_planned": [
        "backend/app/stacks/strategy_candidate_sandbox/learning_artifact_contract.py",
        "backend/app/stacks/strategy_candidate_sandbox/learning_feature_extractor.py",
        "backend/app/stacks/strategy_candidate_sandbox/learning_reward_scorer.py",
        "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/learning_artifact_pipeline.py",
    ],
    "artifact_contract_keys": [
        "artifact_id",
        "run_id",
        "symbol",
        "date",
        "cycle",
        "features",
        "decision",
        "reward",
        "confidence",
        "source",
        "safety_locks",
    ],
    "safety_locks": {
        "database_writes_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
        "source_csv_modification_allowed": False,
    },
    "next_build_order": [
        "121D_LEARNING_ARTIFACT_CONTRACT_STUB",
        "121E_LEARNING_FEATURE_EXTRACTOR_STUB",
        "121F_LEARNING_REWARD_SCORER_STUB",
        "121G_LEARNING_ARTIFACT_PIPELINE_STUB",
    ],
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "replication_sources_found": all(found.values()),
    "target_files_planned": len(plan["target_files_planned"]) == 4,
    "artifact_keys_present": len(plan["artifact_contract_keys"]) >= 10,
    "db_write_blocked": plan["safety_locks"]["database_writes_allowed"] is False,
    "strategy_db_write_blocked": plan["safety_locks"]["strategy_db_write_allowed"] is False,
    "promotion_blocked": plan["safety_locks"]["promotion_enabled"] is False,
    "broker_live_blocked": (
        plan["safety_locks"]["broker_execution_enabled"] is False
        and plan["safety_locks"]["live_execution_enabled"] is False
    ),
    "no_files_written_mode": plan["mode"] == "PLAN_ONLY_NO_FILES_WRITTEN",
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "replication_sources_found": found,
    "plan": plan,
    "checks": checks,
    "recommended_next_phase": "121D_LEARNING_ARTIFACT_CONTRACT_STUB",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "replication_sources_found:",
        *[f"- {k}: {v}" for k, v in found.items()],
        "",
        "Target files planned:",
        *[f"- {p}" for p in plan["target_files_planned"]],
        "",
        "No files written yet.",
        "No DB writes. No training mutation. No broker/live.",
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

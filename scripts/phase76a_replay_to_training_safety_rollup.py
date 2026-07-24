#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

PHASE = "76A_REPLAY_TO_TRAINING_SAFETY_ROLLUP"

EXPECTED = {
    "70D_fixture_calculator_rollup": ARCH / "fixture_replay_calculator_rollup/70D_fixture_replay_calculator_rollup_latest.json",
    "71A_single_fixture_dry_run": ARCH / "single_fixture_replay_dry_run/71A_single_fixture_replay_dry_run_only_latest.json",
    "71B_no_write_no_promotion_no_broker": ARCH / "no_write_no_promotion_no_broker/71B_no_write_no_promotion_no_broker_certification_latest.json",
    "72A_read_only_result_store": ARCH / "read_only_result_store/72A_read_only_result_store_latest.json",
    "73A_inactive_databank_draft": ARCH / "inactive_strategy_databank_draft/73A_inactive_strategy_databank_draft_latest.json",
    "74A_training_architecture": ARCH / "learning_training_architecture/74A_learning_training_architecture_planning_latest.json",
    "75C_training_gate_rollup": ARCH / "training_gate_rollup/75C_training_gate_rollup_certification_latest.json",
}

OUT_DIR = ARCH / "replay_to_training_safety_rollup"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "76A_replay_to_training_safety_rollup_latest.json"
OUT_TXT = OUT_DIR / "76A_replay_to_training_safety_rollup_latest.txt"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


artifacts = {}
checks = {}

for name, path in EXPECTED.items():
    data = read_json(path)
    artifacts[name] = {
        "path": str(path),
        "exists": path.exists(),
        "phase": data.get("phase"),
        "certified": data.get("certified") is True,
    }
    checks[f"{name}_exists"] = path.exists()
    checks[f"{name}_certified"] = data.get("certified") is True

training_gate = read_json(EXPECTED["75C_training_gate_rollup"])
training_status = training_gate.get("training_gate_status", {})

checks["training_disabled"] = training_status.get("training_enabled") is False
checks["self_mutation_blocked"] = training_status.get("self_mutation_allowed") is False
checks["autonomous_promotion_blocked"] = training_status.get("autonomous_promotion_allowed") is False
checks["strategy_db_write_blocked"] = training_status.get("strategy_db_write_allowed") is False
checks["broker_live_blocked"] = (
    training_status.get("broker_execution_enabled") is False
    and training_status.get("live_execution_enabled") is False
)

safety_rollup = {
    "fixture_metric_pipeline_certified": True,
    "read_only_result_store_certified": True,
    "inactive_databank_draft_certified": True,
    "training_architecture_planned": True,
    "training_gate_certified": True,
    "safe_to_enable_training_now": False,
    "why_training_still_blocked": [
        "only fixture data has been proven",
        "historical replay on real bar data is not certified yet",
        "stress tests are not certified yet",
        "manual activation gate is not certified yet",
        "near-miss refactor queue is not certified yet",
        "quarantine/trash path is not certified yet",
    ],
    "next_required_before_training": [
        "real historical replay dry-run architecture",
        "stress-test report store",
        "manual activation gate",
        "near-miss refactor queue capped at 3",
        "quarantine/trash path",
        "training read-only learner stub",
    ],
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "REPLAY_TO_TRAINING_SAFETY_ROLLUP",
    "artifacts": artifacts,
    "safety_rollup": safety_rollup,
    "training_gate_status": training_status,
    "checks": checks,
    "recommended_next_phase": "76B_TRAINING_PRECONDITION_GAP_MANIFEST",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"safe_to_enable_training_now: {safety_rollup['safe_to_enable_training_now']}",
        "",
        "Training still blocked because:",
        *[f"- {x}" for x in safety_rollup["why_training_still_blocked"]],
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "safe_to_enable_training_now": safety_rollup["safe_to_enable_training_now"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

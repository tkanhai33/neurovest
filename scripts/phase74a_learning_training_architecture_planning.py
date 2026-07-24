#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "inactive_strategy_databank_draft" / "73A_inactive_strategy_databank_draft_latest.json"

OUT_DIR = ARCH / "learning_training_architecture"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "74A_learning_training_architecture_planning_latest.json"
OUT_TXT = OUT_DIR / "74A_learning_training_architecture_planning_latest.txt"

PHASE = "74A_LEARNING_TRAINING_ARCHITECTURE_PLANNING"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

training_architecture = {
    "mode": "ARCHITECTURE_PLANNING_ONLY",
    "training_goal": "allow future controlled learning from certified replay results without self-promotion",
    "required_preconditions_before_training": [
        "historical replay certified on real bar data",
        "read-only result store certified",
        "inactive strategy databank certified",
        "manual activation gate certified",
        "near-miss refactor queue capped at 3 attempts",
        "trash/quarantine path certified",
        "no broker/live execution certified",
    ],
    "allowed_future_learning_inputs": [
        "certified replay metrics",
        "certified stress test reports",
        "manual review labels",
        "inactive databank records",
    ],
    "forbidden_training_inputs": [
        "live broker orders",
        "unverified strategy output",
        "uncertified candidate mutations",
        "raw LLM suggestions without replay proof",
    ],
    "future_training_flow": [
        "read certified replay result",
        "read manual label",
        "compare candidate behavior",
        "suggest controlled refactor",
        "send refactor to review queue",
        "never self-promote",
    ],
    "hard_gates": {
        "training_enabled_now": False,
        "self_mutation_allowed": False,
        "autonomous_promotion_allowed": False,
        "strategy_db_write_allowed": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "architecture_present": bool(training_architecture),
    "planning_only": training_architecture["mode"] == "ARCHITECTURE_PLANNING_ONLY",
    "training_disabled_now": training_architecture["hard_gates"]["training_enabled_now"] is False,
    "self_mutation_blocked": training_architecture["hard_gates"]["self_mutation_allowed"] is False,
    "autonomous_promotion_blocked": training_architecture["hard_gates"]["autonomous_promotion_allowed"] is False,
    "strategy_db_write_blocked": training_architecture["hard_gates"]["strategy_db_write_allowed"] is False,
    "broker_live_blocked": (
        training_architecture["hard_gates"]["broker_execution_enabled"] is False
        and training_architecture["hard_gates"]["live_execution_enabled"] is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "LEARNING_TRAINING_ARCHITECTURE_PLANNING_ONLY",
    "source_inactive_databank_draft": str(SOURCE),
    "training_architecture": training_architecture,
    "checks": checks,
    "recommended_next_phase": "75A_TRAINING_GATE_STUB",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "",
        "Training remains blocked:",
        "- training_enabled_now: False",
        "- self_mutation_allowed: False",
        "- autonomous_promotion_allowed: False",
        "- broker/live: False",
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

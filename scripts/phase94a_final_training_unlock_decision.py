#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

PHASE = "94A_FINAL_TRAINING_UNLOCK_DECISION"

EXPECTED = {
    "91A_no_db_no_promotion_no_broker": ARCH / "no_db_no_promotion_no_broker_certification/91A_no_db_no_promotion_no_broker_certification_latest.json",
    "92A_training_result_store": ARCH / "training_result_read_only_store/92A_training_result_read_only_store_latest.json",
    "93A_rollback_relock_gate": ARCH / "rollback_relock_gate/93A_rollback_relock_gate_latest.json",
}

OUT_DIR = ARCH / "final_training_unlock_decision"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "94A_final_training_unlock_decision_latest.json"
OUT_TXT = OUT_DIR / "94A_final_training_unlock_decision_latest.txt"


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

relock = read_json(EXPECTED["93A_rollback_relock_gate"])
policy = relock.get("policy", {})

decision = {
    "decision": "DO_NOT_ENABLE_DB_WRITES_OR_TRAINING_EXECUTION",
    "safe_to_write_strategy_db_now": False,
    "safe_to_promote_candidates_now": False,
    "safe_to_execute_broker_or_live_now": False,
    "safe_next_lane": "95A_10_SYMBOL_10_YEAR_HISTORICAL_DATA_MANIFEST",
    "reason": [
        "single-symbol read-only inspection lane is certified",
        "training result was stored read-only",
        "system was relocked after inspection",
        "multi-symbol historical data is not certified yet",
        "document/research input whitelist is not certified yet",
        "combined symbols plus documents training dry-run is not certified yet",
    ],
}

checks["read_only_learner_relocked"] = policy.get("read_only_learner_enabled") is False
checks["training_execution_relocked"] = policy.get("training_execution_enabled") is False
checks["learner_write_blocked"] = policy.get("learner_write_enabled") is False
checks["mutation_blocked"] = policy.get("mutation_allowed") is False
checks["queue_write_blocked"] = policy.get("queue_write_enabled") is False
checks["strategy_db_write_blocked"] = policy.get("strategy_db_write_allowed") is False
checks["promotion_blocked"] = policy.get("promotion_enabled") is False
checks["broker_live_blocked"] = (
    policy.get("broker_execution_enabled") is False
    and policy.get("live_execution_enabled") is False
)
checks["decision_blocks_db_writes"] = decision["safe_to_write_strategy_db_now"] is False
checks["decision_blocks_promotion"] = decision["safe_to_promote_candidates_now"] is False
checks["decision_blocks_broker_live"] = decision["safe_to_execute_broker_or_live_now"] is False

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "FINAL_TRAINING_UNLOCK_DECISION",
    "artifacts": artifacts,
    "decision": decision,
    "checks": checks,
    "policy": {
        "final_training_unlock_decision_certified": True,
        "training_execution_enabled": False,
        "read_only_learner_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "95A_10_SYMBOL_10_YEAR_HISTORICAL_DATA_MANIFEST",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"decision: {decision['decision']}",
        "safe_to_write_strategy_db_now: False",
        "safe_to_promote_candidates_now: False",
        "safe_to_execute_broker_or_live_now: False",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "decision": decision["decision"],
    "safe_to_write_strategy_db_now": False,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json
import py_compile

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "training_result_read_only_store" / "92A_training_result_read_only_store_latest.json"
LEARNER = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/training_read_only_learner.py"
GATE = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L1_security_auth_safety/training_execution_gate.py"

OUT_DIR = ARCH / "rollback_relock_gate"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "93A_rollback_relock_gate_latest.json"
OUT_TXT = OUT_DIR / "93A_rollback_relock_gate_latest.txt"

PHASE = "93A_ROLLBACK_RELOCK_GATE"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

# Relock learner inspection back to disabled after read-only inspection lane.
learner_text = LEARNER.read_text(encoding="utf-8")
learner_text = learner_text.replace("READ_ONLY_LEARNER_ENABLED = True", "READ_ONLY_LEARNER_ENABLED = False")
LEARNER.write_text(learner_text, encoding="utf-8")

# Ensure training execution gate remains locked.
gate_text = GATE.read_text(encoding="utf-8")
gate_text = gate_text.replace("TRAINING_EXECUTION_ENABLED = True", "TRAINING_EXECUTION_ENABLED = False")
gate_text = gate_text.replace("LEARNER_WRITE_ENABLED = True", "LEARNER_WRITE_ENABLED = False")
gate_text = gate_text.replace("MUTATION_ALLOWED = True", "MUTATION_ALLOWED = False")
gate_text = gate_text.replace("QUEUE_WRITE_ENABLED = True", "QUEUE_WRITE_ENABLED = False")
gate_text = gate_text.replace("STRATEGY_DB_WRITE_ALLOWED = True", "STRATEGY_DB_WRITE_ALLOWED = False")
gate_text = gate_text.replace("PROMOTION_ENABLED = True", "PROMOTION_ENABLED = False")
gate_text = gate_text.replace("BROKER_EXECUTION_ENABLED = True", "BROKER_EXECUTION_ENABLED = False")
gate_text = gate_text.replace("LIVE_EXECUTION_ENABLED = True", "LIVE_EXECUTION_ENABLED = False")
GATE.write_text(gate_text, encoding="utf-8")

compile_errors = []
compile_ok = True

for path in [LEARNER, GATE]:
    try:
        py_compile.compile(str(path), doraise=True)
    except Exception as exc:
        compile_ok = False
        compile_errors.append({
            "file": str(path),
            "type": type(exc).__name__,
            "message": str(exc),
        })

learner_after = LEARNER.read_text(encoding="utf-8")
gate_after = GATE.read_text(encoding="utf-8")

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "learner_exists": LEARNER.exists(),
    "gate_exists": GATE.exists(),
    "compile_ok": compile_ok,
    "read_only_learner_relocked": "READ_ONLY_LEARNER_ENABLED = False" in learner_after,
    "training_execution_relocked": "TRAINING_EXECUTION_ENABLED = False" in gate_after,
    "learner_write_blocked": "LEARNER_WRITE_ENABLED = False" in gate_after,
    "mutation_blocked": "MUTATION_ALLOWED = False" in gate_after,
    "queue_write_blocked": "QUEUE_WRITE_ENABLED = False" in gate_after,
    "strategy_db_write_blocked": "STRATEGY_DB_WRITE_ALLOWED = False" in gate_after,
    "promotion_blocked": "PROMOTION_ENABLED = False" in gate_after,
    "broker_live_blocked": (
        "BROKER_EXECUTION_ENABLED = False" in gate_after
        and "LIVE_EXECUTION_ENABLED = False" in gate_after
    ),
    "no_compile_errors": len(compile_errors) == 0,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "ROLLBACK_RELOCK_GATE",
    "source_read_only_store": str(SOURCE),
    "learner_file": str(LEARNER),
    "training_execution_gate_file": str(GATE),
    "compile_errors": compile_errors,
    "checks": checks,
    "policy": {
        "rollback_relock_gate_certified": True,
        "read_only_learner_enabled": False,
        "training_execution_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "94A_FINAL_TRAINING_UNLOCK_DECISION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"compile_ok: {compile_ok}",
        "read_only_learner_enabled: False",
        "training_execution_enabled: False",
        "",
        "System relocked.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "compile_ok": compile_ok,
    "read_only_learner_enabled": False,
    "training_execution_enabled": False,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

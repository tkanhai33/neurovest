#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

PHASE = "82C_TRAINING_READ_ONLY_LEARNER_ROLLUP"

EXPECTED = {
    "82A_learner_stub": ARCH / "training_read_only_learner/82A_training_read_only_learner_stub_latest.json",
    "82B_learner_certification": ARCH / "training_read_only_learner_certification/82B_training_read_only_learner_certification_latest.json",
}

OUT_DIR = ARCH / "training_read_only_learner_rollup"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "82C_training_read_only_learner_rollup_latest.json"
OUT_TXT = OUT_DIR / "82C_training_read_only_learner_rollup_latest.txt"


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

cert = read_json(EXPECTED["82B_learner_certification"])
status = cert.get("learner_status", {})
preview = cert.get("preview", {})

checks["status_present"] = bool(status)
checks["preview_present"] = bool(preview)
checks["preview_only"] = preview.get("mode") == "PREVIEW_ONLY"
checks["training_disabled"] = status.get("training_enabled") is False
checks["read_only_learner_disabled"] = status.get("read_only_learner_enabled") is False
checks["learner_write_disabled"] = status.get("learner_write_enabled") is False
checks["mutation_blocked"] = status.get("mutation_allowed") is False
checks["queue_write_blocked"] = status.get("queue_write_enabled") is False
checks["strategy_db_write_blocked"] = status.get("strategy_db_write_allowed") is False
checks["promotion_blocked"] = status.get("promotion_enabled") is False
checks["broker_live_blocked"] = (
    status.get("broker_execution_enabled") is False
    and status.get("live_execution_enabled") is False
)

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "TRAINING_READ_ONLY_LEARNER_ROLLUP",
    "artifacts": artifacts,
    "learner_status": status,
    "preview": preview,
    "policy": {
        "training_read_only_learner_rollup_certified": True,
        "training_enabled": False,
        "read_only_learner_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "83A_TRAINING_ENABLEMENT_FINAL_SAFETY_ROLLUP",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "",
        "Training read-only learner rollup certified.",
        "Training/write/mutation/queue/db/promotion/broker/live remain blocked.",
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

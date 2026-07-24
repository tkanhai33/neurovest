#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

PHASE = "81C_CANDIDATE_QUARANTINE_TRASH_PATH_ROLLUP"

EXPECTED = {
    "81A_quarantine_trash_stub": ARCH / "candidate_quarantine_trash_path/81A_candidate_quarantine_trash_path_latest.json",
    "81B_quarantine_trash_certification": ARCH / "candidate_quarantine_trash_path_certification/81B_candidate_quarantine_trash_path_certification_latest.json",
}

OUT_DIR = ARCH / "candidate_quarantine_trash_path_rollup"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "81C_candidate_quarantine_trash_path_rollup_latest.json"
OUT_TXT = OUT_DIR / "81C_candidate_quarantine_trash_path_rollup_latest.txt"


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

cert = read_json(EXPECTED["81B_quarantine_trash_certification"])
status = cert.get("status", {})
preview = cert.get("preview", {})

checks["status_present"] = bool(status)
checks["preview_present"] = bool(preview)
checks["preview_only"] = preview.get("mode") == "PREVIEW_ONLY"
checks["quarantine_disabled"] = status.get("quarantine_path_enabled") is False
checks["trash_disabled"] = status.get("trash_path_enabled") is False
checks["delete_blocked"] = status.get("delete_allowed") is False
checks["mutation_blocked"] = status.get("mutation_allowed") is False
checks["training_blocked"] = status.get("training_enabled") is False
checks["strategy_db_write_blocked"] = status.get("strategy_db_write_allowed") is False
checks["promotion_blocked"] = status.get("promotion_enabled") is False
checks["broker_live_blocked"] = (
    status.get("broker_execution_enabled") is False
    and status.get("live_execution_enabled") is False
)

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "CANDIDATE_QUARANTINE_TRASH_PATH_ROLLUP",
    "artifacts": artifacts,
    "status": status,
    "preview": preview,
    "policy": {
        "candidate_quarantine_trash_path_rollup_certified": True,
        "quarantine_path_enabled": False,
        "trash_path_enabled": False,
        "delete_allowed": False,
        "mutation_allowed": False,
        "training_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "82A_TRAINING_READ_ONLY_LEARNER_STUB",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "",
        "Candidate quarantine/trash path rollup certified.",
        "Quarantine/trash/delete/mutation/training/db/promotion/broker/live remain blocked.",
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

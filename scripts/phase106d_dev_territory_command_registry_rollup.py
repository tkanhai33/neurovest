#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

PHASE = "106D_DEV_TERRITORY_COMMAND_REGISTRY_ROLLUP"

EXPECTED = {
    "106A_preview": ARCH / "dev_territory_command_registry_preview/106A_dev_territory_command_registry_preview_latest.json",
    "106B_stub": ARCH / "dev_territory_command_registry/106B_dev_territory_command_registry_stub_latest.json",
    "106C_certification": ARCH / "dev_territory_command_registry_certification/106C_dev_territory_command_registry_certification_latest.json",
}

OUT_DIR = ARCH / "dev_territory_command_registry_rollup"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "106D_dev_territory_command_registry_rollup_latest.json"
OUT_TXT = OUT_DIR / "106D_dev_territory_command_registry_rollup_latest.txt"


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

cert = read_json(EXPECTED["106C_certification"])
status = cert.get("registry_status", {})

checks["command_count_7"] = cert.get("command_count") == 7
checks["doctrine_present"] = cert.get("doctrine_present") is True
checks["registry_disabled"] = status.get("dev_territory_registry_enabled") is False
checks["runtime_write_blocked"] = status.get("registry_write_to_runtime_enabled") is False
checks["training_blocked"] = status.get("training_execution_enabled") is False
checks["learner_write_blocked"] = status.get("learner_write_enabled") is False
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
    "mode": "DEV_TERRITORY_COMMAND_REGISTRY_ROLLUP",
    "artifacts": artifacts,
    "registry_status": status,
    "command_count": cert.get("command_count"),
    "doctrine_present": cert.get("doctrine_present"),
    "checks": checks,
    "policy": {
        "dev_territory_command_registry_rollup_certified": True,
        "dev_territory_registry_enabled": False,
        "registry_write_to_runtime_enabled": False,
        "training_execution_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "107A_DEV_TERRITORY_COMMAND_ACTIVATION_PREVIEW",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"command_count: {result['command_count']}",
        f"doctrine_present: {result['doctrine_present']}",
        "",
        "Dev territory command registry rollup certified.",
        "Registry/runtime/training/db/mutation/promotion/broker/live remain blocked.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "command_count": result["command_count"],
    "doctrine_present": result["doctrine_present"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

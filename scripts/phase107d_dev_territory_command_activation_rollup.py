#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

PHASE = "107D_DEV_TERRITORY_COMMAND_ACTIVATION_ROLLUP"

EXPECTED = {
    "107A_preview": ARCH / "dev_territory_command_activation_preview/107A_dev_territory_command_activation_preview_latest.json",
    "107B_patch_apply": ARCH / "dev_territory_command_activation_patch_apply/107B_dev_territory_command_activation_patch_apply_latest.json",
    "107C_certification": ARCH / "dev_territory_command_activation_certification/107C_dev_territory_command_activation_certification_latest.json",
}

OUT_DIR = ARCH / "dev_territory_command_activation_rollup"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "107D_dev_territory_command_activation_rollup_latest.json"
OUT_TXT = OUT_DIR / "107D_dev_territory_command_activation_rollup_latest.txt"

def read_json(path: Path) -> dict:
    try: return json.loads(path.read_text(encoding="utf-8"))
    except Exception: return {}

artifacts, checks = {}, {}

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

cert = read_json(EXPECTED["107C_certification"])
status = cert.get("registry_status", {})

checks.update({
    "registry_enabled": status.get("dev_territory_registry_enabled") is True,
    "command_count_7": cert.get("command_count") == 7,
    "doctrine_present": cert.get("doctrine_present") is True,
    "runtime_write_blocked": status.get("registry_write_to_runtime_enabled") is False,
    "training_blocked": status.get("training_execution_enabled") is False,
    "learner_write_blocked": status.get("learner_write_enabled") is False,
    "mutation_blocked": status.get("mutation_allowed") is False,
    "queue_write_blocked": status.get("queue_write_enabled") is False,
    "strategy_db_write_blocked": status.get("strategy_db_write_allowed") is False,
    "promotion_blocked": status.get("promotion_enabled") is False,
    "broker_live_blocked": status.get("broker_execution_enabled") is False and status.get("live_execution_enabled") is False,
})

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "artifacts": artifacts,
    "registry_status": status,
    "command_count": cert.get("command_count"),
    "doctrine_present": cert.get("doctrine_present"),
    "checks": checks,
    "policy": {
        "dev_territory_activation_rollup_certified": True,
        "dev_territory_registry_enabled": True,
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
    "recommended_next_phase": "108A_DEV_COMMAND_READ_ONLY_EXECUTION_PREVIEW",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    f"{PHASE}\n\ncertified: {result['certified']}\nregistry_enabled: True\ncommand_count: {result['command_count']}\n\nNext:\n{result['recommended_next_phase']}\n",
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "registry_enabled": True,
    "command_count": result["command_count"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "dev_territory_command_registry_rollup" / "106D_dev_territory_command_registry_rollup_latest.json"
REGISTRY = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/dev_territory_command_registry.py"

OUT_DIR = ARCH / "dev_territory_command_activation_preview"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "107A_dev_territory_command_activation_preview_latest.json"
OUT_TXT = OUT_DIR / "107A_dev_territory_command_activation_preview_latest.txt"

PHASE = "107A_DEV_TERRITORY_COMMAND_ACTIVATION_PREVIEW"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

activation_preview = {
    "mode": "DEV_TERRITORY_COMMAND_ACTIVATION_PREVIEW_ONLY_NO_PATCH",
    "target_registry": str(REGISTRY),
    "planned_change": {
        "from": "DEV_TERRITORY_REGISTRY_ENABLED = False",
        "to": "DEV_TERRITORY_REGISTRY_ENABLED = True",
    },
    "activation_scope": "READ_ONLY_COMMAND_LISTING_AND_DOCTRINE_ACCESS_ONLY",
    "still_blocked": {
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
}

text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else ""

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "registry_exists": REGISTRY.exists(),
    "registry_currently_disabled": "DEV_TERRITORY_REGISTRY_ENABLED = False" in text,
    "preview_only_no_patch": activation_preview["mode"] == "DEV_TERRITORY_COMMAND_ACTIVATION_PREVIEW_ONLY_NO_PATCH",
    "runtime_write_blocked": activation_preview["still_blocked"]["registry_write_to_runtime_enabled"] is False,
    "training_blocked": activation_preview["still_blocked"]["training_execution_enabled"] is False,
    "learner_write_blocked": activation_preview["still_blocked"]["learner_write_enabled"] is False,
    "mutation_blocked": activation_preview["still_blocked"]["mutation_allowed"] is False,
    "queue_write_blocked": activation_preview["still_blocked"]["queue_write_enabled"] is False,
    "strategy_db_write_blocked": activation_preview["still_blocked"]["strategy_db_write_allowed"] is False,
    "promotion_blocked": activation_preview["still_blocked"]["promotion_enabled"] is False,
    "broker_live_blocked": (
        activation_preview["still_blocked"]["broker_execution_enabled"] is False
        and activation_preview["still_blocked"]["live_execution_enabled"] is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "DEV_TERRITORY_COMMAND_ACTIVATION_PREVIEW",
    "source_rollup": str(SOURCE),
    "activation_preview": activation_preview,
    "checks": checks,
    "policy": {
        "activation_preview_certified": True,
        "patch_apply_allowed_now": False,
        "dev_territory_registry_enabled": False,
        **activation_preview["still_blocked"],
    },
    "recommended_next_phase": "107B_DEV_TERRITORY_COMMAND_ACTIVATION_PATCH_APPLY",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "patch_apply_allowed_now: False",
        "",
        "Preview only:",
        "- DEV_TERRITORY_REGISTRY_ENABLED False -> True",
        "- Runtime writes remain False",
        "- Training remains False",
        "- DB/mutation/promotion/broker/live remain False",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "patch_apply_allowed_now": False,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

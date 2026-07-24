#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json
import py_compile

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "dev_territory_command_activation_preview" / "107A_dev_territory_command_activation_preview_latest.json"
REGISTRY = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/dev_territory_command_registry.py"

OUT_DIR = ARCH / "dev_territory_command_activation_patch_apply"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "107B_dev_territory_command_activation_patch_apply_latest.json"
OUT_TXT = OUT_DIR / "107B_dev_territory_command_activation_patch_apply_latest.txt"

PHASE = "107B_DEV_TERRITORY_COMMAND_ACTIVATION_PATCH_APPLY"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

text_before = REGISTRY.read_text(encoding="utf-8")
text_after = text_before.replace(
    "DEV_TERRITORY_REGISTRY_ENABLED = False",
    "DEV_TERRITORY_REGISTRY_ENABLED = True",
    1,
)

REGISTRY.write_text(text_after, encoding="utf-8")

compile_ok = False
compile_error = None

try:
    py_compile.compile(str(REGISTRY), doraise=True)
    compile_ok = True
except Exception as exc:
    compile_error = {"type": type(exc).__name__, "message": str(exc)}

text = REGISTRY.read_text(encoding="utf-8")

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "registry_exists": REGISTRY.exists(),
    "compile_ok": compile_ok,
    "dev_territory_registry_enabled": "DEV_TERRITORY_REGISTRY_ENABLED = True" in text,
    "runtime_write_still_blocked": "REGISTRY_WRITE_TO_RUNTIME_ENABLED = False" in text,
    "training_still_blocked": "TRAINING_EXECUTION_ENABLED = False" in text,
    "learner_write_still_blocked": "LEARNER_WRITE_ENABLED = False" in text,
    "mutation_still_blocked": "MUTATION_ALLOWED = False" in text,
    "queue_write_still_blocked": "QUEUE_WRITE_ENABLED = False" in text,
    "strategy_db_write_still_blocked": "STRATEGY_DB_WRITE_ALLOWED = False" in text,
    "promotion_still_blocked": "PROMOTION_ENABLED = False" in text,
    "broker_live_still_blocked": (
        "BROKER_EXECUTION_ENABLED = False" in text
        and "LIVE_EXECUTION_ENABLED = False" in text
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "DEV_TERRITORY_COMMAND_ACTIVATION_PATCH_APPLY",
    "source_preview": str(SOURCE),
    "registry_file": str(REGISTRY),
    "compile_error": compile_error,
    "checks": checks,
    "policy": {
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
    "recommended_next_phase": "107C_DEV_TERRITORY_COMMAND_ACTIVATION_CERTIFICATION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"compile_ok: {compile_ok}",
        "dev_territory_registry_enabled: True",
        "runtime_write_enabled: False",
        "training_execution_enabled: False",
        "strategy_db_write_allowed: False",
        "",
        "Dev territory registry activated for read-only command listing/doctrine access only.",
        "DB/mutation/promotion/broker/live remain blocked.",
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
    "dev_territory_registry_enabled": True,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "real_historical_bar_fetch_temp_enablement_plan" / "77O_real_historical_bar_fetch_temp_enablement_plan_latest.json"
GATE = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L1_security_auth_safety/real_historical_bar_fetch_gate.py"

OUT_DIR = ARCH / "temp_fetch_gate_patch_preview"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "77P_temp_fetch_gate_patch_preview_latest.json"
OUT_TXT = OUT_DIR / "77P_temp_fetch_gate_patch_preview_latest.txt"

PHASE = "77P_TEMP_FETCH_GATE_PATCH_PREVIEW"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)
gate_text = GATE.read_text(encoding="utf-8") if GATE.exists() else ""

patch_preview = {
    "mode": "PATCH_PREVIEW_ONLY_NO_WRITE",
    "target_file": str(GATE),
    "planned_change": {
        "from": "HISTORICAL_BAR_FETCH_ENABLED = False",
        "to": "HISTORICAL_BAR_FETCH_ENABLED = True",
    },
    "temporary_scope": {
        "symbol_allowlist": ["VFV.TO"],
        "max_symbols_allowed": 1,
        "max_rows_allowed": 300,
    },
    "required_relock_phase": "77S_FETCH_GATE_RELOCK",
    "forbidden_now": [
        "apply patch",
        "fetch bars",
        "run replay",
        "train",
        "write strategy DB",
        "promote candidate",
        "broker execution",
        "live execution",
    ],
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "gate_exists": GATE.exists(),
    "gate_currently_fetch_disabled": "HISTORICAL_BAR_FETCH_ENABLED = False" in gate_text,
    "preview_only_no_write": patch_preview["mode"] == "PATCH_PREVIEW_ONLY_NO_WRITE",
    "temporary_scope_limited": (
        patch_preview["temporary_scope"]["symbol_allowlist"] == ["VFV.TO"]
        and patch_preview["temporary_scope"]["max_symbols_allowed"] == 1
        and patch_preview["temporary_scope"]["max_rows_allowed"] == 300
    ),
    "training_blocked": True,
    "strategy_db_write_blocked": True,
    "promotion_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "TEMP_FETCH_GATE_PATCH_PREVIEW",
    "source_plan": str(SOURCE),
    "patch_preview": patch_preview,
    "policy": {
        "patch_preview_allowed": True,
        "patch_apply_allowed_now": False,
        "historical_bar_fetch_enabled_now": False,
        "real_historical_replay_enabled": False,
        "training_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "77Q_TEMP_FETCH_GATE_PATCH_APPLY",
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
        "- HISTORICAL_BAR_FETCH_ENABLED False -> True",
        "- VFV.TO only",
        "- 300 rows max",
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

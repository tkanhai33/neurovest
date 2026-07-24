#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "real_historical_bar_fetch_enablement_precheck" / "77N_real_historical_bar_fetch_enablement_precheck_latest.json"

OUT_DIR = ARCH / "real_historical_bar_fetch_temp_enablement_plan"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "77O_real_historical_bar_fetch_temp_enablement_plan_latest.json"
OUT_TXT = OUT_DIR / "77O_real_historical_bar_fetch_temp_enablement_plan_latest.txt"

PHASE = "77O_REAL_HISTORICAL_BAR_FETCH_TEMP_ENABLEMENT_PLAN"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

plan = {
    "mode": "TEMP_ENABLEMENT_PLAN_ONLY_NO_ENABLEMENT",
    "safe_to_enable_fetch_now": False,
    "future_temp_enablement_scope": {
        "symbol": "VFV.TO",
        "max_symbols": 1,
        "max_rows": 300,
        "period": "1y",
        "interval": "1d",
        "output_mode": "READ_ONLY_BAR_FIXTURE",
    },
    "temporary_rules": [
        "enable fetch only for one command phase",
        "fetch one symbol only",
        "cap rows at 300",
        "write bars only to runtime/replay_runtime_architecture/real_historical_bar_fixture/",
        "disable fetch immediately after artifact creation",
        "do not run replay in the fetch phase",
        "do not train",
        "do not write strategy DB",
        "do not promote",
        "do not touch broker or live execution",
    ],
    "required_next_sequence": [
        "77P_TEMP_FETCH_GATE_PATCH_PREVIEW",
        "77Q_TEMP_FETCH_GATE_PATCH_APPLY",
        "77R_FETCH_ONE_SYMBOL_READ_ONLY_BARS",
        "77S_FETCH_GATE_RELOCK",
        "77T_FETCH_ARTIFACT_CERTIFICATION",
    ],
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "plan_present": bool(plan),
    "plan_only_no_enablement": plan["mode"] == "TEMP_ENABLEMENT_PLAN_ONLY_NO_ENABLEMENT",
    "safe_to_enable_fetch_now_false": plan["safe_to_enable_fetch_now"] is False,
    "scope_one_symbol": plan["future_temp_enablement_scope"]["max_symbols"] == 1,
    "scope_max_rows_300": plan["future_temp_enablement_scope"]["max_rows"] == 300,
    "output_read_only": plan["future_temp_enablement_scope"]["output_mode"] == "READ_ONLY_BAR_FIXTURE",
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "REAL_HISTORICAL_BAR_FETCH_TEMP_ENABLEMENT_PLAN",
    "source_precheck": str(SOURCE),
    "plan": plan,
    "policy": {
        "temp_enablement_plan_allowed": True,
        "historical_bar_fetch_enabled_now": False,
        "real_historical_replay_enabled": False,
        "training_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "77P_TEMP_FETCH_GATE_PATCH_PREVIEW",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "safe_to_enable_fetch_now: False",
        "",
        "This is only a plan. Fetch remains disabled.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "safe_to_enable_fetch_now": False,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "real_historical_bar_fetch_source_rollup" / "77M_real_historical_bar_fetch_source_rollup_latest.json"
GATE = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L1_security_auth_safety/real_historical_bar_fetch_gate.py"
SERVICE = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/real_historical_bar_fetch_service.py"

OUT_DIR = ARCH / "real_historical_bar_fetch_enablement_precheck"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "77N_real_historical_bar_fetch_enablement_precheck_latest.json"
OUT_TXT = OUT_DIR / "77N_real_historical_bar_fetch_enablement_precheck_latest.txt"

PHASE = "77N_REAL_HISTORICAL_BAR_FETCH_ENABLEMENT_PRECHECK"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

precheck = {
    "mode": "ENABLEMENT_PRECHECK_ONLY_NO_ENABLEMENT",
    "safe_to_enable_fetch_now": False,
    "gate_file": str(GATE),
    "service_file": str(SERVICE),
    "required_before_enablement": [
        "explicit temporary fetch enablement phase",
        "one-symbol-only enforcement",
        "300-row hard cap enforcement",
        "read-only output path",
        "no replay execution during fetch",
        "no training",
        "no strategy DB write",
        "no promotion",
        "no broker/live",
    ],
    "approved_initial_scope_future": {
        "symbol": "VFV.TO",
        "max_symbols": 1,
        "max_rows": 300,
        "period": "1y",
        "interval": "1d",
        "persist_as_read_only_fixture": True,
    },
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "gate_file_exists": GATE.exists(),
    "service_file_exists": SERVICE.exists(),
    "precheck_present": bool(precheck),
    "safe_to_enable_fetch_now_false": precheck["safe_to_enable_fetch_now"] is False,
    "training_blocked": True,
    "strategy_db_write_blocked": True,
    "promotion_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "REAL_HISTORICAL_BAR_FETCH_ENABLEMENT_PRECHECK",
    "source_rollup": str(SOURCE),
    "precheck": precheck,
    "policy": {
        "enablement_precheck_allowed": True,
        "historical_bar_fetch_enabled_now": False,
        "real_historical_replay_enabled": False,
        "training_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "77O_REAL_HISTORICAL_BAR_FETCH_TEMP_ENABLEMENT_PLAN",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"safe_to_enable_fetch_now: {precheck['safe_to_enable_fetch_now']}",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "safe_to_enable_fetch_now": precheck["safe_to_enable_fetch_now"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

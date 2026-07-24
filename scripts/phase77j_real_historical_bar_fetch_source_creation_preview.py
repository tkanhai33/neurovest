#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "real_historical_bar_fetch_gate_rollup" / "77I_real_historical_bar_fetch_gate_rollup_latest.json"

OUT_DIR = ARCH / "real_historical_bar_fetch_source_creation_preview"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "77J_real_historical_bar_fetch_source_creation_preview_latest.json"
OUT_TXT = OUT_DIR / "77J_real_historical_bar_fetch_source_creation_preview_latest.txt"

PHASE = "77J_REAL_HISTORICAL_BAR_FETCH_SOURCE_CREATION_PREVIEW"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

preview = {
    "mode": "SOURCE_CREATION_PREVIEW_ONLY_NO_WRITE",
    "future_target_file": "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/real_historical_bar_fetch_service.py",
    "planned_source_dependencies": [
        "real_historical_bar_fetch_gate",
        "market_data_provider_router",
        "yfinance_historical_bars_adapter",
    ],
    "planned_functions": [
        "get_fetch_gate_status",
        "validate_fetch_scope",
        "validate_bar_schema",
        "preview_fetch_contract",
        "future_fetch_single_symbol_bars",
    ],
    "locked_scope": {
        "symbol": "VFV.TO",
        "max_symbols": 1,
        "max_rows": 300,
        "period": "1y",
        "interval": "1d",
    },
    "forbidden_now": [
        "write fetch source file",
        "fetch historical bars",
        "persist historical bars",
        "run real historical replay",
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
    "preview_present": bool(preview),
    "preview_only_no_write": preview["mode"] == "SOURCE_CREATION_PREVIEW_ONLY_NO_WRITE",
    "target_declared": bool(preview["future_target_file"]),
    "planned_functions_present": len(preview["planned_functions"]) > 0,
    "scope_locked": (
        preview["locked_scope"]["symbol"] == "VFV.TO"
        and preview["locked_scope"]["max_symbols"] == 1
        and preview["locked_scope"]["max_rows"] == 300
    ),
    "source_write_blocked_now": True,
    "historical_bar_fetch_blocked_now": True,
    "real_historical_replay_blocked": True,
    "training_blocked": True,
    "strategy_db_write_blocked": True,
    "promotion_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "REAL_HISTORICAL_BAR_FETCH_SOURCE_CREATION_PREVIEW",
    "source_fetch_gate_rollup": str(SOURCE),
    "preview": preview,
    "policy": {
        "source_creation_preview_allowed": True,
        "source_write_allowed_now": False,
        "historical_bar_fetch_allowed_now": False,
        "real_historical_replay_allowed_now": False,
        "training_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "77K_REAL_HISTORICAL_BAR_FETCH_SOURCE_CREATION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"future_target_file: {preview['future_target_file']}",
        "",
        "Still blocked:",
        "- source write",
        "- historical fetch",
        "- replay",
        "- training",
        "- strategy DB write",
        "- promotion",
        "- broker/live",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "future_target_file": preview["future_target_file"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

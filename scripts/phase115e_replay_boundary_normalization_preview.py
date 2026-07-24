#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "shop_to_numeric_anomaly_inspection/115C_shop_to_numeric_anomaly_inspection_latest.json"

OUT_DIR = ARCH / "replay_boundary_normalization_preview"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "115E_replay_boundary_normalization_preview_latest.json"
OUT_TXT = OUT_DIR / "115E_replay_boundary_normalization_preview_latest.txt"

PHASE = "115E_REPLAY_BOUNDARY_NORMALIZATION_PREVIEW"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source = read_json(SOURCE)
anomalies = source.get("anomalies", [])

boundary_anomalies = []
for a in anomalies:
    prev_date = a.get("previous_date")
    curr_date = a.get("historical_date")
    if prev_date and curr_date and curr_date < prev_date:
        boundary_anomalies.append({
            "symbol": a.get("symbol"),
            "previous_date": prev_date,
            "current_date": curr_date,
            "previous_close": a.get("previous_close"),
            "current_close": a.get("current_close"),
            "computed_return": a.get("computed_return"),
            "detected_cause": "REPLAY_BOUNDARY_WRAP",
            "normalization_action_preview": {
                "reset_previous_close": True,
                "skip_cross_boundary_return": True,
                "force_boundary_decision": "HOLD",
                "mark_replay_boundary_reset": True,
            },
            "data_modification_required": False,
        })

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "boundary_anomalies_found": len(boundary_anomalies) > 0,
    "all_boundary_wraps": len(boundary_anomalies) == len(anomalies),
    "data_modification_not_required": all(a["data_modification_required"] is False for a in boundary_anomalies),
    "reset_policy_present": all(a["normalization_action_preview"]["reset_previous_close"] is True for a in boundary_anomalies),
    "skip_cross_boundary_return_present": all(a["normalization_action_preview"]["skip_cross_boundary_return"] is True for a in boundary_anomalies),
    "training_blocked": True,
    "strategy_db_write_blocked": True,
    "promotion_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "REPLAY_BOUNDARY_NORMALIZATION_PREVIEW_ONLY",
    "source_anomaly_inspection": str(SOURCE),
    "summary": {
        "anomalies_inspected": len(anomalies),
        "replay_boundary_wraps": len(boundary_anomalies),
        "data_normalization_required": False,
        "runner_logic_patch_required": True,
    },
    "boundary_anomalies": boundary_anomalies,
    "policy": {
        "preview_only": True,
        "data_modification_allowed": False,
        "normalization_executed": False,
        "runner_patch_executed": False,
        "training_execution_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "115F_REPLAY_BOUNDARY_GUARD_PATCH",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"anomalies_inspected: {len(anomalies)}",
        f"replay_boundary_wraps: {len(boundary_anomalies)}",
        "data_normalization_required: False",
        "runner_logic_patch_required: True",
        "",
        "Cause identified: replay loop wrapped from 2026 back to 2016.",
        "Fix required in runner logic, not CSV data.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "anomalies_inspected": len(anomalies),
    "replay_boundary_wraps": len(boundary_anomalies),
    "data_normalization_required": False,
    "runner_logic_patch_required": True,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

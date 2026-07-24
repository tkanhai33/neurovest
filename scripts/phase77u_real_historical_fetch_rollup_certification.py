#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

PHASE = "77U_REAL_HISTORICAL_FETCH_ROLLUP_CERTIFICATION"

EXPECTED = {
    "77Q_temp_gate_apply": ARCH / "temp_fetch_gate_patch_apply/77Q_temp_fetch_gate_patch_apply_latest.json",
    "77R_fetch_one_symbol": ARCH / "real_historical_bar_fixture/77R_fetch_one_symbol_read_only_bars_latest.json",
    "77S_fetch_gate_relock": ARCH / "fetch_gate_relock/77S_fetch_gate_relock_latest.json",
    "77T_fetch_artifact_certification": ARCH / "fetch_artifact_certification/77T_fetch_artifact_certification_latest.json",
}

OUT_DIR = ARCH / "real_historical_fetch_rollup"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "77U_real_historical_fetch_rollup_certification_latest.json"
OUT_TXT = OUT_DIR / "77U_real_historical_fetch_rollup_certification_latest.txt"


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

fetch = read_json(EXPECTED["77R_fetch_one_symbol"])
artifact = read_json(EXPECTED["77T_fetch_artifact_certification"])
relock = read_json(EXPECTED["77S_fetch_gate_relock"])

checks["rows_present"] = artifact.get("row_count", 0) > 0
checks["rows_capped_300"] = artifact.get("row_count", 0) <= 300
checks["one_symbol_only"] = artifact.get("symbols") == ["VFV.TO"]
checks["date_range_present"] = bool(artifact.get("date_min")) and bool(artifact.get("date_max"))
checks["fetch_gate_relocked"] = relock.get("policy", {}).get("historical_bar_fetch_enabled") is False
checks["real_replay_blocked"] = relock.get("policy", {}).get("real_historical_replay_enabled") is False
checks["training_blocked"] = relock.get("policy", {}).get("training_enabled") is False
checks["strategy_db_write_blocked"] = relock.get("policy", {}).get("strategy_db_write_allowed") is False
checks["promotion_blocked"] = relock.get("policy", {}).get("promotion_enabled") is False
checks["broker_live_blocked"] = (
    relock.get("policy", {}).get("broker_execution_enabled") is False
    and relock.get("policy", {}).get("live_execution_enabled") is False
)

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "REAL_HISTORICAL_FETCH_ROLLUP_CERTIFICATION",
    "artifacts": artifacts,
    "fetch_summary": {
        "symbol": fetch.get("symbol"),
        "row_count": artifact.get("row_count"),
        "date_min": artifact.get("date_min"),
        "date_max": artifact.get("date_max"),
        "csv": artifact.get("csv"),
    },
    "policy": {
        "real_historical_bar_fixture_certified": True,
        "historical_bar_fetch_enabled": False,
        "real_historical_replay_enabled": False,
        "training_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "78A_STRESS_TEST_REPORT_STORE",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"symbol: {result['fetch_summary']['symbol']}",
        f"row_count: {result['fetch_summary']['row_count']}",
        f"date_min: {result['fetch_summary']['date_min']}",
        f"date_max: {result['fetch_summary']['date_max']}",
        "",
        "Fetch gate remains relocked.",
        "Replay/training/db/promotion/broker/live remain blocked.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "fetch_summary": result["fetch_summary"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

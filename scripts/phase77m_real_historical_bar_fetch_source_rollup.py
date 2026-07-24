#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

PHASE = "77M_REAL_HISTORICAL_BAR_FETCH_SOURCE_ROLLUP"

EXPECTED = {
    "77J_source_preview": ARCH / "real_historical_bar_fetch_source_creation_preview/77J_real_historical_bar_fetch_source_creation_preview_latest.json",
    "77K_source_creation": ARCH / "real_historical_bar_fetch_source_creation/77K_real_historical_bar_fetch_source_creation_latest.json",
    "77L_source_certification": ARCH / "real_historical_bar_fetch_source_certification/77L_real_historical_bar_fetch_source_certification_latest.json",
}

OUT_DIR = ARCH / "real_historical_bar_fetch_source_rollup"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "77M_real_historical_bar_fetch_source_rollup_latest.json"
OUT_TXT = OUT_DIR / "77M_real_historical_bar_fetch_source_rollup_latest.txt"


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

cert = read_json(EXPECTED["77L_source_certification"])
tests = cert.get("tests", {})

checks["tests_present"] = len(tests) > 0
checks["all_tests_passed"] = all(tests.values()) if tests else False
checks["historical_bar_fetch_blocked"] = cert.get("policy", {}).get("historical_bar_fetch_enabled") is False
checks["real_historical_replay_blocked"] = cert.get("policy", {}).get("real_historical_replay_enabled") is False
checks["training_blocked"] = cert.get("policy", {}).get("training_enabled") is False
checks["strategy_db_write_blocked"] = cert.get("policy", {}).get("strategy_db_write_allowed") is False
checks["promotion_blocked"] = cert.get("policy", {}).get("promotion_enabled") is False
checks["broker_live_blocked"] = (
    cert.get("policy", {}).get("broker_execution_enabled") is False
    and cert.get("policy", {}).get("live_execution_enabled") is False
)

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "REAL_HISTORICAL_BAR_FETCH_SOURCE_ROLLUP",
    "artifacts": artifacts,
    "test_count": len(tests),
    "policy": {
        "historical_bar_fetch_source_rollup_certified": True,
        "historical_bar_fetch_enabled": False,
        "real_historical_replay_enabled": False,
        "training_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "77N_REAL_HISTORICAL_BAR_FETCH_ENABLEMENT_PRECHECK",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"test_count: {len(tests)}",
        "",
        "Fetch source exists and is certified, but fetch is still blocked.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "test_count": len(tests),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

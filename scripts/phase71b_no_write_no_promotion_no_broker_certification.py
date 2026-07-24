#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "single_fixture_replay_dry_run" / "71A_single_fixture_replay_dry_run_only_latest.json"

OUT_DIR = ARCH / "no_write_no_promotion_no_broker"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "71B_no_write_no_promotion_no_broker_certification_latest.json"
OUT_TXT = OUT_DIR / "71B_no_write_no_promotion_no_broker_certification_latest.txt"

PHASE = "71B_NO_WRITE_NO_PROMOTION_NO_BROKER_CERTIFICATION"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)
metrics = source.get("metrics", {})
safety = metrics.get("safety", {}) if isinstance(metrics, dict) else {}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "metrics_present": bool(metrics),
    "strategy_db_write_blocked": safety.get("strategy_db_write_allowed") is False,
    "promotion_blocked": safety.get("promotion_enabled") is False,
    "broker_execution_blocked": safety.get("broker_execution_enabled") is False,
    "live_execution_blocked": safety.get("live_execution_enabled") is False,
    "strategy_execution_blocked": safety.get("strategy_execution_allowed") is False,
    "historical_replay_blocked": safety.get("historical_replay_allowed") is False,
    "runtime_execution_blocked": safety.get("replay_runtime_enabled") is False,
    "result_store_write_not_enabled": source.get("policy", {}).get("strategy_db_write_allowed") is False,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "NO_WRITE_NO_PROMOTION_NO_BROKER_CERTIFICATION",
    "source_dry_run": str(SOURCE),
    "certified_safety": {
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
        "strategy_execution_allowed": False,
        "historical_replay_allowed": False,
        "runtime_execution_allowed": False,
    },
    "checks": checks,
    "policy": {
        "no_write_no_promotion_no_broker_certified": True,
        "read_only_result_store_allowed_next": True,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "72A_READ_ONLY_RESULT_STORE",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "",
        "Certified blocked:",
        "- strategy DB write",
        "- promotion",
        "- broker execution",
        "- live execution",
        "- runtime execution",
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

#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "replay_spec_validation_rollup" / "67F_replay_spec_validation_rollup_latest.json"

OUT_DIR = ARCH / "fixture_bar_dataset"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "68A_fixture_bar_dataset_manifest_latest.json"
OUT_TXT = OUT_DIR / "68A_fixture_bar_dataset_manifest_latest.txt"

PHASE = "68A_FIXTURE_BAR_DATASET_MANIFEST"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

fixture_manifest = {
    "dataset_id": "fixture_ohlcv_v1",
    "mode": "MANIFEST_ONLY",
    "purpose": "define tiny OHLCV fixture shape for future replay math tests",
    "rows_planned": 10,
    "symbols_planned": ["FIXTURE.TO"],
    "columns_required": [
        "symbol",
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ],
    "validation_rules": [
        "high >= open",
        "high >= close",
        "low <= open",
        "low <= close",
        "volume >= 0",
        "dates strictly increasing per symbol",
    ],
    "future_allowed_use": [
        "contract test fixture",
        "bar math validation",
        "metric calculation validation",
    ],
    "forbidden_now": [
        "run replay",
        "score strategy",
        "write strategy database",
        "promote candidate",
        "broker execution",
        "live execution",
    ],
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "fixture_manifest_present": bool(fixture_manifest),
    "columns_present": len(fixture_manifest["columns_required"]) == 7,
    "manifest_only": fixture_manifest["mode"] == "MANIFEST_ONLY",
    "historical_replay_blocked": True,
    "runtime_execution_blocked": True,
    "strategy_db_write_blocked": True,
    "promotion_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_FIXTURE_BAR_DATASET_MANIFEST",
    "source_validation_rollup": str(SOURCE),
    "fixture_manifest": fixture_manifest,
    "policy": {
        "fixture_manifest_allowed": True,
        "fixture_file_write_allowed_now": False,
        "historical_replay_allowed_now": False,
        "runtime_execution_allowed": False,
        "runtime_mutation_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "68B_FIXTURE_BAR_DATASET_SOURCE_CREATION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"dataset_id: {fixture_manifest['dataset_id']}",
        f"rows_planned: {fixture_manifest['rows_planned']}",
        "",
        "Columns:",
        *[f"- {c}" for c in fixture_manifest["columns_required"]],
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "dataset_id": fixture_manifest["dataset_id"],
    "rows_planned": fixture_manifest["rows_planned"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

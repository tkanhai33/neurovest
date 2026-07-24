#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "research_input_whitelist_refresh/111A_research_input_whitelist_refresh_latest.json"

OUT_DIR = ARCH / "eight_hour_training_run_manifest"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "112A_8_hour_read_only_training_run_manifest_latest.json"
OUT_TXT = OUT_DIR / "112A_8_hour_read_only_training_run_manifest_latest.txt"

PHASE = "112A_8_HOUR_READ_ONLY_TRAINING_RUN_MANIFEST"

def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source = read_json(SOURCE)
whitelist = source.get("whitelist", {})

manifest = {
    "training_run_id": "TRAINING_RUN_0002_8H",
    "duration_hours": 8,
    "mode": "READ_ONLY_SANDBOX_TRAINING",
    "historical_fixtures": whitelist.get("historical_fixtures", []),
    "research_documents": whitelist.get("research_documents", []),
    "macro_research_inputs": whitelist.get("macro_research_inputs", []),
    "stream_enabled": True,
    "stream_file": str(ARCH / "eight_hour_training_run_stream/TRAINING_RUN_0002_8H/training_stream.jsonl"),
    "sandbox_output_dir": str(ARCH / "eight_hour_training_run_stream/TRAINING_RUN_0002_8H/sandbox"),
    "hard_blocks": whitelist.get("hard_blocks", {}),
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "historical_fixtures_10": len(manifest["historical_fixtures"]) == 10,
    "macro_research_inputs_1": len(manifest["macro_research_inputs"]) == 1,
    "duration_8_hours": manifest["duration_hours"] == 8,
    "stream_enabled": manifest["stream_enabled"] is True,
    "training_execution_blocked": manifest["hard_blocks"].get("training_execution_enabled") is False,
    "strategy_db_write_blocked": manifest["hard_blocks"].get("strategy_db_write_allowed") is False,
    "promotion_blocked": manifest["hard_blocks"].get("promotion_enabled") is False,
    "broker_live_blocked": (
        manifest["hard_blocks"].get("broker_execution_enabled") is False
        and manifest["hard_blocks"].get("live_execution_enabled") is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "manifest": manifest,
    "checks": checks,
    "policy": {
        "eight_hour_training_manifest_certified": True,
        **manifest["hard_blocks"],
    },
    "recommended_next_phase": "113A_8_HOUR_TRAINING_STREAM_STUB",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"training_run_id: {manifest['training_run_id']}",
        f"duration_hours: {manifest['duration_hours']}",
        f"historical_fixtures: {len(manifest['historical_fixtures'])}",
        f"macro_research_inputs: {len(manifest['macro_research_inputs'])}",
        "",
        "8-hour read-only training manifest created.",
        "Training/db/mutation/promotion/broker/live remain blocked.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "training_run_id": manifest["training_run_id"],
    "duration_hours": manifest["duration_hours"],
    "historical_fixtures": len(manifest["historical_fixtures"]),
    "macro_research_inputs": len(manifest["macro_research_inputs"]),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "fred_canada_research_input_rollup/110C_fred_canada_research_input_rollup_latest.json"
OLD = ARCH / "research_whitelist_and_training_input_certification/97A_research_whitelist_and_training_input_certification_latest.json"

OUT_DIR = ARCH / "research_input_whitelist_refresh"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "111A_research_input_whitelist_refresh_latest.json"
OUT_TXT = OUT_DIR / "111A_research_input_whitelist_refresh_latest.txt"

PHASE = "111A_RESEARCH_INPUT_WHITELIST_REFRESH"

def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source = read_json(SOURCE)
old = read_json(OLD)

fred = source.get("certification", {})
old_manifest = old.get("manifest", {})

whitelist = {
    "training_run_id": "TRAINING_RUN_0002",
    "historical_fixtures": old_manifest.get("historical_fixtures", []),
    "research_documents": old_manifest.get("research_documents", []),
    "macro_research_inputs": [
        {
            "dataset_id": fred.get("dataset_id"),
            "provider": fred.get("provider"),
            "country": fred.get("country"),
            "workbook": fred.get("workbook"),
            "sheet_names": fred.get("sheet_names"),
            "approved": True,
            "read_only": True,
        }
    ],
    "external_models": [],
    "hard_blocks": {
        "training_execution_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
}

checks = {
    "source_110c_exists": SOURCE.exists(),
    "source_110c_certified": source.get("certified") is True,
    "old_whitelist_exists": OLD.exists(),
    "old_whitelist_certified": old.get("certified") is True,
    "historical_fixtures_preserved": len(whitelist["historical_fixtures"]) == 10,
    "fred_macro_input_added": len(whitelist["macro_research_inputs"]) == 1,
    "fred_dataset_id_correct": whitelist["macro_research_inputs"][0]["dataset_id"] == "FRED_CANADA_MACRO_0001",
    "fred_read_only": whitelist["macro_research_inputs"][0]["read_only"] is True,
    "external_models_empty": whitelist["external_models"] == [],
    "training_blocked": whitelist["hard_blocks"]["training_execution_enabled"] is False,
    "strategy_db_write_blocked": whitelist["hard_blocks"]["strategy_db_write_allowed"] is False,
    "promotion_blocked": whitelist["hard_blocks"]["promotion_enabled"] is False,
    "broker_live_blocked": (
        whitelist["hard_blocks"]["broker_execution_enabled"] is False
        and whitelist["hard_blocks"]["live_execution_enabled"] is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "RESEARCH_INPUT_WHITELIST_REFRESH",
    "whitelist": whitelist,
    "checks": checks,
    "policy": {
        "research_input_whitelist_refreshed": True,
        **whitelist["hard_blocks"],
    },
    "recommended_next_phase": "112A_8_HOUR_READ_ONLY_TRAINING_RUN_MANIFEST",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"historical_fixtures: {len(whitelist['historical_fixtures'])}",
        f"macro_research_inputs: {len(whitelist['macro_research_inputs'])}",
        "external_models: 0",
        "",
        "Research whitelist refreshed with FRED Canada.",
        "No HF model added yet.",
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
    "historical_fixtures": len(whitelist["historical_fixtures"]),
    "macro_research_inputs": len(whitelist["macro_research_inputs"]),
    "external_models": len(whitelist["external_models"]),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

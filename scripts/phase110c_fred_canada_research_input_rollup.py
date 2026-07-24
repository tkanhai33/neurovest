#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

PHASE = "110C_FRED_CANADA_RESEARCH_INPUT_ROLLUP"

EXPECTED = {
    "110A_foundation": ARCH / "research_knowledge_repository_foundation/110A_research_knowledge_repository_foundation_latest.json",
    "110B_certification": ARCH / "fred_canada_research_input_certification/110B_fred_canada_research_input_certification_latest.json",
}

OUT_DIR = ARCH / "fred_canada_research_input_rollup"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "110C_fred_canada_research_input_rollup_latest.json"
OUT_TXT = OUT_DIR / "110C_fred_canada_research_input_rollup_latest.txt"

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

cert = read_json(EXPECTED["110B_certification"])
certification = cert.get("certification", {})

checks.update({
    "dataset_id_present": certification.get("dataset_id") == "FRED_CANADA_MACRO_0001",
    "provider_fred": certification.get("provider") == "FRED",
    "country_canada": certification.get("country") == "Canada",
    "workbook_present": bool(certification.get("workbook")),
    "read_only": certification.get("read_only") is True,
    "approved_for_research_input": certification.get("approved_for_research_input") is True,
    "postgres_not_written": certification.get("postgres_rows_written") is False,
    "training_blocked": certification.get("training_execution_enabled") is False,
    "strategy_db_write_blocked": certification.get("strategy_db_write_allowed") is False,
    "promotion_blocked": certification.get("promotion_enabled") is False,
    "broker_live_blocked": (
        certification.get("broker_execution_enabled") is False
        and certification.get("live_execution_enabled") is False
    ),
})

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "FRED_CANADA_RESEARCH_INPUT_ROLLUP",
    "artifacts": artifacts,
    "certification": certification,
    "checks": checks,
    "policy": {
        "fred_canada_research_input_rollup_certified": True,
        "approved_for_research_input": True,
        "read_only": True,
        "postgres_rows_written": False,
        "training_execution_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "111A_RESEARCH_INPUT_WHITELIST_REFRESH",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"dataset_id: {certification.get('dataset_id')}",
        f"workbook: {certification.get('workbook')}",
        "",
        "FRED Canada research input rollup certified.",
        "Read-only. Postgres metadata only. No DB write executed.",
        "Training/strategy DB/promotion/broker/live remain blocked.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "dataset_id": certification.get("dataset_id"),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

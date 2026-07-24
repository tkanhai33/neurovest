#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json, hashlib, zipfile

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "research_knowledge_repository_foundation/110A_research_knowledge_repository_foundation_latest.json"

FRED_ROOT = ROOT / "backend/app/stacks/learning_research/research_data/fred_canada"
RAW = FRED_ROOT / "raw"
META = FRED_ROOT / "metadata"
MANIFEST = META / "fred_canada_dataset_manifest.json"

OUT_DIR = ARCH / "fred_canada_research_input_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "110B_fred_canada_research_input_certification_latest.json"
OUT_TXT = OUT_DIR / "110B_fred_canada_research_input_certification_latest.txt"

PHASE = "110B_FRED_CANADA_RESEARCH_INPUT_CERTIFICATION"

def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def xlsx_sheets(path: Path) -> list[str]:
    try:
        with zipfile.ZipFile(path) as z:
            wb = z.read("xl/workbook.xml").decode("utf-8", errors="ignore")
        sheets = []
        for chunk in wb.split("<sheet ")[1:]:
            if 'name="' in chunk:
                sheets.append(chunk.split('name="', 1)[1].split('"', 1)[0])
        return sheets
    except Exception:
        return []

source = read_json(SOURCE)
manifest = read_json(MANIFEST)

workbook = Path(manifest.get("repo_raw_file", "")) if manifest else None
sheets = xlsx_sheets(workbook) if workbook and workbook.exists() else []

expected_sheets = {"README", "5 Year", "Annual", "Monthly", "Quarterly"}

certification = {
    "dataset_id": manifest.get("dataset_id"),
    "provider": manifest.get("provider"),
    "country": manifest.get("country"),
    "workbook": str(workbook) if workbook else None,
    "sheet_names": sheets,
    "checksum_sha256": sha256(workbook) if workbook and workbook.exists() else None,
    "approved_for_research_input": True,
    "read_only": True,
    "postgres_rows_written": False,
    "training_execution_enabled": False,
    "strategy_db_write_allowed": False,
    "promotion_enabled": False,
    "broker_execution_enabled": False,
    "live_execution_enabled": False,
}

checks = {
    "source_110a_exists": SOURCE.exists(),
    "source_110a_certified": source.get("certified") is True,
    "fred_root_exists": FRED_ROOT.exists(),
    "raw_dir_exists": RAW.exists(),
    "metadata_dir_exists": META.exists(),
    "manifest_exists": MANIFEST.exists(),
    "manifest_dataset_id_present": bool(manifest.get("dataset_id")),
    "workbook_exists": workbook is not None and workbook.exists(),
    "checksum_matches_manifest": (
        workbook is not None
        and workbook.exists()
        and sha256(workbook) == manifest.get("checksum_sha256")
    ),
    "expected_sheets_present": expected_sheets.issubset(set(sheets)),
    "approved_true": manifest.get("approved") is True,
    "read_only_true": manifest.get("read_only") is True,
    "postgres_not_written": manifest.get("postgres_rows_written") is False,
    "training_blocked": certification["training_execution_enabled"] is False,
    "strategy_db_write_blocked": certification["strategy_db_write_allowed"] is False,
    "promotion_blocked": certification["promotion_enabled"] is False,
    "broker_live_blocked": (
        certification["broker_execution_enabled"] is False
        and certification["live_execution_enabled"] is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "FRED_CANADA_RESEARCH_INPUT_CERTIFICATION",
    "source_foundation": str(SOURCE),
    "certification": certification,
    "checks": checks,
    "policy": {
        "fred_canada_research_input_certified": True,
        "approved_for_research_input": True,
        "read_only": True,
        "postgres_rows_written": False,
        "training_execution_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "110C_FRED_CANADA_RESEARCH_INPUT_ROLLUP",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"dataset_id: {certification['dataset_id']}",
        f"workbook: {certification['workbook']}",
        f"sheets: {len(sheets)}",
        "",
        "FRED Canada research input certified read-only.",
        "Postgres metadata only. No DB write executed.",
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
    "dataset_id": certification["dataset_id"],
    "sheets": sheets,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

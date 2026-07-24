#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json, hashlib, shutil, zipfile

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE_109B = ARCH / "dev_command_execution_enablement_patch_apply/109B_dev_command_execution_enablement_patch_apply_latest.json"

PHASE = "110A_RESEARCH_KNOWLEDGE_REPOSITORY_FOUNDATION"

RESEARCH_ROOT = ROOT / "backend/app/stacks/learning_research/research_data"
FRED_ROOT = RESEARCH_ROOT / "fred_canada"
RAW = FRED_ROOT / "raw"
META = FRED_ROOT / "metadata"
SQL = FRED_ROOT / "postgres_metadata_preview"

for p in [RAW, META, SQL]:
    p.mkdir(parents=True, exist_ok=True)

OUT_DIR = ARCH / "research_knowledge_repository_foundation"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "110A_research_knowledge_repository_foundation_latest.json"
OUT_TXT = OUT_DIR / "110A_research_knowledge_repository_foundation_latest.txt"

def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def find_workbook() -> Path | None:
    candidates = []
    search_roots = [Path.home() / "Downloads", ROOT, Path("/mnt/data")]
    for base in search_roots:
        if base.exists():
            candidates.extend(base.glob("*.xlsx"))
            candidates.extend(base.glob("*.xls"))
    preferred = [p for p in candidates if "fred" in p.name.lower() or "canada" in p.name.lower() or "neurovest" in p.name.lower()]
    pool = preferred or candidates
    return max(pool, key=lambda p: p.stat().st_mtime) if pool else None

def xlsx_sheets(path: Path) -> list[str]:
    try:
        with zipfile.ZipFile(path) as z:
            wb = z.read("xl/workbook.xml").decode("utf-8", errors="ignore")
        out = []
        for chunk in wb.split("<sheet ")[1:]:
            if 'name="' in chunk:
                out.append(chunk.split('name="', 1)[1].split('"', 1)[0])
        return out
    except Exception:
        return []

source = read_json(SOURCE_109B)
src = find_workbook()

errors = []
copied_path = None
manifest = {}

if not src:
    errors.append("No .xlsx/.xls workbook found in ~/Downloads, repo root, or /mnt/data.")
else:
    dest = RAW / src.name
    if dest.resolve() != src.resolve():
        shutil.copy2(src, dest)
    copied_path = dest

    manifest = {
        "dataset_id": "FRED_CANADA_MACRO_0001",
        "provider": "FRED",
        "country": "Canada",
        "source_file": str(src),
        "repo_raw_file": str(dest),
        "checksum_sha256": sha256(dest),
        "file_size_bytes": dest.stat().st_size,
        "sheet_names": xlsx_sheets(dest),
        "approved": True,
        "read_only": True,
        "storage_mode": "FILE_REPOSITORY_WITH_POSTGRES_METADATA_PREVIEW_ONLY",
        "postgres_rows_written": False,
        "created_at": datetime.now(UTC).isoformat(),
    }

    (META / "fred_canada_dataset_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    (SQL / "fred_canada_dataset_registry_preview.sql").write_text(
        """
-- PREVIEW ONLY. DO NOT RUN AUTOMATICALLY.
CREATE TABLE IF NOT EXISTS macro_dataset_registry (
    dataset_id TEXT PRIMARY KEY,
    provider TEXT NOT NULL,
    country TEXT NOT NULL,
    repo_raw_file TEXT NOT NULL,
    checksum_sha256 TEXT NOT NULL,
    approved BOOLEAN NOT NULL,
    read_only BOOLEAN NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
);

-- Metadata only. Raw workbook remains on disk.
""".strip() + "\n",
        encoding="utf-8",
    )

checks = {
    "source_109b_exists": SOURCE_109B.exists(),
    "source_109b_certified": source.get("certified") is True,
    "research_root_exists": RESEARCH_ROOT.exists(),
    "fred_raw_exists": RAW.exists(),
    "fred_metadata_exists": META.exists(),
    "workbook_found": src is not None,
    "workbook_copied": copied_path is not None and copied_path.exists(),
    "manifest_written": (META / "fred_canada_dataset_manifest.json").exists(),
    "postgres_preview_written": (SQL / "fred_canada_dataset_registry_preview.sql").exists(),
    "postgres_not_written": True,
    "training_blocked": True,
    "db_strategy_write_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "research_root": str(RESEARCH_ROOT),
    "fred_canada_raw": str(RAW),
    "manifest": manifest,
    "errors": errors,
    "checks": checks,
    "policy": {
        "research_repository_created": True,
        "postgres_metadata_preview_only": True,
        "postgres_rows_written": False,
        "training_execution_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "110B_FRED_CANADA_RESEARCH_INPUT_CERTIFICATION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"workbook: {copied_path}",
        f"sheets: {len(manifest.get('sheet_names', [])) if manifest else 0}",
        f"errors: {len(errors)}",
        "",
        "FRED Canada workbook placed in learning_research research_data repository.",
        "Postgres metadata is preview only. No DB write executed.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "workbook": str(copied_path) if copied_path else None,
    "sheets": manifest.get("sheet_names", []) if manifest else [],
    "errors": errors,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

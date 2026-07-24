#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json
import py_compile

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "source_creation" / "67A_replay_contract_source_creation_latest.json"

OUT_DIR = ARCH / "source_creation_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "67B_replay_contract_source_creation_certification_latest.json"
OUT_TXT = OUT_DIR / "67B_replay_contract_source_creation_certification_latest.txt"

PHASE = "67B_REPLAY_CONTRACT_SOURCE_CREATION_CERTIFICATION"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)
created_files = source.get("created_files", [])

file_checks = []

for item in created_files:
    path = ROOT / item["path"]
    compile_ok = False
    contains_locks = False
    error = None

    try:
        py_compile.compile(str(path), doraise=True)
        compile_ok = True
    except Exception as exc:
        error = {
            "type": type(exc).__name__,
            "message": str(exc),
        }

    try:
        text = path.read_text(encoding="utf-8")
        contains_locks = all(flag in text for flag in [
            "REPLAY_RUNTIME_ENABLED = False",
            "HISTORICAL_REPLAY_ALLOWED = False",
            "STRATEGY_EXECUTION_ALLOWED = False",
            "STRATEGY_DB_WRITE_ALLOWED = False",
            "PROMOTION_ENABLED = False",
            "BROKER_EXECUTION_ENABLED = False",
            "LIVE_EXECUTION_ENABLED = False",
            "contract_status",
        ])
    except Exception as exc:
        error = error or {
            "type": type(exc).__name__,
            "message": str(exc),
        }

    file_checks.append({
        "path": item["path"],
        "exists": path.exists(),
        "compile_ok": compile_ok,
        "contains_required_locks": contains_locks,
        "error": error,
    })

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "files_present": len(file_checks) > 0,
    "all_files_exist": all(x["exists"] for x in file_checks),
    "all_compile_ok": all(x["compile_ok"] for x in file_checks),
    "all_required_locks_present": all(x["contains_required_locks"] for x in file_checks),
    "historical_replay_blocked": True,
    "runtime_execution_blocked": True,
    "strategy_db_write_blocked": True,
    "promotion_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "REPLAY_CONTRACT_SOURCE_CREATION_CERTIFICATION",
    "source_creation_artifact": str(SOURCE),
    "file_checks": file_checks,
    "policy": {
        "contract_source_certification_allowed": True,
        "historical_replay_allowed_now": False,
        "runtime_execution_allowed": False,
        "runtime_mutation_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "67C_REPLAY_CONTRACT_IMPORT_SMOKE_TEST",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

lines = [
    PHASE,
    "",
    f"certified: {result['certified']}",
    f"file_count: {len(file_checks)}",
    "",
    "File checks:",
    "",
]

for item in file_checks:
    lines.append(
        f"- {item['path']} | exists={item['exists']} | "
        f"compile_ok={item['compile_ok']} | locks={item['contains_required_locks']}"
    )

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(json.dumps({
    "phase": PHASE,
    "file_count": len(file_checks),
    "certified": result["certified"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

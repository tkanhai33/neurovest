#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import importlib.util
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "source_creation_certification" / "67B_replay_contract_source_creation_certification_latest.json"

OUT_DIR = ARCH / "import_smoke"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "67C_replay_contract_import_smoke_test_latest.json"
OUT_TXT = OUT_DIR / "67C_replay_contract_import_smoke_test_latest.txt"

PHASE = "67C_REPLAY_CONTRACT_IMPORT_SMOKE_TEST"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def import_file(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


source = read_json(SOURCE)
file_checks = source.get("file_checks", [])

imports = []

for item in file_checks:
    path = ROOT / item["path"]
    ok = False
    status = None
    error = None

    try:
        module = import_file(path)
        status = module.contract_status()
        ok = (
            isinstance(status, dict)
            and status.get("replay_runtime_enabled") is False
            and status.get("historical_replay_allowed") is False
            and status.get("strategy_execution_allowed") is False
            and status.get("strategy_db_write_allowed") is False
            and status.get("promotion_enabled") is False
            and status.get("broker_execution_enabled") is False
            and status.get("live_execution_enabled") is False
        )
    except Exception as exc:
        error = {
            "type": type(exc).__name__,
            "message": str(exc),
        }

    imports.append({
        "path": item["path"],
        "import_ok": ok,
        "contract_status": status,
        "error": error,
    })

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "files_present": len(imports) > 0,
    "all_imports_ok": all(x["import_ok"] for x in imports),
    "all_replay_disabled": all(x["contract_status"]["historical_replay_allowed"] is False for x in imports if x["contract_status"]),
    "all_runtime_disabled": all(x["contract_status"]["replay_runtime_enabled"] is False for x in imports if x["contract_status"]),
    "all_strategy_db_write_blocked": all(x["contract_status"]["strategy_db_write_allowed"] is False for x in imports if x["contract_status"]),
    "all_promotion_blocked": all(x["contract_status"]["promotion_enabled"] is False for x in imports if x["contract_status"]),
    "all_broker_live_blocked": all(
        x["contract_status"]["broker_execution_enabled"] is False
        and x["contract_status"]["live_execution_enabled"] is False
        for x in imports
        if x["contract_status"]
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "REPLAY_CONTRACT_IMPORT_SMOKE_TEST",
    "source_certification": str(SOURCE),
    "imports": imports,
    "policy": {
        "import_smoke_test_allowed": True,
        "historical_replay_allowed_now": False,
        "runtime_execution_allowed": False,
        "runtime_mutation_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "67D_REPLAY_CONTRACT_IMPORT_ROLLUP_CERTIFICATION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

lines = [
    PHASE,
    "",
    f"certified: {result['certified']}",
    f"file_count: {len(imports)}",
    "",
    "Imports:",
    "",
]

for item in imports:
    lines.append(f"- {item['path']} | import_ok={item['import_ok']}")

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(json.dumps({
    "phase": PHASE,
    "file_count": len(imports),
    "certified": result["certified"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

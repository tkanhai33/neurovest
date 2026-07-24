#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

PHASE = "67D_REPLAY_CONTRACT_IMPORT_ROLLUP_CERTIFICATION"

EXPECTED = {
    "67A_source_creation": ARCH / "source_creation/67A_replay_contract_source_creation_latest.json",
    "67B_source_certification": ARCH / "source_creation_certification/67B_replay_contract_source_creation_certification_latest.json",
    "67C_import_smoke": ARCH / "import_smoke/67C_replay_contract_import_smoke_test_latest.json",
}

OUT_DIR = ARCH / "contract_import_rollup"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "67D_replay_contract_import_rollup_latest.json"
OUT_TXT = OUT_DIR / "67D_replay_contract_import_rollup_latest.txt"


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

source_creation = read_json(EXPECTED["67A_source_creation"])
source_cert = read_json(EXPECTED["67B_source_certification"])
import_smoke = read_json(EXPECTED["67C_import_smoke"])

created_files = source_creation.get("created_files", [])
file_checks = source_cert.get("file_checks", [])
imports = import_smoke.get("imports", [])

checks["file_count_consistent"] = (
    len(created_files) == len(file_checks) == len(imports) and len(imports) > 0
)
checks["all_files_compile_ok"] = all(x.get("compile_ok") is True for x in file_checks)
checks["all_required_locks_present"] = all(x.get("contains_required_locks") is True for x in file_checks)
checks["all_imports_ok"] = all(x.get("import_ok") is True for x in imports)

checks["historical_replay_blocked"] = all(
    x.get("contract_status", {}).get("historical_replay_allowed") is False
    for x in imports
)
checks["runtime_blocked"] = all(
    x.get("contract_status", {}).get("replay_runtime_enabled") is False
    for x in imports
)
checks["strategy_execution_blocked"] = all(
    x.get("contract_status", {}).get("strategy_execution_allowed") is False
    for x in imports
)
checks["strategy_db_write_blocked"] = all(
    x.get("contract_status", {}).get("strategy_db_write_allowed") is False
    for x in imports
)
checks["promotion_blocked"] = all(
    x.get("contract_status", {}).get("promotion_enabled") is False
    for x in imports
)
checks["broker_live_blocked"] = all(
    x.get("contract_status", {}).get("broker_execution_enabled") is False
    and x.get("contract_status", {}).get("live_execution_enabled") is False
    for x in imports
)

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "REPLAY_CONTRACT_IMPORT_ROLLUP_CERTIFICATION",
    "artifacts": artifacts,
    "file_count": len(imports),
    "rollup_summary": {
        "contract_files_created_or_verified": len(created_files),
        "compile_certified": checks["all_files_compile_ok"],
        "import_certified": checks["all_imports_ok"],
        "required_locks_present": checks["all_required_locks_present"],
        "historical_replay_allowed": False,
        "runtime_execution_allowed": False,
        "strategy_execution_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "67E_REPLAY_SPEC_CONTRACT_VALIDATOR",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

lines = [
    PHASE,
    "",
    f"certified: {result['certified']}",
    f"file_count: {result['file_count']}",
    "",
    "Artifacts:",
    "",
]

for name, item in artifacts.items():
    lines.append(f"- {name}: exists={item['exists']} certified={item['certified']}")

lines += ["", "Rollup summary:", ""]

for k, v in result["rollup_summary"].items():
    lines.append(f"{k}: {v}")

lines += ["", "Next:", result["recommended_next_phase"]]

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(json.dumps({
    "phase": PHASE,
    "file_count": result["file_count"],
    "certified": result["certified"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

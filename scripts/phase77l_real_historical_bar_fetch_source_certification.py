#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import importlib.util
import json
import py_compile

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "real_historical_bar_fetch_source_creation" / "77K_real_historical_bar_fetch_source_creation_latest.json"
TARGET = ROOT / "backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/real_historical_bar_fetch_service.py"

OUT_DIR = ARCH / "real_historical_bar_fetch_source_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "77L_real_historical_bar_fetch_source_certification_latest.json"
OUT_TXT = OUT_DIR / "77L_real_historical_bar_fetch_source_certification_latest.txt"

PHASE = "77L_REAL_HISTORICAL_BAR_FETCH_SOURCE_CERTIFICATION"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def import_file(path: Path):
    spec = importlib.util.spec_from_file_location("real_historical_bar_fetch_service", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


source = read_json(SOURCE)
errors = []
tests = {}

compile_ok = False

try:
    py_compile.compile(str(TARGET), doraise=True)
    compile_ok = True
except Exception as exc:
    errors.append({"type": type(exc).__name__, "message": str(exc)})

try:
    module = import_file(TARGET)

    gate = module.get_fetch_gate_status()
    tests["gate_status_present"] = bool(gate)
    tests["historical_fetch_disabled"] = gate.get("historical_bar_fetch_enabled") is False
    tests["replay_disabled"] = gate.get("real_historical_replay_enabled") is False
    tests["training_disabled"] = gate.get("training_enabled") is False
    tests["db_promotion_broker_live_blocked"] = (
        gate.get("strategy_db_write_allowed") is False
        and gate.get("promotion_enabled") is False
        and gate.get("broker_execution_enabled") is False
        and gate.get("live_execution_enabled") is False
    )

    scope_ok = module.validate_fetch_scope(["VFV.TO"], 300)
    tests["valid_scope_allowed"] = scope_ok.get("valid") is True

    scope_bad_symbol = module.validate_fetch_scope(["SPY"], 300)
    tests["bad_symbol_blocked"] = scope_bad_symbol.get("valid") is False

    scope_bad_rows = module.validate_fetch_scope(["VFV.TO"], 301)
    tests["too_many_rows_blocked"] = scope_bad_rows.get("valid") is False

    schema_ok = module.validate_bar_schema([{
        "symbol": "VFV.TO",
        "date": "2024-01-01",
        "open": 1,
        "high": 1,
        "low": 1,
        "close": 1,
        "volume": 100,
    }])
    tests["schema_valid"] = schema_ok.get("valid") is True

    schema_bad = module.validate_bar_schema([{
        "symbol": "VFV.TO",
        "date": "2024-01-01",
    }])
    tests["schema_missing_fields_detected"] = schema_bad.get("valid") is False and len(schema_bad.get("missing", [])) > 0

    contract = module.preview_fetch_contract()
    tests["preview_contract_no_fetch"] = (
        contract.get("mode") == "FETCH_CONTRACT_ONLY"
        and contract.get("fetch_allowed_now") is False
    )

    blocked = module.future_fetch_single_symbol_bars()
    tests["future_fetch_blocked_by_gate"] = (
        blocked.get("fetch_executed") is False
        and blocked.get("blocked_by_gate") is True
    )

except Exception as exc:
    errors.append({"type": type(exc).__name__, "message": str(exc)})

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "target_exists": TARGET.exists(),
    "compile_ok": compile_ok,
    "tests_present": len(tests) > 0,
    "all_tests_passed": all(tests.values()) if tests else False,
    "no_errors": len(errors) == 0,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "REAL_HISTORICAL_BAR_FETCH_SOURCE_CERTIFICATION",
    "source_creation": str(SOURCE),
    "target_file": str(TARGET),
    "tests": tests,
    "errors": errors,
    "checks": checks,
    "policy": {
        "historical_bar_fetch_source_certified": True,
        "historical_bar_fetch_enabled": False,
        "real_historical_replay_enabled": False,
        "training_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "77M_REAL_HISTORICAL_BAR_FETCH_SOURCE_ROLLUP",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"compile_ok: {compile_ok}",
        "",
        "Tests:",
        *[f"- {k}: {v}" for k, v in tests.items()],
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "compile_ok": compile_ok,
    "test_count": len(tests),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

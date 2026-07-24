#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

PHASE = "77I_REAL_HISTORICAL_BAR_FETCH_GATE_ROLLUP"

EXPECTED = {
    "77F_fetch_preview": ARCH / "real_historical_bar_source_fetch_preview/77F_real_historical_bar_source_fetch_preview_latest.json",
    "77G_fetch_gate": ARCH / "real_historical_bar_source_fetch_gate/77G_real_historical_bar_source_fetch_gate_latest.json",
    "77H_fetch_gate_certification": ARCH / "real_historical_bar_source_fetch_gate_certification/77H_real_historical_bar_source_fetch_gate_certification_latest.json",
}

OUT_DIR = ARCH / "real_historical_bar_fetch_gate_rollup"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "77I_real_historical_bar_fetch_gate_rollup_latest.json"
OUT_TXT = OUT_DIR / "77I_real_historical_bar_fetch_gate_rollup_latest.txt"


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

cert = read_json(EXPECTED["77H_fetch_gate_certification"])
status = cert.get("gate_status", {})

checks["status_present"] = bool(status)
checks["historical_bar_fetch_disabled"] = status.get("historical_bar_fetch_enabled") is False
checks["real_historical_replay_disabled"] = status.get("real_historical_replay_enabled") is False
checks["training_disabled"] = status.get("training_enabled") is False
checks["strategy_db_write_blocked"] = status.get("strategy_db_write_allowed") is False
checks["promotion_blocked"] = status.get("promotion_enabled") is False
checks["broker_live_blocked"] = (
    status.get("broker_execution_enabled") is False
    and status.get("live_execution_enabled") is False
)
checks["scope_limited"] = (
    status.get("max_symbols_allowed") == 1
    and status.get("max_rows_allowed") == 300
    and status.get("symbol_allowlist") == ["VFV.TO"]
)

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "REAL_HISTORICAL_BAR_FETCH_GATE_ROLLUP",
    "artifacts": artifacts,
    "gate_status": status,
    "policy": {
        "historical_bar_fetch_gate_rollup_certified": True,
        "historical_bar_fetch_enabled": False,
        "real_historical_replay_enabled": False,
        "training_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": checks,
    "recommended_next_phase": "77J_REAL_HISTORICAL_BAR_FETCH_SOURCE_CREATION_PREVIEW",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        "",
        "Fetch gate rollup:",
        *[f"- {k}: {v}" for k, v in status.items()],
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
OUT = SANDBOX / "yfinance_historical_bars_adapter_wire_preview_latest.json"
TXT = SANDBOX / "yfinance_historical_bars_adapter_wire_preview_latest.txt"

ADAPTER = ROOT / "backend/app/stacks/market_data/yfinance_historical_bars_adapter.py"

if not ADAPTER.exists():
    raise SystemExit("Missing yfinance adapter. Run Phase 30D first.")

preview = {
    "phase": "30F_YFINANCE_HISTORICAL_BARS_ADAPTER_WIRE_PREVIEW",
    "generated_at": datetime.now(UTC).isoformat(),
    "wire_status": "preview_only",
    "adapter_path": str(ADAPTER),
    "selected_provider": "yfinance",
    "target_function": "get_historical_bars",
    "proposed_change": {
        "provider_wired": True,
        "market_data_enabled": True,
        "historical_replay_enabled": False,
        "simulation_enabled": False,
        "live_execution_enabled": False,
        "broker_execution_enabled": False,
        "registry_write_enabled": False,
    },
    "preview_rules": [
        "Only wire yfinance historical bars adapter.",
        "Only fetch bars on explicit later certification phase.",
        "Do not execute replay in this phase.",
        "Do not simulate trades in this phase.",
        "Do not mutate strategy registry.",
        "Do not enable broker or live execution.",
    ],
    "expected_runtime_shape": {
        "symbol": "string",
        "provider": "yfinance",
        "bars": "list",
        "bar_count": "integer",
        "status": "ok|error",
        "error": "string|null",
    },
    "hard_locks": {
        "historical_replay_enabled": False,
        "simulation_enabled": False,
        "monte_carlo_enabled": False,
        "promotion_enabled": False,
        "live_execution_enabled": False,
        "broker_execution_enabled": False,
        "registry_write_enabled": False,
    },
    "notes": [
        "Wire preview only.",
        "No source adapter mutation performed by this phase.",
        "No bars fetched.",
        "No replay executed.",
    ],
}

OUT.write_text(json.dumps(preview, indent=2))

TXT.write_text("\n".join([
    "YFINANCE HISTORICAL BARS ADAPTER WIRE PREVIEW",
    f"Generated: {preview['generated_at']}",
    "Wire Status: PREVIEW ONLY",
    "Provider: yfinance",
    "Target Function: get_historical_bars",
    "Proposed Provider Wired: TRUE",
    "Proposed Market Data Enabled: TRUE",
    "Historical Replay Enabled: FALSE",
    "Simulation Enabled: FALSE",
    "Live Execution Enabled: FALSE",
    "Broker Execution Enabled: FALSE",
    "Registry Write Enabled: FALSE",
]))

print(json.dumps({
    "status": "ok",
    "wire_status": preview["wire_status"],
    "output_json": str(OUT),
    "output_txt": str(TXT),
}, indent=2))

#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
ADAPTER_DIR = ROOT / "backend/app/stacks/market_data"
ADAPTER = ADAPTER_DIR / "yfinance_historical_bars_adapter.py"

OUT = SANDBOX / "yfinance_historical_bars_adapter_stub_latest.json"
TXT = SANDBOX / "yfinance_historical_bars_adapter_stub_latest.txt"

ADAPTER_DIR.mkdir(parents=True, exist_ok=True)
SANDBOX.mkdir(parents=True, exist_ok=True)

ADAPTER.write_text(r'''from __future__ import annotations

from typing import Any


def get_historical_bars(
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str = "1d",
) -> dict[str, Any]:
    return {
        "symbol": symbol,
        "provider": "yfinance",
        "bars": [],
        "bar_count": 0,
        "status": "not_wired",
        "error": "yfinance_historical_bars_adapter_stub_only",
        "execution_flags": {
            "provider_wired": False,
            "market_data_enabled": False,
            "historical_replay_enabled": False,
            "simulation_enabled": False,
            "live_execution_enabled": False,
            "broker_execution_enabled": False,
            "registry_write_enabled": False,
        },
    }
''')

snapshot = {
    "phase": "30D_YFINANCE_HISTORICAL_BARS_ADAPTER_STUB",
    "generated_at": datetime.now(UTC).isoformat(),
    "adapter_path": str(ADAPTER),
    "adapter_status": "stub_only",
    "selected_provider": "yfinance",
    "required_function": "get_historical_bars",
    "provider_wired": False,
    "market_data_enabled": False,
    "historical_replay_enabled": False,
    "simulation_enabled": False,
    "live_execution_enabled": False,
    "broker_execution_enabled": False,
    "registry_write_enabled": False,
}

OUT.write_text(json.dumps(snapshot, indent=2))

TXT.write_text("\n".join([
    "YFINANCE HISTORICAL BARS ADAPTER STUB",
    f"Generated: {snapshot['generated_at']}",
    f"Adapter: {snapshot['adapter_path']}",
    "Adapter Status: STUB ONLY",
    "Provider Wired: FALSE",
    "Market Data Enabled: FALSE",
    "Historical Replay Enabled: FALSE",
    "Simulation Enabled: FALSE",
    "Live Execution Enabled: FALSE",
    "Broker Execution Enabled: FALSE",
    "Registry Write Enabled: FALSE",
]))

print(json.dumps({
    "status": "ok",
    "adapter": str(ADAPTER),
    "snapshot_json": str(OUT),
    "snapshot_txt": str(TXT),
}, indent=2))

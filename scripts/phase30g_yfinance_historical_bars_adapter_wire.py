#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
ADAPTER = ROOT / "backend/app/stacks/market_data/yfinance_historical_bars_adapter.py"
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
OUT = SANDBOX / "yfinance_historical_bars_adapter_wire_latest.json"

ADAPTER.write_text(r'''from __future__ import annotations

from typing import Any
import math


def _clean_number(value: Any) -> float | None:
    try:
        number = float(value)
        if math.isnan(number):
            return None
        return number
    except Exception:
        return None


def get_historical_bars(
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str = "1d",
) -> dict[str, Any]:
    try:
        import yfinance as yf

        frame = yf.download(
            symbol,
            start=start_date,
            end=end_date,
            interval=interval,
            progress=False,
            auto_adjust=False,
            threads=False,
        )

        bars = []

        if frame is not None and not frame.empty:
            for timestamp, row in frame.iterrows():
                open_value = _clean_number(row.get("Open"))
                high_value = _clean_number(row.get("High"))
                low_value = _clean_number(row.get("Low"))
                close_value = _clean_number(row.get("Close"))
                volume_value = _clean_number(row.get("Volume"))

                if None in (open_value, high_value, low_value, close_value):
                    continue

                bars.append({
                    "timestamp": timestamp.isoformat(),
                    "open": open_value,
                    "high": high_value,
                    "low": low_value,
                    "close": close_value,
                    "volume": volume_value,
                })

        return {
            "symbol": symbol,
            "provider": "yfinance",
            "bars": bars,
            "bar_count": len(bars),
            "status": "ok" if bars else "empty",
            "error": None if bars else "no_bars_returned",
            "execution_flags": {
                "provider_wired": True,
                "market_data_enabled": True,
                "historical_replay_enabled": False,
                "simulation_enabled": False,
                "live_execution_enabled": False,
                "broker_execution_enabled": False,
                "registry_write_enabled": False,
            },
        }

    except Exception as exc:
        return {
            "symbol": symbol,
            "provider": "yfinance",
            "bars": [],
            "bar_count": 0,
            "status": "error",
            "error": f"{type(exc).__name__}: {exc}",
            "execution_flags": {
                "provider_wired": True,
                "market_data_enabled": True,
                "historical_replay_enabled": False,
                "simulation_enabled": False,
                "live_execution_enabled": False,
                "broker_execution_enabled": False,
                "registry_write_enabled": False,
            },
        }
''')

snapshot = {
    "phase": "30G_YFINANCE_HISTORICAL_BARS_ADAPTER_WIRE",
    "generated_at": datetime.now(UTC).isoformat(),
    "adapter_path": str(ADAPTER),
    "provider_wired": True,
    "market_data_enabled": True,
    "historical_replay_enabled": False,
    "simulation_enabled": False,
    "live_execution_enabled": False,
    "broker_execution_enabled": False,
    "registry_write_enabled": False,
}

OUT.write_text(json.dumps(snapshot, indent=2))
print(json.dumps({"status": "ok", "adapter": str(ADAPTER), "snapshot": str(OUT)}, indent=2))

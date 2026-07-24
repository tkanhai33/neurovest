from __future__ import annotations

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
            # yfinance 1.x may return MultiIndex columns such as:
            #
            #   ("Open", "AAPL")
            #   ("High", "AAPL")
            #
            # Normalize the requested symbol into a simple OHLCV
            # DataFrame before iterating. Older single-level DataFrames
            # continue through unchanged.
            normalized_frame = frame

            if getattr(frame.columns, "nlevels", 1) > 1:
                symbol_upper = symbol.strip().upper()

                level_zero = {
                    str(value)
                    for value
                    in frame.columns.get_level_values(0)
                }

                level_one = {
                    str(value).upper()
                    for value
                    in frame.columns.get_level_values(1)
                }

                if symbol_upper in level_one:
                    normalized_frame = frame.xs(
                        symbol_upper,
                        axis=1,
                        level=1,
                        drop_level=True,
                    )

                elif symbol in frame.columns.get_level_values(1):
                    normalized_frame = frame.xs(
                        symbol,
                        axis=1,
                        level=1,
                        drop_level=True,
                    )

                elif {
                    "Open",
                    "High",
                    "Low",
                    "Close",
                }.issubset(level_zero):
                    normalized_frame = frame.copy()
                    normalized_frame.columns = (
                        normalized_frame.columns
                        .get_level_values(0)
                    )

                else:
                    raise ValueError(
                        "Unsupported yfinance MultiIndex "
                        f"columns for {symbol}: "
                        f"{list(frame.columns)}"
                    )

            for timestamp, row in normalized_frame.iterrows():
                open_value = _clean_number(
                    row.get("Open")
                )
                high_value = _clean_number(
                    row.get("High")
                )
                low_value = _clean_number(
                    row.get("Low")
                )
                close_value = _clean_number(
                    row.get("Close")
                )
                volume_value = _clean_number(
                    row.get("Volume")
                )

                if None in (
                    open_value,
                    high_value,
                    low_value,
                    close_value,
                ):
                    continue

                bars.append({
                    "timestamp": timestamp.isoformat(),
                    "open": open_value,
                    "high": high_value,
                    "low": low_value,
                    "close": close_value,
                    "volume": (
                        volume_value
                        if volume_value is not None
                        else 0.0
                    ),
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

from __future__ import annotations

import pytest

from backend.app.stacks.market_data import multi_symbol_bars


def _bars(symbol: str, count: int) -> list[dict[str, object]]:
    return [
        {
            "timestamp": f"2026-01-{index + 1:02d}T00:00:00+00:00",
            "open": 100.0 + index,
            "high": 101.0 + index,
            "low": 99.0 + index,
            "close": 100.5 + index,
            "volume": 1000.0 + index,
            "symbol": symbol,
        }
        for index in range(count)
    ]


def test_normalizes_deduplicates_and_preserves_request_order(monkeypatch):
    calls: list[tuple[str, int]] = []

    def fake_get_bars(symbol: str, limit: int):
        calls.append((symbol, limit))
        return _bars(symbol, limit)

    monkeypatch.setattr(multi_symbol_bars, "get_bars", fake_get_bars)

    result = multi_symbol_bars.get_daily_bars_for_symbols(
        [" aapl ", "MSFT", "aapl"],
        limit=3,
    )

    assert tuple(result) == ("AAPL", "MSFT")
    assert calls == [("AAPL", 3), ("MSFT", 3)]
    assert all(len(bars) == 3 for bars in result.values())


def test_fails_closed_when_one_symbol_cannot_supply_history(monkeypatch):
    def fake_get_bars(symbol: str, limit: int):
        if symbol == "BAD":
            raise RuntimeError("insufficient truthful history")
        return _bars(symbol, limit)

    monkeypatch.setattr(multi_symbol_bars, "get_bars", fake_get_bars)

    with pytest.raises(RuntimeError, match="insufficient truthful history"):
        multi_symbol_bars.get_daily_bars_for_symbols(
            ["AAPL", "BAD"],
            limit=253,
        )


@pytest.mark.parametrize(
    "symbols",
    (
        [],
        ["AAPL", ""],
        "AAPL",
    ),
)
def test_rejects_invalid_symbol_requests(symbols):
    with pytest.raises(multi_symbol_bars.MultiSymbolBarsContractError):
        multi_symbol_bars.get_daily_bars_for_symbols(symbols)

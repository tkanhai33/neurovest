import asyncio

from backend.app.stacks.market_data import (
    market_data_service,
)


def test_bulk_quotes_normalize_and_cache(
    monkeypatch,
) -> None:
    market_data_service._bulk_quote_cache.clear()
    requested: list[str] = []

    async def fake_quote(
        symbol: str,
    ) -> dict[str, object]:
        requested.append(symbol)

        return {
            "status": "ok",
            "symbol": symbol,
            "price": 100.0,
            "provider": "yfinance",
        }

    monkeypatch.setattr(
        market_data_service,
        "get_live_price_quote",
        fake_quote,
    )

    first = asyncio.run(
        market_data_service.get_live_market_prices_for_api(
            [" aapl ", "MSFT", "AAPL"],
        )
    )

    assert first["status"] == "ok"
    assert first["requested_count"] == 2
    assert set(first["quotes"]) == {"AAPL", "MSFT"}
    assert requested == ["AAPL", "MSFT"]

    asyncio.run(
        market_data_service.get_live_market_prices_for_api(
            ["AAPL", "MSFT"],
        )
    )

    assert requested == ["AAPL", "MSFT"]


def test_bulk_quotes_reject_more_than_250_symbols() -> None:
    result = asyncio.run(
        market_data_service.get_live_market_prices_for_api(
            [
                f"TEST{index}"
                for index in range(251)
            ]
        )
    )

    assert result["status"] == "error"
    assert result["error"] == "too_many_symbols:250"

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from backend.app.stacks.market_data.dto import (
    HistoricalBarsRequest,
    HistoricalBarsResult,
    MarketDataCapability,
    MarketQuote,
    MarketSessionState,
)
from backend.app.stacks.market_data.provider_contract import (
    MarketDataProvider,
    verify_provider_shape,
)
from backend.app.stacks.market_data.yfinance_provider import (
    YFinanceHistoricalBarsError,
    YFinanceNormalizationError,
    YFinanceProvider,
    YFinanceQuoteError,
)


def fixture_provider(
    *,
    quote_loader=None,
    historical_loader=None,
) -> YFinanceProvider:
    return YFinanceProvider(
        quote_loader=(
            quote_loader
            or (
                lambda symbol: {
                    "symbol": symbol,
                    "price": 100.0,
                }
            )
        ),
        historical_loader=(
            historical_loader
            or (
                lambda *args: {
                    "bars": [],
                }
            )
        ),
    )


def test_module_import_does_not_require_yfinance() -> None:
    provider = YFinanceProvider()

    assert provider.provider_name == "yfinance"


def test_wrapper_satisfies_provider_contract() -> None:
    provider = fixture_provider()

    assert isinstance(
        provider,
        MarketDataProvider,
    )

    valid, missing = verify_provider_shape(
        provider
    )

    assert valid is True
    assert missing == ()


def test_capabilities_are_declared() -> None:
    provider = fixture_provider()

    assert provider.supports(
        MarketDataCapability.QUOTE
    )

    assert provider.supports(
        MarketDataCapability.HISTORICAL_BARS
    )

    assert not provider.supports(
        MarketDataCapability.MARKET_STATUS
    )


def test_numeric_quote_is_normalized() -> None:
    provider = fixture_provider(
        quote_loader=lambda symbol: 123.45
    )

    quote = provider.get_quote(
        " aapl "
    )

    assert isinstance(
        quote,
        MarketQuote,
    )
    assert quote.symbol == "AAPL"
    assert quote.price == 123.45
    assert quote.currency == "USD"
    assert quote.provider == "yfinance"


def test_mapping_quote_is_normalized() -> None:
    provider = fixture_provider(
        quote_loader=lambda symbol: {
            "ticker": symbol,
            "regularMarketPrice": 201.5,
            "currency": "cad",
            "bid": 201.0,
            "ask": 202.0,
            "regularMarketPreviousClose": 199.0,
            "regularMarketVolume": 5000,
            "marketState": "REGULAR",
            "regularMarketTime": 1783706400,
        }
    )

    quote = provider.get_quote(
        "shop.to"
    )

    assert quote.symbol == "SHOP.TO"
    assert quote.price == 201.5
    assert quote.currency == "CAD"
    assert quote.bid == 201.0
    assert quote.ask == 202.0
    assert quote.previous_close == 199.0
    assert quote.volume == 5000.0
    assert quote.session == (
        MarketSessionState.OPEN
    )


def test_quote_symbol_mismatch_fails() -> None:
    provider = fixture_provider(
        quote_loader=lambda symbol: {
            "symbol": "MSFT",
            "price": 100.0,
        }
    )

    with pytest.raises(
        YFinanceNormalizationError,
        match="does not match",
    ):
        provider.get_quote(
            "AAPL"
        )


def test_quote_loader_failure_is_translated() -> None:
    def fail(
        symbol: str,
    ) -> object:
        raise TimeoutError(
            "provider timeout"
        )

    provider = fixture_provider(
        quote_loader=fail
    )

    with pytest.raises(
        YFinanceQuoteError,
        match="retrieval failed",
    ):
        provider.get_quote(
            "AAPL"
        )


def test_historical_mapping_is_normalized() -> None:
    received = {}

    def loader(
        symbol: str,
        start: str,
        end: str,
        interval: str,
    ) -> object:
        received.update(
            {
                "symbol": symbol,
                "start": start,
                "end": end,
                "interval": interval,
            }
        )

        return {
            "bars": [
                {
                    "symbol": symbol,
                    "timestamp": (
                        "2026-07-02T00:00:00+00:00"
                    ),
                    "open": 100.0,
                    "high": 105.0,
                    "low": 99.0,
                    "close": 104.0,
                    "volume": 1000,
                },
                {
                    "symbol": symbol,
                    "timestamp": (
                        "2026-07-03T00:00:00+00:00"
                    ),
                    "open": 104.0,
                    "high": 106.0,
                    "low": 103.0,
                    "close": 105.0,
                    "volume": 1500,
                },
            ],
            "complete": True,
        }

    provider = fixture_provider(
        historical_loader=loader
    )

    request = HistoricalBarsRequest(
        symbol="AAPL",
        start=datetime(
            2026,
            7,
            1,
            tzinfo=UTC,
        ),
        end=datetime(
            2026,
            7,
            5,
            tzinfo=UTC,
        ),
        interval="1d",
    )

    result = provider.get_historical_bars(
        request
    )

    assert isinstance(
        result,
        HistoricalBarsResult,
    )
    assert result.provider == "yfinance"
    assert len(result.bars) == 2
    assert result.bars[0].close == 104.0
    assert result.bars[1].close == 105.0

    assert received == {
        "symbol": "AAPL",
        "start": "2026-07-01",
        "end": "2026-07-05",
        "interval": "1d",
    }


def test_historical_rows_are_sorted() -> None:
    provider = fixture_provider(
        historical_loader=lambda *args: {
            "bars": [
                {
                    "timestamp": (
                        "2026-07-03T00:00:00+00:00"
                    ),
                    "open": 104,
                    "high": 106,
                    "low": 103,
                    "close": 105,
                    "volume": 20,
                },
                {
                    "timestamp": (
                        "2026-07-02T00:00:00+00:00"
                    ),
                    "open": 100,
                    "high": 105,
                    "low": 99,
                    "close": 104,
                    "volume": 10,
                },
            ]
        }
    )

    now = datetime(
        2026,
        7,
        5,
        tzinfo=UTC,
    )

    request = HistoricalBarsRequest(
        symbol="AAPL",
        start=now - timedelta(
            days=5
        ),
        end=now,
    )

    result = provider.get_historical_bars(
        request
    )

    assert (
        result.bars[0].timestamp
        < result.bars[1].timestamp
    )


def test_historical_limit_is_applied() -> None:
    provider = fixture_provider(
        historical_loader=lambda *args: {
            "bars": [
                {
                    "timestamp": (
                        "2026-07-02T00:00:00+00:00"
                    ),
                    "open": 100,
                    "high": 101,
                    "low": 99,
                    "close": 100,
                    "volume": 10,
                },
                {
                    "timestamp": (
                        "2026-07-03T00:00:00+00:00"
                    ),
                    "open": 100,
                    "high": 102,
                    "low": 99,
                    "close": 101,
                    "volume": 20,
                },
            ]
        }
    )

    request = HistoricalBarsRequest(
        symbol="AAPL",
        start=datetime(
            2026,
            7,
            1,
            tzinfo=UTC,
        ),
        end=datetime(
            2026,
            7,
            5,
            tzinfo=UTC,
        ),
        limit=1,
    )

    result = provider.get_historical_bars(
        request
    )

    assert len(result.bars) == 1


def test_historical_loader_failure_is_translated() -> None:
    def fail(
        *args: object,
    ) -> object:
        raise ConnectionError(
            "connection failed"
        )

    provider = fixture_provider(
        historical_loader=fail
    )

    request = HistoricalBarsRequest(
        symbol="AAPL",
        start=datetime(
            2026,
            7,
            1,
            tzinfo=UTC,
        ),
        end=datetime(
            2026,
            7,
            5,
            tzinfo=UTC,
        ),
    )

    with pytest.raises(
        YFinanceHistoricalBarsError,
        match="retrieval failed",
    ):
        provider.get_historical_bars(
            request
        )


def test_healthcheck_does_not_load_dependencies() -> None:
    provider = YFinanceProvider()

    health = provider.healthcheck()

    assert health.healthy is True
    assert health.provider == "yfinance"

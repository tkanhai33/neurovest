from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from backend.app.stacks.market_data.dto import (
    HistoricalBar,
    HistoricalBarsRequest,
    HistoricalBarsResult,
    MarketDataCapability,
    MarketQuote,
    MarketSessionState,
    ProviderHealth,
    normalize_symbol,
)
from backend.app.stacks.market_data.provider_contract import (
    MarketDataProvider,
    verify_provider_shape,
)


class ContractFixtureProvider:
    @property
    def provider_name(self) -> str:
        return "contract_fixture"

    @property
    def capabilities(
        self,
    ) -> frozenset[MarketDataCapability]:
        return frozenset(
            {
                MarketDataCapability.QUOTE,
                MarketDataCapability.HISTORICAL_BARS,
            }
        )

    def supports(
        self,
        capability: MarketDataCapability,
    ) -> bool:
        return capability in self.capabilities

    def get_quote(
        self,
        symbol: str,
    ) -> MarketQuote:
        return MarketQuote(
            symbol=symbol,
            price=100.0,
            currency="CAD",
            observed_at=datetime.now(
                UTC
            ),
            provider=self.provider_name,
            bid=99.5,
            ask=100.5,
            session=(
                MarketSessionState.OPEN
            ),
        )

    def get_historical_bars(
        self,
        request: HistoricalBarsRequest,
    ) -> HistoricalBarsResult:
        bar = HistoricalBar(
            symbol=request.symbol,
            timestamp=request.start,
            interval=request.interval,
            open=99.0,
            high=101.0,
            low=98.0,
            close=100.0,
            volume=1000.0,
            provider=self.provider_name,
        )

        return HistoricalBarsResult(
            request=request,
            provider=self.provider_name,
            bars=(bar,),
            fetched_at=datetime.now(
                UTC
            ),
        )

    def healthcheck(
        self,
    ) -> ProviderHealth:
        return ProviderHealth(
            provider=self.provider_name,
            healthy=True,
            checked_at=datetime.now(
                UTC
            ),
            capabilities=self.capabilities,
        )


def test_symbol_normalization() -> None:
    assert normalize_symbol(
        " aapl "
    ) == "AAPL"

    assert normalize_symbol(
        "brk.b"
    ) == "BRK.B"


def test_empty_symbol_rejected() -> None:
    with pytest.raises(
        ValueError,
    ):
        normalize_symbol("   ")


def test_quote_normalizes_fields() -> None:
    quote = MarketQuote(
        symbol=" msft ",
        price=500.0,
        currency="usd",
        observed_at=datetime.now(
            UTC
        ),
        provider="fixture",
    )

    assert quote.symbol == "MSFT"
    assert quote.currency == "USD"
    assert quote.price == 500.0


def test_naive_quote_timestamp_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        MarketQuote(
            symbol="AAPL",
            price=100.0,
            currency="USD",
            observed_at=datetime.now(),
            provider="fixture",
        )


def test_invalid_ohlc_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="high",
    ):
        HistoricalBar(
            symbol="AAPL",
            timestamp=datetime.now(
                UTC
            ),
            interval="1d",
            open=100.0,
            high=90.0,
            low=95.0,
            close=98.0,
            volume=10.0,
            provider="fixture",
        )


def test_request_date_order_enforced() -> None:
    now = datetime.now(
        UTC
    )

    with pytest.raises(
        ValueError,
        match="start",
    ):
        HistoricalBarsRequest(
            symbol="AAPL",
            start=now,
            end=now - timedelta(
                days=1
            ),
        )


def test_result_requires_matching_symbol() -> None:
    now = datetime.now(
        UTC
    )

    request = HistoricalBarsRequest(
        symbol="AAPL",
        start=now - timedelta(
            days=2
        ),
        end=now,
    )

    mismatched_bar = HistoricalBar(
        symbol="MSFT",
        timestamp=request.start,
        interval=request.interval,
        open=99.0,
        high=101.0,
        low=98.0,
        close=100.0,
        volume=1000.0,
        provider="fixture",
    )

    with pytest.raises(
        ValueError,
        match="requested symbol",
    ):
        HistoricalBarsResult(
            request=request,
            provider="fixture",
            bars=(mismatched_bar,),
            fetched_at=now,
        )


def test_fixture_satisfies_protocol() -> None:
    provider = ContractFixtureProvider()

    assert isinstance(
        provider,
        MarketDataProvider,
    )

    valid, missing = (
        verify_provider_shape(
            provider
        )
    )

    assert valid is True
    assert missing == ()


def test_fixture_returns_canonical_quote() -> None:
    provider = ContractFixtureProvider()

    quote = provider.get_quote(
        "shop.to"
    )

    assert isinstance(
        quote,
        MarketQuote,
    )
    assert quote.symbol == "SHOP.TO"
    assert quote.provider == (
        provider.provider_name
    )


def test_fixture_returns_canonical_bars() -> None:
    provider = ContractFixtureProvider()

    now = datetime.now(
        UTC
    )

    request = HistoricalBarsRequest(
        symbol="AAPL",
        start=now - timedelta(
            days=5
        ),
        end=now,
    )

    result = (
        provider.get_historical_bars(
            request
        )
    )

    assert isinstance(
        result,
        HistoricalBarsResult,
    )
    assert len(result.bars) == 1
    assert result.bars[0].symbol == "AAPL"

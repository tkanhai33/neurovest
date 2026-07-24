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
)
from backend.app.stacks.market_data.market_session import (
    MarketSessionService,
)
from backend.app.stacks.market_data.provider_cache import (
    MarketDataCache,
)
from backend.app.stacks.market_data.provider_registry import (
    ProviderAlreadyRegisteredError,
    ProviderCapabilityUnavailableError,
    ProviderRegistry,
)
from backend.app.stacks.market_data.provider_router import (
    ProviderRouter,
    ProviderRoutingError,
)


class MutableClock:
    def __init__(self) -> None:
        self.value = 100.0

    def __call__(self) -> float:
        return self.value

    def advance(
        self,
        seconds: float,
    ) -> None:
        self.value += seconds


class FixtureProvider:
    def __init__(
        self,
        name: str,
        *,
        capabilities: frozenset[
            MarketDataCapability
        ],
        quote_price: float = 100.0,
        fail_quotes: bool = False,
        fail_bars: bool = False,
    ) -> None:
        self._name = name
        self._capabilities = capabilities
        self.quote_price = quote_price
        self.fail_quotes = fail_quotes
        self.fail_bars = fail_bars
        self.quote_calls = 0
        self.bar_calls = 0

    @property
    def provider_name(self) -> str:
        return self._name

    @property
    def capabilities(
        self,
    ) -> frozenset[
        MarketDataCapability
    ]:
        return self._capabilities

    def supports(
        self,
        capability: MarketDataCapability,
    ) -> bool:
        return capability in self.capabilities

    def get_quote(
        self,
        symbol: str,
    ) -> MarketQuote:
        self.quote_calls += 1

        if self.fail_quotes:
            raise RuntimeError(
                f"{self.provider_name} quote failure"
            )

        return MarketQuote(
            symbol=symbol,
            price=self.quote_price,
            currency="USD",
            observed_at=datetime.now(
                UTC
            ),
            provider=self.provider_name,
        )

    def get_historical_bars(
        self,
        request: HistoricalBarsRequest,
    ) -> HistoricalBarsResult:
        self.bar_calls += 1

        if self.fail_bars:
            raise RuntimeError(
                f"{self.provider_name} bar failure"
            )

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


def test_registry_registers_and_selects_by_priority() -> None:
    registry = ProviderRegistry()

    slow = FixtureProvider(
        "slow",
        capabilities=frozenset(
            {
                MarketDataCapability.QUOTE,
            }
        ),
    )

    preferred = FixtureProvider(
        "preferred",
        capabilities=frozenset(
            {
                MarketDataCapability.QUOTE,
            }
        ),
    )

    registry.register(
        slow,
        priority=50,
    )

    registry.register(
        preferred,
        priority=10,
    )

    selected = registry.select(
        MarketDataCapability.QUOTE
    )

    assert selected.provider_name == (
        "preferred"
    )


def test_registry_rejects_duplicate_name() -> None:
    registry = ProviderRegistry()

    provider = FixtureProvider(
        "fixture",
        capabilities=frozenset(),
    )

    registry.register(provider)

    with pytest.raises(
        ProviderAlreadyRegisteredError,
    ):
        registry.register(provider)


def test_registry_ignores_disabled_provider() -> None:
    registry = ProviderRegistry()

    provider = FixtureProvider(
        "fixture",
        capabilities=frozenset(
            {
                MarketDataCapability.QUOTE,
            }
        ),
    )

    registry.register(
        provider,
        enabled=False,
    )

    with pytest.raises(
        ProviderCapabilityUnavailableError,
    ):
        registry.select(
            MarketDataCapability.QUOTE
        )


def test_cache_returns_unexpired_value() -> None:
    clock = MutableClock()

    cache = MarketDataCache[
        str,
        int,
    ](
        maximum_size=2,
        default_ttl_seconds=10,
        clock=clock,
    )

    cache.set(
        "answer",
        42,
    )

    assert cache.get(
        "answer"
    ) == 42

    stats = cache.stats()

    assert stats.hits == 1
    assert stats.misses == 0


def test_cache_expires_value() -> None:
    clock = MutableClock()

    cache = MarketDataCache[
        str,
        int,
    ](
        maximum_size=2,
        default_ttl_seconds=10,
        clock=clock,
    )

    cache.set(
        "answer",
        42,
    )

    clock.advance(11)

    assert cache.get(
        "answer"
    ) is None

    stats = cache.stats()

    assert stats.expirations == 1
    assert stats.misses == 1


def test_cache_evicts_least_recently_used() -> None:
    clock = MutableClock()

    cache = MarketDataCache[
        str,
        int,
    ](
        maximum_size=2,
        default_ttl_seconds=10,
        clock=clock,
    )

    cache.set("a", 1)
    cache.set("b", 2)

    assert cache.get("a") == 1

    cache.set("c", 3)

    assert cache.get("b") is None
    assert cache.get("a") == 1
    assert cache.get("c") == 3
    assert cache.stats().evictions == 1


@pytest.mark.parametrize(
    (
        "moment",
        "expected",
    ),
    [
        (
            datetime(
                2026,
                7,
                6,
                12,
                0,
                tzinfo=UTC,
            ),
            MarketSessionState.PRE_MARKET,
        ),
        (
            datetime(
                2026,
                7,
                6,
                15,
                0,
                tzinfo=UTC,
            ),
            MarketSessionState.OPEN,
        ),
        (
            datetime(
                2026,
                7,
                6,
                21,
                0,
                tzinfo=UTC,
            ),
            MarketSessionState.AFTER_HOURS,
        ),
        (
            datetime(
                2026,
                7,
                5,
                15,
                0,
                tzinfo=UTC,
            ),
            MarketSessionState.CLOSED,
        ),
    ],
)
def test_market_session_classification(
    moment: datetime,
    expected: MarketSessionState,
) -> None:
    service = MarketSessionService()

    assert service.state_at(
        moment
    ) == expected


def test_market_session_rejects_naive_datetime() -> None:
    service = MarketSessionService()

    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        service.state_at(
            datetime.now()
        )


def test_router_uses_highest_priority_provider() -> None:
    registry = ProviderRegistry()

    first = FixtureProvider(
        "first",
        capabilities=frozenset(
            {
                MarketDataCapability.QUOTE,
            }
        ),
        quote_price=111.0,
    )

    second = FixtureProvider(
        "second",
        capabilities=frozenset(
            {
                MarketDataCapability.QUOTE,
            }
        ),
        quote_price=222.0,
    )

    registry.register(
        second,
        priority=20,
    )
    registry.register(
        first,
        priority=10,
    )

    router = ProviderRouter(
        registry
    )

    quote = router.get_quote(
        "aapl"
    )

    assert quote.provider == "first"
    assert quote.price == 111.0


def test_router_falls_back_after_provider_failure() -> None:
    registry = ProviderRegistry()

    failing = FixtureProvider(
        "failing",
        capabilities=frozenset(
            {
                MarketDataCapability.QUOTE,
            }
        ),
        fail_quotes=True,
    )

    fallback = FixtureProvider(
        "fallback",
        capabilities=frozenset(
            {
                MarketDataCapability.QUOTE,
            }
        ),
        quote_price=321.0,
    )

    registry.register(
        failing,
        priority=1,
    )
    registry.register(
        fallback,
        priority=2,
    )

    router = ProviderRouter(
        registry
    )

    quote = router.get_quote(
        "msft"
    )

    assert quote.provider == "fallback"
    assert failing.quote_calls == 1
    assert fallback.quote_calls == 1


def test_router_fails_closed_when_all_providers_fail() -> None:
    registry = ProviderRegistry()

    registry.register(
        FixtureProvider(
            "broken",
            capabilities=frozenset(
                {
                    MarketDataCapability.QUOTE,
                }
            ),
            fail_quotes=True,
        )
    )

    router = ProviderRouter(
        registry
    )

    with pytest.raises(
        ProviderRoutingError,
        match="all eligible providers failed",
    ):
        router.get_quote(
            "AAPL"
        )


def test_router_quote_cache_prevents_second_provider_call() -> None:
    registry = ProviderRegistry()

    provider = FixtureProvider(
        "fixture",
        capabilities=frozenset(
            {
                MarketDataCapability.QUOTE,
            }
        ),
    )

    registry.register(provider)

    cache = MarketDataCache[
        tuple[object, ...],
        object,
    ](
        maximum_size=10,
        default_ttl_seconds=60,
    )

    router = ProviderRouter(
        registry,
        cache=cache,
    )

    first = router.get_quote(
        "shop.to"
    )

    second = router.get_quote(
        "SHOP.TO"
    )

    assert first == second
    assert provider.quote_calls == 1


def test_router_returns_canonical_historical_result() -> None:
    registry = ProviderRegistry()

    provider = FixtureProvider(
        "fixture",
        capabilities=frozenset(
            {
                MarketDataCapability.HISTORICAL_BARS,
            }
        ),
    )

    registry.register(provider)

    router = ProviderRouter(
        registry
    )

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
        router.get_historical_bars(
            request
        )
    )

    assert isinstance(
        result,
        HistoricalBarsResult,
    )
    assert result.provider == "fixture"
    assert len(result.bars) == 1

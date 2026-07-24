from __future__ import annotations

import time
from datetime import UTC, datetime
from threading import Lock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.stacks.market_data.api_router import (
    router as market_data_router,
)
from backend.app.stacks.market_data.dto import (
    HistoricalBar,
    HistoricalBarsRequest,
    HistoricalBarsResult,
    MarketDataCapability,
    MarketQuote,
    ProviderHealth,
)
from backend.app.stacks.market_data.market_session import (
    MarketSessionService,
)
from backend.app.stacks.market_data.provider_cache import (
    MarketDataCache,
)
from backend.app.stacks.market_data.provider_registry import (
    ProviderRegistry,
)
from backend.app.stacks.market_data.provider_router import (
    ProviderRouter,
    ProviderRoutingError,
)
from backend.app.stacks.market_data.runtime_composition import (
    MarketDataRuntime,
    set_market_data_runtime_for_testing,
)


class ControlledProvider:
    def __init__(
        self,
        name: str,
        *,
        fail_quote: bool = False,
        fail_historical: bool = False,
        price: float = 123.45,
    ) -> None:
        self._name = name
        self.fail_quote = fail_quote
        self.fail_historical = fail_historical
        self.price = price

        self.quote_calls = 0
        self.historical_calls = 0

        self._lock = Lock()

    @property
    def provider_name(self) -> str:
        return self._name

    @property
    def capabilities(
        self,
    ) -> frozenset[
        MarketDataCapability
    ]:
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
        with self._lock:
            self.quote_calls += 1

        if self.fail_quote:
            raise RuntimeError(
                f"{self.provider_name} quote failure"
            )

        return MarketQuote(
            symbol=symbol,
            price=self.price,
            currency="USD",
            observed_at=datetime(
                2026,
                7,
                10,
                tzinfo=UTC,
            ),
            provider=self.provider_name,
        )

    def get_historical_bars(
        self,
        request: HistoricalBarsRequest,
    ) -> HistoricalBarsResult:
        with self._lock:
            self.historical_calls += 1

        if self.fail_historical:
            raise RuntimeError(
                f"{self.provider_name} historical failure"
            )

        bar = HistoricalBar(
            symbol=request.symbol,
            timestamp=request.start,
            interval=request.interval,
            open=100.0,
            high=125.0,
            low=99.0,
            close=self.price,
            volume=1000.0,
            provider=self.provider_name,
        )

        return HistoricalBarsResult(
            request=request,
            provider=self.provider_name,
            bars=(bar,),
            fetched_at=datetime(
                2026,
                7,
                10,
                tzinfo=UTC,
            ),
        )

    def healthcheck(
        self,
    ) -> ProviderHealth:
        return ProviderHealth(
            provider=self.provider_name,
            healthy=True,
            checked_at=datetime(
                2026,
                7,
                10,
                tzinfo=UTC,
            ),
            capabilities=self.capabilities,
        )


def build_runtime(
    providers: list[
        ControlledProvider
    ],
    *,
    quote_ttl: float = 30.0,
    historical_ttl: float = 300.0,
) -> MarketDataRuntime:
    registry = ProviderRegistry()

    for index, provider in enumerate(
        providers,
        start=1,
    ):
        registry.register(
            provider,
            priority=index,
            enabled=True,
        )

    cache = MarketDataCache[
        tuple[object, ...],
        object,
    ](
        maximum_size=64,
        default_ttl_seconds=quote_ttl,
    )

    session = MarketSessionService()

    router = ProviderRouter(
        registry,
        cache=cache,
        quote_ttl_seconds=quote_ttl,
        historical_ttl_seconds=historical_ttl,
    )

    return MarketDataRuntime(
        registry=registry,
        cache=cache,
        session=session,
        router=router,
    )


def test_quote_cache_prevents_repeated_provider_call() -> None:
    provider = ControlledProvider(
        "cache-provider"
    )

    runtime = build_runtime(
        [provider],
        quote_ttl=30.0,
    )

    first = runtime.router.get_quote(
        "AAPL",
        use_cache=True,
    )

    second = runtime.router.get_quote(
        "AAPL",
        use_cache=True,
    )

    assert first == second
    assert provider.quote_calls == 1

    stats = runtime.cache.stats()

    assert stats.hits >= 1
    assert stats.size >= 1


def test_quote_cache_expiry_forces_refresh() -> None:
    provider = ControlledProvider(
        "expiry-provider"
    )

    runtime = build_runtime(
        [provider],
        quote_ttl=0.05,
    )

    runtime.router.get_quote(
        "AAPL",
        use_cache=True,
    )

    time.sleep(
        0.08
    )

    runtime.router.get_quote(
        "AAPL",
        use_cache=True,
    )

    assert provider.quote_calls == 2

    stats = runtime.cache.stats()

    assert stats.expirations >= 1


def test_use_cache_false_always_calls_provider() -> None:
    provider = ControlledProvider(
        "uncached-provider"
    )

    runtime = build_runtime(
        [provider]
    )

    runtime.router.get_quote(
        "AAPL",
        use_cache=False,
    )

    runtime.router.get_quote(
        "AAPL",
        use_cache=False,
    )

    assert provider.quote_calls == 2


def test_router_falls_back_after_quote_failure() -> None:
    first = ControlledProvider(
        "first"
    )

    second = ControlledProvider(
        "second"
    )

    runtime = build_runtime(
        [
            first,
            second,
        ]
    )

    ordered = runtime.registry.providers_for(
        MarketDataCapability.QUOTE
    )

    assert len(ordered) == 2

    ordered[0].fail_quote = True
    ordered[1].fail_quote = False

    quote = runtime.router.get_quote(
        "AAPL",
        use_cache=False,
    )

    assert quote.provider == (
        ordered[1].provider_name
    )

    assert (
        ordered[0].quote_calls
        == 1
    )

    assert (
        ordered[1].quote_calls
        == 1
    )


def test_router_falls_back_after_historical_failure() -> None:
    first = ControlledProvider(
        "first"
    )

    second = ControlledProvider(
        "second"
    )

    runtime = build_runtime(
        [
            first,
            second,
        ]
    )

    ordered = runtime.registry.providers_for(
        MarketDataCapability.HISTORICAL_BARS
    )

    ordered[0].fail_historical = True
    ordered[1].fail_historical = False

    request = HistoricalBarsRequest(
        symbol="AAPL",
        start=datetime(
            2024,
            1,
            2,
            tzinfo=UTC,
        ),
        end=datetime(
            2024,
            2,
            1,
            tzinfo=UTC,
        ),
        interval="1d",
        adjusted=True,
        limit=10,
    )

    result = (
        runtime.router
        .get_historical_bars(
            request,
            use_cache=False,
        )
    )

    assert result.provider == (
        ordered[1].provider_name
    )


def test_router_fails_closed_when_every_provider_fails() -> None:
    first = ControlledProvider(
        "first",
        fail_quote=True,
    )

    second = ControlledProvider(
        "second",
        fail_quote=True,
    )

    runtime = build_runtime(
        [
            first,
            second,
        ]
    )

    try:
        runtime.router.get_quote(
            "AAPL",
            use_cache=False,
        )

    except ProviderRoutingError as exc:
        message = str(
            exc
        )

        assert "first" in message
        assert "second" in message

    else:
        raise AssertionError(
            "ProviderRoutingError was not raised"
        )


def test_api_translates_provider_failure_to_503() -> None:
    provider = ControlledProvider(
        "failed-provider",
        fail_quote=True,
    )

    runtime = build_runtime(
        [provider]
    )

    set_market_data_runtime_for_testing(
        runtime
    )

    try:
        app = FastAPI()
        app.include_router(
            market_data_router
        )

        client = TestClient(
            app
        )

        response = client.get(
            "/api/v1/market-data/quote/AAPL",
            params={
                "use_cache": "false",
            },
        )

        assert response.status_code == 503

        payload = response.json()

        assert payload[
            "detail"
        ][
            "error"
        ] == "market_data_unavailable"

    finally:
        set_market_data_runtime_for_testing(
            None
        )


def test_api_rejects_invalid_historical_range() -> None:
    provider = ControlledProvider(
        "fixture"
    )

    runtime = build_runtime(
        [provider]
    )

    set_market_data_runtime_for_testing(
        runtime
    )

    try:
        app = FastAPI()
        app.include_router(
            market_data_router
        )

        client = TestClient(
            app
        )

        response = client.get(
            "/api/v1/market-data/historical/AAPL",
            params={
                "start": "2024-02-01",
                "end": "2024-01-02",
            },
        )

        assert response.status_code == 422

    finally:
        set_market_data_runtime_for_testing(
            None
        )


def test_status_endpoint_does_not_call_provider() -> None:
    provider = ControlledProvider(
        "status-provider"
    )

    runtime = build_runtime(
        [provider]
    )

    set_market_data_runtime_for_testing(
        runtime
    )

    try:
        app = FastAPI()
        app.include_router(
            market_data_router
        )

        client = TestClient(
            app
        )

        response = client.get(
            "/api/v1/market-data/status"
        )

        assert response.status_code == 200

        assert provider.quote_calls == 0
        assert provider.historical_calls == 0

        payload = response.json()

        assert payload[
            "mode"
        ] == "read_only"

        assert payload[
            "broker_execution_enabled"
        ] is False

        assert payload[
            "live_trading_enabled"
        ] is False

    finally:
        set_market_data_runtime_for_testing(
            None
        )

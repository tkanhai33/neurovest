from __future__ import annotations

from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.stacks.market_data.api_router import (
    router,
)
from backend.app.stacks.market_data.dto import (
    HistoricalBar,
    HistoricalBarsRequest,
    HistoricalBarsResult,
    MarketDataCapability,
    MarketQuote,
    ProviderHealth,
)
from backend.app.stacks.market_data.runtime_composition import (
    build_market_data_runtime,
    get_market_data_runtime,
    reset_market_data_runtime,
    set_market_data_runtime_for_testing,
)


class FixtureProvider:
    @property
    def provider_name(self) -> str:
        return "fixture"

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
        return MarketQuote(
            symbol=symbol,
            price=123.45,
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
        bar = HistoricalBar(
            symbol=request.symbol,
            timestamp=request.start,
            interval=request.interval,
            open=100.0,
            high=125.0,
            low=99.0,
            close=123.45,
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


def build_fixture_runtime():
    runtime = build_market_data_runtime(
        register_yfinance=False
    )

    runtime.registry.register(
        FixtureProvider(),
        priority=1,
    )

    return runtime


def test_production_runtime_constructs_without_network() -> None:
    reset_market_data_runtime()

    runtime = get_market_data_runtime()

    records = runtime.registry.records(
        include_disabled=True
    )

    assert len(records) == 1
    assert records[0].name == "yfinance"
    assert records[0].enabled is True

    reset_market_data_runtime()


def test_runtime_components_are_shared() -> None:
    reset_market_data_runtime()

    first = get_market_data_runtime()
    second = get_market_data_runtime()

    assert first is second

    reset_market_data_runtime()


def test_read_only_routes_are_declared() -> None:
    paths = {
        route.path
        for route in router.routes
    }

    assert (
        "/api/v1/market-data/status"
        in paths
    )

    assert (
        "/api/v1/market-data/quote/{symbol}"
        in paths
    )

    assert (
        "/api/v1/market-data/historical/{symbol}"
        in paths
    )


def test_status_endpoint_is_network_free() -> None:
    runtime = build_fixture_runtime()

    set_market_data_runtime_for_testing(
        runtime
    )

    app = FastAPI()
    app.include_router(router)

    client = TestClient(app)

    response = client.get(
        "/api/v1/market-data/status"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "ready"
    assert payload["mode"] == "read_only"
    assert payload[
        "broker_execution_enabled"
    ] is False
    assert payload[
        "live_trading_enabled"
    ] is False

    set_market_data_runtime_for_testing(
        None
    )


def test_quote_endpoint_uses_shared_router() -> None:
    runtime = build_fixture_runtime()

    set_market_data_runtime_for_testing(
        runtime
    )

    app = FastAPI()
    app.include_router(router)

    client = TestClient(app)

    response = client.get(
        "/api/v1/market-data/quote/AAPL"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["symbol"] == "AAPL"
    assert payload["price"] == 123.45
    assert payload["provider"] == "fixture"

    set_market_data_runtime_for_testing(
        None
    )


def test_historical_endpoint_uses_shared_router() -> None:
    runtime = build_fixture_runtime()

    set_market_data_runtime_for_testing(
        runtime
    )

    app = FastAPI()
    app.include_router(router)

    client = TestClient(app)

    response = client.get(
        "/api/v1/market-data/historical/AAPL",
        params={
            "start": (
                "2024-01-02T00:00:00+00:00"
            ),
            "end": (
                "2024-02-01T00:00:00+00:00"
            ),
            "interval": "1d",
            "limit": 10,
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload[
        "provider"
    ] == "fixture"

    assert len(
        payload["bars"]
    ) == 1

    assert payload[
        "bars"
    ][0]["symbol"] == "AAPL"

    set_market_data_runtime_for_testing(
        None
    )


def test_invalid_historical_range_fails_closed() -> None:
    runtime = build_fixture_runtime()

    set_market_data_runtime_for_testing(
        runtime
    )

    app = FastAPI()
    app.include_router(router)

    client = TestClient(app)

    response = client.get(
        "/api/v1/market-data/historical/AAPL",
        params={
            "start": "2024-02-01",
            "end": "2024-01-02",
        },
    )

    assert response.status_code == 422

    set_market_data_runtime_for_testing(
        None
    )

"""
Canonical market-data runtime composition root.

This module owns construction of the read-only market-data runtime:

- provider registry
- bounded process-local cache
- market-session service
- provider router
- YFinanceProvider registration

It performs no market-data network call during construction.

Broker execution, order execution, portfolio mutation, and live trading
are outside this composition root.
"""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock

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
)
from backend.app.stacks.market_data.yfinance_provider import (
    YFinanceProvider,
)


@dataclass(
    frozen=True,
    slots=True,
)
class MarketDataRuntime:
    registry: ProviderRegistry
    cache: MarketDataCache[
        tuple[object, ...],
        object,
    ]
    session: MarketSessionService
    router: ProviderRouter


def build_market_data_runtime(
    *,
    register_yfinance: bool = True,
) -> MarketDataRuntime:
    """
    Construct an isolated read-only market-data runtime.

    Construction performs no external provider call.
    """

    registry = ProviderRegistry()

    cache = MarketDataCache[
        tuple[object, ...],
        object,
    ](
        maximum_size=2048,
        default_ttl_seconds=30.0,
    )

    session = MarketSessionService()

    if register_yfinance:
        registry.register(
            YFinanceProvider(),
            priority=100,
            enabled=True,
        )

    router = ProviderRouter(
        registry,
        cache=cache,
        quote_ttl_seconds=5.0,
        historical_ttl_seconds=300.0,
    )

    return MarketDataRuntime(
        registry=registry,
        cache=cache,
        session=session,
        router=router,
    )


_RUNTIME_LOCK = RLock()

_RUNTIME: MarketDataRuntime | None = None

_TEST_RUNTIME_OVERRIDE: MarketDataRuntime | None = None


def get_market_data_runtime() -> MarketDataRuntime:
    """
    Return the shared process-local read-only market-data runtime.
    """

    global _RUNTIME

    with _RUNTIME_LOCK:
        if _TEST_RUNTIME_OVERRIDE is not None:
            return _TEST_RUNTIME_OVERRIDE

        if _RUNTIME is None:
            _RUNTIME = build_market_data_runtime()

        return _RUNTIME


def set_market_data_runtime_for_testing(
    runtime: MarketDataRuntime | None,
) -> None:
    """
    Install or clear a test-only runtime override.

    Production application code must not call this function.
    """

    global _TEST_RUNTIME_OVERRIDE

    with _RUNTIME_LOCK:
        _TEST_RUNTIME_OVERRIDE = runtime


def reset_market_data_runtime() -> None:
    """
    Clear the shared runtime without performing provider operations.
    """

    global _RUNTIME
    global _TEST_RUNTIME_OVERRIDE

    with _RUNTIME_LOCK:
        _RUNTIME = None
        _TEST_RUNTIME_OVERRIDE = None


def healthcheck() -> dict[str, object]:
    """
    Return construction-level health without calling a provider.
    """

    runtime = get_market_data_runtime()

    records = runtime.registry.records(
        include_disabled=True
    )

    return {
        "component": "market_data_runtime",
        "healthy": bool(records),
        "providers": [
            {
                "name": record.name,
                "priority": record.priority,
                "enabled": record.enabled,
            }
            for record in records
        ],
        "network_called": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
    }

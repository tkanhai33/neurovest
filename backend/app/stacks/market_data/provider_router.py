"""
Fail-closed market-data provider router.

The router selects providers through ProviderRegistry, returns canonical
DTOs, applies optional TTL caching, and falls back only to other
registered providers supporting the same capability.

It does not register external adapters or modify application startup.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, TypeVar

from backend.app.stacks.market_data.dto import (
    HistoricalBarsRequest,
    HistoricalBarsResult,
    MarketDataCapability,
    MarketQuote,
    normalize_symbol,
)
from backend.app.stacks.market_data.provider_cache import (
    MarketDataCache,
)
from backend.app.stacks.market_data.provider_registry import (
    ProviderCapabilityUnavailableError,
    ProviderRegistry,
)


ResultT = TypeVar(
    "ResultT",
)


class ProviderRoutingError(RuntimeError):
    """Raised when all eligible providers fail."""


@dataclass(
    frozen=True,
    slots=True,
)
class ProviderAttempt:
    provider: str
    succeeded: bool
    error_type: str | None = None
    error_message: str | None = None


class ProviderRouter:
    """Route canonical requests across registered providers."""

    def __init__(
        self,
        registry: ProviderRegistry,
        *,
        cache: MarketDataCache[
            tuple[object, ...],
            object,
        ]
        | None = None,
        quote_ttl_seconds: float = 5.0,
        historical_ttl_seconds: float = 300.0,
    ) -> None:
        if quote_ttl_seconds <= 0:
            raise ValueError(
                "quote_ttl_seconds must be greater than zero"
            )

        if historical_ttl_seconds <= 0:
            raise ValueError(
                "historical_ttl_seconds must be greater than zero"
            )

        self._registry = registry
        self._cache = cache
        self._quote_ttl_seconds = (
            float(
                quote_ttl_seconds
            )
        )
        self._historical_ttl_seconds = (
            float(
                historical_ttl_seconds
            )
        )

    def _route(
        self,
        *,
        capability: MarketDataCapability,
        operation: Callable[
            [object],
            ResultT,
        ],
    ) -> tuple[
        ResultT,
        tuple[ProviderAttempt, ...],
    ]:
        providers = (
            self._registry.providers_for(
                capability
            )
        )

        if not providers:
            raise ProviderCapabilityUnavailableError(
                "no enabled provider supports "
                f"{capability.value}"
            )

        attempts = []

        for provider in providers:
            try:
                result = operation(
                    provider
                )

            except Exception as exc:
                attempts.append(
                    ProviderAttempt(
                        provider=(
                            provider.provider_name
                        ),
                        succeeded=False,
                        error_type=(
                            type(exc).__name__
                        ),
                        error_message=str(
                            exc
                        ),
                    )
                )

                continue

            attempts.append(
                ProviderAttempt(
                    provider=(
                        provider.provider_name
                    ),
                    succeeded=True,
                )
            )

            return (
                result,
                tuple(attempts),
            )

        summary = "; ".join(
            (
                f"{attempt.provider}: "
                f"{attempt.error_type}: "
                f"{attempt.error_message}"
            )
            for attempt in attempts
        )

        raise ProviderRoutingError(
            "all eligible providers failed"
            + (
                f": {summary}"
                if summary
                else ""
            )
        )

    def get_quote(
        self,
        symbol: str,
        *,
        use_cache: bool = True,
    ) -> MarketQuote:
        normalized = normalize_symbol(
            symbol
        )

        cache_key = (
            "quote",
            normalized,
        )

        if (
            use_cache
            and self._cache is not None
        ):
            cached = self._cache.get(
                cache_key
            )

            if isinstance(
                cached,
                MarketQuote,
            ):
                return cached

        result, _ = self._route(
            capability=(
                MarketDataCapability.QUOTE
            ),
            operation=lambda provider: (
                provider.get_quote(
                    normalized
                )
            ),
        )

        if not isinstance(
            result,
            MarketQuote,
        ):
            raise ProviderRoutingError(
                "provider returned a non-canonical quote"
            )

        if (
            use_cache
            and self._cache is not None
        ):
            self._cache.set(
                cache_key,
                result,
                ttl_seconds=(
                    self._quote_ttl_seconds
                ),
            )

        return result

    def get_historical_bars(
        self,
        request: HistoricalBarsRequest,
        *,
        use_cache: bool = True,
    ) -> HistoricalBarsResult:
        cache_key = (
            "historical_bars",
            request.symbol,
            request.start.isoformat(),
            request.end.isoformat(),
            request.interval,
            request.adjusted,
            request.limit,
        )

        if (
            use_cache
            and self._cache is not None
        ):
            cached = self._cache.get(
                cache_key
            )

            if isinstance(
                cached,
                HistoricalBarsResult,
            ):
                return cached

        result, _ = self._route(
            capability=(
                MarketDataCapability
                .HISTORICAL_BARS
            ),
            operation=lambda provider: (
                provider.get_historical_bars(
                    request
                )
            ),
        )

        if not isinstance(
            result,
            HistoricalBarsResult,
        ):
            raise ProviderRoutingError(
                "provider returned non-canonical historical bars"
            )

        if (
            use_cache
            and self._cache is not None
        ):
            self._cache.set(
                cache_key,
                result,
                ttl_seconds=(
                    self._historical_ttl_seconds
                ),
            )

        return result


def healthcheck() -> dict[str, object]:
    return {
        "component": "provider_router",
        "healthy": True,
        "network_called": False,
        "providers_registered": False,
    }

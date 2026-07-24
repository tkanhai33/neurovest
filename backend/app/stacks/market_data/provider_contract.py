"""
Canonical market-data provider contract.

Adapters implement this provider-independent contract.

The provider registry and router depend on this protocol.
Portfolio, risk, research, strategy, AI, and API layers depend on
canonical DTOs rather than upstream provider response formats.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from backend.app.stacks.market_data.dto import (
    HistoricalBarsRequest,
    HistoricalBarsResult,
    MarketDataCapability,
    MarketQuote,
    ProviderHealth,
)


@runtime_checkable
class MarketDataProvider(Protocol):
    """
    Required behavior for a NeuroVest market-data provider.

    Implementations may support only a subset of capabilities, but
    must declare those capabilities explicitly.
    """

    @property
    def provider_name(self) -> str:
        """Return the stable provider identifier."""

    @property
    def capabilities(
        self,
    ) -> frozenset[MarketDataCapability]:
        """Return supported canonical capabilities."""

    def supports(
        self,
        capability: MarketDataCapability,
    ) -> bool:
        """Return whether the provider supports a capability."""

    def get_quote(
        self,
        symbol: str,
    ) -> MarketQuote:
        """
        Return a normalized quote.

        Raise a provider-specific exception until Stage 4 introduces
        canonical provider failure translation.
        """

    def get_historical_bars(
        self,
        request: HistoricalBarsRequest,
    ) -> HistoricalBarsResult:
        """
        Return normalized historical bars.

        Raise a provider-specific exception until Stage 4 introduces
        canonical provider failure translation.
        """

    def healthcheck(
        self,
    ) -> ProviderHealth:
        """Return provider health without mutating trading state."""


def verify_provider_shape(
    provider: object,
) -> tuple[
    bool,
    tuple[str, ...],
]:
    """
    Verify the runtime-visible provider surface.

    This does not call external services.
    """

    required_attributes = (
        "provider_name",
        "capabilities",
        "supports",
        "get_quote",
        "get_historical_bars",
        "healthcheck",
    )

    missing = tuple(
        name
        for name in required_attributes
        if not hasattr(
            provider,
            name,
        )
    )

    return (
        not missing,
        missing,
    )

"""
Canonical NeuroVest market-data DTOs.

These DTOs define provider-independent data returned by the
market-data stack.

External providers must normalize their native responses into these
types before data reaches portfolio, risk, strategy, research, AI, or
API consumers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from math import isfinite
from typing import Any, Mapping


class MarketDataCapability(StrEnum):
    QUOTE = "quote"
    HISTORICAL_BARS = "historical_bars"
    MARKET_STATUS = "market_status"


class MarketSessionState(StrEnum):
    PRE_MARKET = "pre_market"
    OPEN = "open"
    AFTER_HOURS = "after_hours"
    CLOSED = "closed"
    UNKNOWN = "unknown"


class MarketDataErrorCode(StrEnum):
    INVALID_REQUEST = "invalid_request"
    SYMBOL_NOT_FOUND = "symbol_not_found"
    CAPABILITY_UNSUPPORTED = "capability_unsupported"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    RATE_LIMITED = "rate_limited"
    UPSTREAM_ERROR = "upstream_error"
    NORMALIZATION_ERROR = "normalization_error"


def normalize_symbol(value: str) -> str:
    normalized = value.strip().upper()

    if not normalized:
        raise ValueError("symbol must not be empty")

    if len(normalized) > 32:
        raise ValueError("symbol must not exceed 32 characters")

    allowed = set(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789.-^="
    )

    if any(
        character not in allowed
        for character in normalized
    ):
        raise ValueError(
            "symbol contains unsupported characters"
        )

    return normalized


def require_aware_datetime(
    value: datetime,
    field_name: str,
) -> datetime:
    if value.tzinfo is None:
        raise ValueError(
            f"{field_name} must be timezone-aware"
        )

    return value.astimezone(UTC)


def require_finite(
    value: float | None,
    field_name: str,
) -> float | None:
    if value is None:
        return None

    numeric = float(value)

    if not isfinite(numeric):
        raise ValueError(
            f"{field_name} must be finite"
        )

    return numeric


def require_non_negative(
    value: float | None,
    field_name: str,
) -> float | None:
    numeric = require_finite(
        value,
        field_name,
    )

    if (
        numeric is not None
        and numeric < 0
    ):
        raise ValueError(
            f"{field_name} must not be negative"
        )

    return numeric


@dataclass(
    frozen=True,
    slots=True,
)
class MarketDataError:
    code: MarketDataErrorCode
    message: str
    provider: str | None = None
    retryable: bool = False
    details: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        message = self.message.strip()

        if not message:
            raise ValueError(
                "error message must not be empty"
            )

        object.__setattr__(
            self,
            "message",
            message,
        )

        if self.provider is not None:
            provider = self.provider.strip()

            object.__setattr__(
                self,
                "provider",
                provider or None,
            )


@dataclass(
    frozen=True,
    slots=True,
)
class MarketQuote:
    symbol: str
    price: float
    currency: str
    observed_at: datetime
    provider: str
    bid: float | None = None
    ask: float | None = None
    previous_close: float | None = None
    volume: float | None = None
    session: MarketSessionState = (
        MarketSessionState.UNKNOWN
    )
    delayed: bool = False
    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        symbol = normalize_symbol(
            self.symbol
        )

        price = require_non_negative(
            self.price,
            "price",
        )

        bid = require_non_negative(
            self.bid,
            "bid",
        )

        ask = require_non_negative(
            self.ask,
            "ask",
        )

        previous_close = require_non_negative(
            self.previous_close,
            "previous_close",
        )

        volume = require_non_negative(
            self.volume,
            "volume",
        )

        currency = self.currency.strip().upper()
        provider = self.provider.strip()

        if not currency:
            raise ValueError(
                "currency must not be empty"
            )

        if not provider:
            raise ValueError(
                "provider must not be empty"
            )

        observed_at = require_aware_datetime(
            self.observed_at,
            "observed_at",
        )

        object.__setattr__(
            self,
            "symbol",
            symbol,
        )
        object.__setattr__(
            self,
            "price",
            price,
        )
        object.__setattr__(
            self,
            "currency",
            currency,
        )
        object.__setattr__(
            self,
            "provider",
            provider,
        )
        object.__setattr__(
            self,
            "observed_at",
            observed_at,
        )
        object.__setattr__(
            self,
            "bid",
            bid,
        )
        object.__setattr__(
            self,
            "ask",
            ask,
        )
        object.__setattr__(
            self,
            "previous_close",
            previous_close,
        )
        object.__setattr__(
            self,
            "volume",
            volume,
        )


@dataclass(
    frozen=True,
    slots=True,
)
class HistoricalBar:
    symbol: str
    timestamp: datetime
    interval: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    provider: str

    def __post_init__(self) -> None:
        symbol = normalize_symbol(
            self.symbol
        )

        timestamp = require_aware_datetime(
            self.timestamp,
            "timestamp",
        )

        interval = self.interval.strip().lower()
        provider = self.provider.strip()

        if not interval:
            raise ValueError(
                "interval must not be empty"
            )

        if not provider:
            raise ValueError(
                "provider must not be empty"
            )

        open_price = require_non_negative(
            self.open,
            "open",
        )
        high_price = require_non_negative(
            self.high,
            "high",
        )
        low_price = require_non_negative(
            self.low,
            "low",
        )
        close_price = require_non_negative(
            self.close,
            "close",
        )
        volume = require_non_negative(
            self.volume,
            "volume",
        )

        assert open_price is not None
        assert high_price is not None
        assert low_price is not None
        assert close_price is not None
        assert volume is not None

        if high_price < low_price:
            raise ValueError(
                "high must be greater than or equal to low"
            )

        if not (
            low_price
            <= open_price
            <= high_price
        ):
            raise ValueError(
                "open must be between low and high"
            )

        if not (
            low_price
            <= close_price
            <= high_price
        ):
            raise ValueError(
                "close must be between low and high"
            )

        object.__setattr__(
            self,
            "symbol",
            symbol,
        )
        object.__setattr__(
            self,
            "timestamp",
            timestamp,
        )
        object.__setattr__(
            self,
            "interval",
            interval,
        )
        object.__setattr__(
            self,
            "provider",
            provider,
        )
        object.__setattr__(
            self,
            "open",
            open_price,
        )
        object.__setattr__(
            self,
            "high",
            high_price,
        )
        object.__setattr__(
            self,
            "low",
            low_price,
        )
        object.__setattr__(
            self,
            "close",
            close_price,
        )
        object.__setattr__(
            self,
            "volume",
            volume,
        )


@dataclass(
    frozen=True,
    slots=True,
)
class HistoricalBarsRequest:
    symbol: str
    start: datetime
    end: datetime
    interval: str = "1d"
    adjusted: bool = True
    limit: int | None = None

    def __post_init__(self) -> None:
        symbol = normalize_symbol(
            self.symbol
        )

        start = require_aware_datetime(
            self.start,
            "start",
        )

        end = require_aware_datetime(
            self.end,
            "end",
        )

        interval = self.interval.strip().lower()

        if not interval:
            raise ValueError(
                "interval must not be empty"
            )

        if start >= end:
            raise ValueError(
                "start must be earlier than end"
            )

        if (
            self.limit is not None
            and self.limit <= 0
        ):
            raise ValueError(
                "limit must be greater than zero"
            )

        object.__setattr__(
            self,
            "symbol",
            symbol,
        )
        object.__setattr__(
            self,
            "start",
            start,
        )
        object.__setattr__(
            self,
            "end",
            end,
        )
        object.__setattr__(
            self,
            "interval",
            interval,
        )


@dataclass(
    frozen=True,
    slots=True,
)
class HistoricalBarsResult:
    request: HistoricalBarsRequest
    provider: str
    bars: tuple[HistoricalBar, ...]
    fetched_at: datetime
    complete: bool = True
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        provider = self.provider.strip()

        if not provider:
            raise ValueError(
                "provider must not be empty"
            )

        fetched_at = require_aware_datetime(
            self.fetched_at,
            "fetched_at",
        )

        bars = tuple(self.bars)

        previous_timestamp: datetime | None = None

        for bar in bars:
            if bar.symbol != self.request.symbol:
                raise ValueError(
                    "all bars must match the requested symbol"
                )

            if bar.provider != provider:
                raise ValueError(
                    "all bars must match the result provider"
                )

            if (
                previous_timestamp is not None
                and bar.timestamp
                < previous_timestamp
            ):
                raise ValueError(
                    "bars must be ordered by timestamp"
                )

            previous_timestamp = (
                bar.timestamp
            )

        object.__setattr__(
            self,
            "provider",
            provider,
        )
        object.__setattr__(
            self,
            "bars",
            bars,
        )
        object.__setattr__(
            self,
            "fetched_at",
            fetched_at,
        )
        object.__setattr__(
            self,
            "warnings",
            tuple(self.warnings),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class ProviderHealth:
    provider: str
    healthy: bool
    checked_at: datetime
    latency_ms: float | None = None
    message: str | None = None
    capabilities: frozenset[
        MarketDataCapability
    ] = frozenset()

    def __post_init__(self) -> None:
        provider = self.provider.strip()

        if not provider:
            raise ValueError(
                "provider must not be empty"
            )

        checked_at = require_aware_datetime(
            self.checked_at,
            "checked_at",
        )

        latency = require_non_negative(
            self.latency_ms,
            "latency_ms",
        )

        message = (
            self.message.strip()
            if self.message
            else None
        )

        object.__setattr__(
            self,
            "provider",
            provider,
        )
        object.__setattr__(
            self,
            "checked_at",
            checked_at,
        )
        object.__setattr__(
            self,
            "latency_ms",
            latency,
        )
        object.__setattr__(
            self,
            "message",
            message,
        )
        object.__setattr__(
            self,
            "capabilities",
            frozenset(
                self.capabilities
            ),
        )

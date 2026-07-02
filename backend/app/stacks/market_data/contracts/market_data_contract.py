from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class MarketDataProvider(StrEnum):
    YFINANCE = "yfinance"
    FINNHUB = "finnhub"


class ExchangeStatus(StrEnum):
    UNKNOWN = "unknown"
    OPEN = "open"
    CLOSED = "closed"


@dataclass(frozen=True)
class SymbolContract:
    symbol: str
    exchange: str
    currency: str


@dataclass(frozen=True)
class QuoteContract:
    symbol: str
    provider: MarketDataProvider
    price: float | None = None
    currency: str | None = None


@dataclass(frozen=True)
class CandleContract:
    symbol: str
    provider: MarketDataProvider
    timestamp: str
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: int | None = None


@dataclass(frozen=True)
class MarketDataSkeletonStatus:
    stack: str = "market_data"
    phase: str = "phase_4_skeleton"
    yfinance_adapter_implemented: bool = False
    finnhub_adapter_implemented: bool = False
    live_provider_calls_enabled: bool = False
    strategy_logic_implemented: bool = False
    risk_logic_implemented: bool = False
    business_logic_implemented: bool = False

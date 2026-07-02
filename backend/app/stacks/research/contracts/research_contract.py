from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ResearchOutputType(StrEnum):
    INDICATOR = "indicator"
    SCREENER = "screener"
    BACKTEST = "backtest"
    NEWS_SUMMARY = "news_summary"
    HISTORICAL_COMPARISON = "historical_comparison"


@dataclass(frozen=True)
class IndicatorRequestContract:
    symbol: str
    indicator_name: str
    period: str | None = None


@dataclass(frozen=True)
class ScreenerRequestContract:
    universe_name: str
    filter_name: str


@dataclass(frozen=True)
class BacktestRequestContract:
    strategy_name: str
    symbol: str
    start_date: str | None = None
    end_date: str | None = None


@dataclass(frozen=True)
class ResearchOutputContract:
    output_type: ResearchOutputType
    symbol: str | None = None
    summary: str | None = None


@dataclass(frozen=True)
class ResearchSkeletonStatus:
    stack: str = "research"
    phase: str = "phase_6_skeleton"
    indicators_implemented: bool = False
    screeners_implemented: bool = False
    backtests_implemented: bool = False
    news_analysis_implemented: bool = False
    market_data_calls_enabled: bool = False
    strategy_logic_implemented: bool = False
    trading_logic_implemented: bool = False
    business_logic_implemented: bool = False

"""Immutable contracts for the first bulk deterministic strategy batch."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping


@dataclass(
    frozen=True,
    slots=True,
)
class BulkIndicatorStrategyContract:
    strategy_name: str
    evaluator_id: str
    family: str
    minimum_bars: int
    parameters: Mapping[str, float | int]
    transition_only: bool
    buy_rule: str
    sell_rule: str
    hold_rule: str
    abstain_rule: str


def _parameters(
    **values: float | int,
) -> Mapping[str, float | int]:
    return MappingProxyType(
        dict(values)
    )


def _contract(
    *,
    strategy_name: str,
    evaluator_id: str,
    family: str,
    minimum_bars: int,
    parameters: Mapping[str, float | int],
    transition_only: bool,
    buy_rule: str,
    sell_rule: str,
    hold_rule: str,
) -> BulkIndicatorStrategyContract:
    return BulkIndicatorStrategyContract(
        strategy_name=strategy_name,
        evaluator_id=evaluator_id,
        family=family,
        minimum_bars=minimum_bars,
        parameters=parameters,
        transition_only=transition_only,
        buy_rule=buy_rule,
        sell_rule=sell_rule,
        hold_rule=hold_rule,
        abstain_rule=(
            "ABSTAIN on insufficient truthful daily OHLCV bars, "
            "non-finite required values, impossible price ranges, "
            "unavailable indicators, or ambiguous simultaneous "
            "directional conditions."
        ),
    )


MACD_CROSSOVER = _contract(
    strategy_name="MACD Crossover",
    evaluator_id="macd_crossover_v1",
    family="macd",
    minimum_bars=35,
    parameters=_parameters(
        fast_ema=12,
        slow_ema=26,
        signal_ema=9,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when previous MACD is at or below its signal and "
        "current MACD is above its signal."
    ),
    sell_rule=(
        "SELL when previous MACD is at or above its signal and "
        "current MACD is below its signal."
    ),
    hold_rule="HOLD when no new MACD-signal transition occurs.",
)

MACD_ZERO_LINE = _contract(
    strategy_name="MACD Zero-Line",
    evaluator_id="macd_zero_line_v1",
    family="macd",
    minimum_bars=27,
    parameters=_parameters(
        fast_ema=12,
        slow_ema=26,
        zero_threshold=0.0,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when previous MACD is at or below zero and current "
        "MACD is above zero."
    ),
    sell_rule=(
        "SELL when previous MACD is at or above zero and current "
        "MACD is below zero."
    ),
    hold_rule="HOLD when no new zero-line transition occurs.",
)

MACD_HISTOGRAM_MOMENTUM = _contract(
    strategy_name="MACD Histogram Momentum",
    evaluator_id="macd_histogram_momentum_v1",
    family="macd",
    minimum_bars=35,
    parameters=_parameters(
        fast_ema=12,
        slow_ema=26,
        signal_ema=9,
        zero_threshold=0.0,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when the previous MACD histogram is at or below zero "
        "and the current histogram is above zero."
    ),
    sell_rule=(
        "SELL when the previous MACD histogram is at or above zero "
        "and the current histogram is below zero."
    ),
    hold_rule="HOLD when no new histogram zero transition occurs.",
)

STOCHASTIC_MOMENTUM = _contract(
    strategy_name="Stochastic Momentum",
    evaluator_id="stochastic_momentum_v1",
    family="stochastic",
    minimum_bars=17,
    parameters=_parameters(
        k_window=14,
        d_window=3,
        center_threshold=50.0,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when percent K crosses above percent D and current "
        "percent K is above 50."
    ),
    sell_rule=(
        "SELL when percent K crosses below percent D and current "
        "percent K is below 50."
    ),
    hold_rule="HOLD when no confirmed directional crossover occurs.",
)

STOCHASTIC_OVERSOLD_REVERSION = _contract(
    strategy_name="Stochastic Oversold Reversion",
    evaluator_id="stochastic_oversold_reversion_v1",
    family="stochastic",
    minimum_bars=17,
    parameters=_parameters(
        k_window=14,
        d_window=3,
        oversold_threshold=20.0,
        normalization_threshold=50.0,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when percent K crosses above percent D after the "
        "previous percent K was at or below 20."
    ),
    sell_rule=(
        "SELL is not emitted because the catalog strategy is "
        "long-only mean reversion."
    ),
    hold_rule=(
        "HOLD when no new oversold bullish crossover occurs, "
        "including after normalization at or above 50."
    ),
)

CCI_MOMENTUM = _contract(
    strategy_name="Commodity Channel Index Momentum",
    evaluator_id="cci_momentum_v1",
    family="cci",
    minimum_bars=22,
    parameters=_parameters(
        window=20,
        scaling_constant=0.015,
        positive_threshold=100.0,
        negative_threshold=-100.0,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when CCI crosses above positive 100."
    ),
    sell_rule=(
        "SELL when CCI crosses below negative 100."
    ),
    hold_rule="HOLD when neither threshold transition occurs.",
)

CCI_MEAN_REVERSION = _contract(
    strategy_name="CCI Mean Reversion",
    evaluator_id="cci_mean_reversion_v1",
    family="cci",
    minimum_bars=22,
    parameters=_parameters(
        window=20,
        scaling_constant=0.015,
        oversold_threshold=-100.0,
        overbought_threshold=100.0,
        normalization_threshold=0.0,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when CCI crosses upward from at or below negative 100."
    ),
    sell_rule=(
        "SELL when CCI crosses downward from at or above positive 100."
    ),
    hold_rule=(
        "HOLD when no new extreme-reversion transition occurs."
    ),
)

RATE_OF_CHANGE_MOMENTUM = _contract(
    strategy_name="Rate of Change Momentum",
    evaluator_id="rate_of_change_momentum_v1",
    family="roc",
    minimum_bars=22,
    parameters=_parameters(
        window=20,
        positive_threshold=5.0,
        negative_threshold=-5.0,
    ),
    transition_only=True,
    buy_rule="BUY when 20-bar ROC crosses above positive 5 percent.",
    sell_rule="SELL when 20-bar ROC crosses below negative 5 percent.",
    hold_rule="HOLD when neither ROC threshold transition occurs.",
)

ROC_ZERO_CROSS = _contract(
    strategy_name="ROC Zero Cross",
    evaluator_id="roc_zero_cross_v1",
    family="roc",
    minimum_bars=22,
    parameters=_parameters(
        window=20,
        zero_threshold=0.0,
    ),
    transition_only=True,
    buy_rule="BUY when 20-bar ROC crosses above zero.",
    sell_rule="SELL when 20-bar ROC crosses below zero.",
    hold_rule="HOLD when no new ROC zero transition occurs.",
)

TIME_SERIES_MOMENTUM = _contract(
    strategy_name="Time-Series Momentum",
    evaluator_id="time_series_momentum_v1",
    family="roc",
    minimum_bars=253,
    parameters=_parameters(
        lookback=252,
        zero_threshold=0.0,
    ),
    transition_only=False,
    buy_rule="BUY when the 252-session return is above zero.",
    sell_rule="SELL when the 252-session return is below zero.",
    hold_rule="HOLD when the return equals zero.",
)

RSI_MOMENTUM = _contract(
    strategy_name="RSI Momentum",
    evaluator_id="rsi_momentum_v1",
    family="rsi",
    minimum_bars=16,
    parameters=_parameters(
        window=14,
        momentum_threshold=50.0,
    ),
    transition_only=True,
    buy_rule="BUY when RSI crosses upward through 50.",
    sell_rule="SELL when RSI crosses downward through 50.",
    hold_rule="HOLD when no new RSI threshold transition occurs.",
)

TRIX_TREND = _contract(
    strategy_name="TRIX Trend",
    evaluator_id="trix_trend_v1",
    family="trix",
    minimum_bars=47,
    parameters=_parameters(
        ema_window=15,
        zero_threshold=0.0,
    ),
    transition_only=True,
    buy_rule="BUY when 15-period TRIX crosses above zero.",
    sell_rule="SELL when 15-period TRIX crosses below zero.",
    hold_rule="HOLD when no new TRIX zero transition occurs.",
)

GOLDEN_CROSS = _contract(
    strategy_name="Golden Cross",
    evaluator_id="golden_cross_v1",
    family="moving_average",
    minimum_bars=202,
    parameters=_parameters(
        fast_sma=50,
        slow_sma=200,
    ),
    transition_only=True,
    buy_rule="BUY when SMA 50 crosses above SMA 200.",
    sell_rule="SELL when SMA 50 crosses below SMA 200.",
    hold_rule="HOLD when no new SMA 50/200 transition occurs.",
)

EMA_CROSSOVER = _contract(
    strategy_name="Exponential Moving Average Crossover",
    evaluator_id="ema_crossover_v1",
    family="moving_average",
    minimum_bars=27,
    parameters=_parameters(
        fast_ema=12,
        slow_ema=26,
    ),
    transition_only=True,
    buy_rule="BUY when EMA 12 crosses above EMA 26.",
    sell_rule="SELL when EMA 12 crosses below EMA 26.",
    hold_rule="HOLD when no new EMA transition occurs.",
)

PRICE_ABOVE_MOVING_AVERAGE = _contract(
    strategy_name="Price Above Moving Average",
    evaluator_id="price_above_moving_average_v1",
    family="moving_average",
    minimum_bars=202,
    parameters=_parameters(
        sma_window=200,
    ),
    transition_only=True,
    buy_rule="BUY when close crosses above SMA 200.",
    sell_rule="SELL when close crosses below SMA 200.",
    hold_rule="HOLD when no new close/SMA transition occurs.",
)


BULK_INDICATOR_STRATEGY_CONTRACTS = MappingProxyType(
    {
        contract.strategy_name: contract
        for contract in (
            MACD_CROSSOVER,
            MACD_ZERO_LINE,
            MACD_HISTOGRAM_MOMENTUM,
            STOCHASTIC_MOMENTUM,
            STOCHASTIC_OVERSOLD_REVERSION,
            CCI_MOMENTUM,
            CCI_MEAN_REVERSION,
            RATE_OF_CHANGE_MOMENTUM,
            ROC_ZERO_CROSS,
            TIME_SERIES_MOMENTUM,
            RSI_MOMENTUM,
            TRIX_TREND,
            GOLDEN_CROSS,
            EMA_CROSSOVER,
            PRICE_ABOVE_MOVING_AVERAGE,
        )
    }
)


def get_bulk_indicator_strategy_contract(
    strategy_name: str,
) -> BulkIndicatorStrategyContract:
    normalized = str(
        strategy_name
    ).strip()

    contract = BULK_INDICATOR_STRATEGY_CONTRACTS.get(
        normalized
    )

    if contract is None:
        raise KeyError(
            "No deterministic bulk strategy contract: "
            f"{normalized or '<empty>'}"
        )

    return contract


def healthcheck() -> dict[str, object]:
    return {
        "component": "bulk_15_parameter_contracts_v1",
        "healthy": True,
        "contract_count": len(
            BULK_INDICATOR_STRATEGY_CONTRACTS
        ),
        "strategy_names": tuple(
            BULK_INDICATOR_STRATEGY_CONTRACTS
        ),
        "immutable": True,
        "truthful_daily_ohlcv_only": True,
        "evaluator_implementations_present": False,
        "registry_activated": False,
        "owner_integration_present": False,
        "execution_enabled": False,
    }

"""Immutable contracts for the second bulk daily-OHLCV batch."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping


Number = int | float


@dataclass(
    frozen=True,
    slots=True,
)
class BulkIndicatorStrategyContractV2:
    strategy_name: str
    evaluator_id: str
    family: str
    minimum_bars: int
    parameters: Mapping[str, Number]
    transition_only: bool
    stateful_position_required: bool
    buy_rule: str
    sell_rule: str
    hold_rule: str
    abstain_rule: str


def _parameters(
    **values: Number,
) -> Mapping[str, Number]:
    return MappingProxyType(
        dict(values)
    )


def _contract(
    *,
    strategy_name: str,
    evaluator_id: str,
    family: str,
    minimum_bars: int,
    parameters: Mapping[str, Number],
    transition_only: bool,
    buy_rule: str,
    sell_rule: str,
    hold_rule: str,
) -> BulkIndicatorStrategyContractV2:
    return BulkIndicatorStrategyContractV2(
        strategy_name=strategy_name,
        evaluator_id=evaluator_id,
        family=family,
        minimum_bars=minimum_bars,
        parameters=parameters,
        transition_only=transition_only,
        stateful_position_required=False,
        buy_rule=buy_rule,
        sell_rule=sell_rule,
        hold_rule=hold_rule,
        abstain_rule=(
            "ABSTAIN on insufficient truthful daily OHLCV bars, "
            "non-finite required values, impossible OHLC ranges, "
            "unavailable indicators, zero denominators, or "
            "simultaneous directional conditions."
        ),
    )


STOCHASTIC_PULLBACK_IN_TREND = _contract(
    strategy_name="Stochastic Pullback in Trend",
    evaluator_id="stochastic_pullback_in_trend_v1",
    family="stochastic_trend",
    minimum_bars=202,
    parameters=_parameters(
        k_window=14,
        d_window=3,
        trend_sma=200,
        oversold_threshold=20.0,
        overbought_threshold=80.0,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when close is above SMA 200 and percent K crosses "
        "above percent D after previous percent K was at or below 20."
    ),
    sell_rule=(
        "SELL when close is below SMA 200 and percent K crosses "
        "below percent D after previous percent K was at or above 80."
    ),
    hold_rule=(
        "HOLD when trend and stochastic pullback conditions do not "
        "produce a new aligned crossover."
    ),
)

HIGH_LOW_MOMENTUM = _contract(
    strategy_name="High-Low Momentum",
    evaluator_id="high_low_momentum_v1",
    family="range_momentum",
    minimum_bars=21,
    parameters=_parameters(
        window=20,
        bullish_threshold=0.8,
        bearish_threshold=0.2,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when the 20-bar range-position score crosses above 0.8."
    ),
    sell_rule=(
        "SELL when the 20-bar range-position score crosses below 0.2."
    ),
    hold_rule="HOLD when neither range-position transition occurs.",
)

PRICE_ACCELERATION = _contract(
    strategy_name="Price Acceleration",
    evaluator_id="price_acceleration_v1",
    family="price_momentum",
    minimum_bars=26,
    parameters=_parameters(
        velocity_window=20,
        acceleration_lag=5,
        zero_threshold=0.0,
    ),
    transition_only=False,
    buy_rule=(
        "BUY when 20-bar price velocity and its 5-bar acceleration "
        "are both positive."
    ),
    sell_rule=(
        "SELL when 20-bar price velocity and its 5-bar acceleration "
        "are both negative."
    ),
    hold_rule=(
        "HOLD when velocity and acceleration are zero or disagree."
    ),
)

ADX_BREAKOUT = _contract(
    strategy_name="ADX Breakout",
    evaluator_id="adx_breakout_v1",
    family="adx_dmi",
    minimum_bars=35,
    parameters=_parameters(
        adx_window=14,
        adx_threshold=25.0,
        breakout_window=20,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when close breaks above the prior 20-bar high while "
        "ADX is at or above 25 and positive DI exceeds negative DI."
    ),
    sell_rule=(
        "SELL when close breaks below the prior 20-bar low while "
        "ADX is at or above 25 and negative DI exceeds positive DI."
    ),
    hold_rule="HOLD when breakout strength or direction is unconfirmed.",
)

ADX_TREND_FOLLOWING = _contract(
    strategy_name="ADX Trend Following",
    evaluator_id="adx_trend_following_v1",
    family="adx_dmi",
    minimum_bars=29,
    parameters=_parameters(
        window=14,
        adx_threshold=25.0,
    ),
    transition_only=False,
    buy_rule=(
        "BUY when ADX is at or above 25 and positive DI exceeds "
        "negative DI."
    ),
    sell_rule=(
        "SELL when ADX is at or above 25 and negative DI exceeds "
        "positive DI."
    ),
    hold_rule="HOLD when ADX is weak or DI direction is tied.",
)

DMI_CROSSOVER = _contract(
    strategy_name="DMI Crossover",
    evaluator_id="dmi_crossover_v1",
    family="adx_dmi",
    minimum_bars=16,
    parameters=_parameters(
        window=14,
        require_adx_filter=0,
        adx_threshold=25.0,
    ),
    transition_only=True,
    buy_rule="BUY when positive DI crosses above negative DI.",
    sell_rule="SELL when negative DI crosses above positive DI.",
    hold_rule="HOLD when no new directional-index crossover occurs.",
)

HULL_MOVING_AVERAGE_TREND = _contract(
    strategy_name="Hull Moving Average Trend",
    evaluator_id="hull_moving_average_trend_v1",
    family="moving_average",
    minimum_bars=57,
    parameters=_parameters(
        window=55,
        slope_lag=1,
    ),
    transition_only=False,
    buy_rule="BUY when the 55-period Hull moving average slope is positive.",
    sell_rule="SELL when the 55-period Hull moving average slope is negative.",
    hold_rule="HOLD when the Hull moving average slope is zero.",
)

MOVING_AVERAGE_RIBBON = _contract(
    strategy_name="Moving Average Ribbon",
    evaluator_id="moving_average_ribbon_v1",
    family="moving_average",
    minimum_bars=202,
    parameters=_parameters(
        ma_1=10,
        ma_2=20,
        ma_3=50,
        ma_4=100,
        ma_5=200,
    ),
    transition_only=False,
    buy_rule=(
        "BUY when SMA 10 is above SMA 20, 50, 100, and 200 in "
        "strict descending period order."
    ),
    sell_rule=(
        "SELL when SMA 10 is below SMA 20, 50, 100, and 200 in "
        "strict ascending period order."
    ),
    hold_rule="HOLD when the ribbon is mixed or contains equal values.",
)

ENVELOPE_MEAN_REVERSION = _contract(
    strategy_name="Envelope Mean Reversion",
    evaluator_id="envelope_mean_reversion_v1",
    family="moving_average_reversion",
    minimum_bars=21,
    parameters=_parameters(
        sma_window=20,
        envelope_fraction=0.02,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when close crosses below the lower two-percent SMA envelope."
    ),
    sell_rule=(
        "SELL when close crosses above the upper two-percent SMA envelope."
    ),
    hold_rule="HOLD when close remains inside the envelope.",
)

MOVING_AVERAGE_DEVIATION_REVERSION = _contract(
    strategy_name="Moving Average Deviation Reversion",
    evaluator_id="moving_average_deviation_reversion_v1",
    family="moving_average_reversion",
    minimum_bars=21,
    parameters=_parameters(
        sma_window=20,
        oversold_deviation=-0.05,
        overbought_deviation=0.05,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when close-to-SMA deviation crosses below negative five percent."
    ),
    sell_rule=(
        "SELL when close-to-SMA deviation crosses above positive five percent."
    ),
    hold_rule="HOLD when deviation remains between the adopted thresholds.",
)

MOVING_AVERAGE_CROSSOVER_WITH_ATR_FILTER = _contract(
    strategy_name="Moving Average Crossover with ATR Filter",
    evaluator_id="moving_average_crossover_with_atr_filter_v1",
    family="moving_average_atr",
    minimum_bars=52,
    parameters=_parameters(
        fast_sma=20,
        slow_sma=50,
        atr_window=14,
        separation_atr_ratio=0.5,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when SMA 20 crosses above SMA 50 and their separation "
        "is greater than one-half ATR."
    ),
    sell_rule=(
        "SELL when SMA 20 crosses below SMA 50 and their separation "
        "is greater than one-half ATR."
    ),
    hold_rule="HOLD when no filtered moving-average crossover occurs.",
)

MOVING_AVERAGE_SLOPE = _contract(
    strategy_name="Moving Average Slope",
    evaluator_id="moving_average_slope_v1",
    family="moving_average",
    minimum_bars=56,
    parameters=_parameters(
        sma_window=50,
        slope_lag=5,
        zero_threshold=0.0,
    ),
    transition_only=False,
    buy_rule="BUY when the five-session slope of SMA 50 is positive.",
    sell_rule="SELL when the five-session slope of SMA 50 is negative.",
    hold_rule="HOLD when the adopted SMA slope equals zero.",
)

TRIPLE_MOVING_AVERAGE_TREND = _contract(
    strategy_name="Triple Moving Average Trend",
    evaluator_id="triple_moving_average_trend_v1",
    family="moving_average",
    minimum_bars=202,
    parameters=_parameters(
        short_sma=20,
        medium_sma=50,
        long_sma=200,
    ),
    transition_only=False,
    buy_rule="BUY when SMA 20 is above SMA 50 and SMA 50 is above SMA 200.",
    sell_rule="SELL when SMA 20 is below SMA 50 and SMA 50 is below SMA 200.",
    hold_rule="HOLD when the three moving averages are not strictly aligned.",
)

ATR_COMPRESSION_EXPANSION = _contract(
    strategy_name="ATR Compression Expansion",
    evaluator_id="atr_compression_expansion_v1",
    family="atr_volatility",
    minimum_bars=121,
    parameters=_parameters(
        atr_window=14,
        percentile_window=100,
        compression_percentile=20.0,
        breakout_window=20,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when prior ATR percentile was at or below 20, current "
        "ATR expands, and close breaks above the prior 20-bar high."
    ),
    sell_rule=(
        "SELL when prior ATR percentile was at or below 20, current "
        "ATR expands, and close breaks below the prior 20-bar low."
    ),
    hold_rule="HOLD when compression, expansion, and breakout do not align.",
)

MONEY_FLOW_INDEX_REVERSION = _contract(
    strategy_name="Money Flow Index Reversion",
    evaluator_id="money_flow_index_reversion_v1",
    family="volume_ohlcv",
    minimum_bars=16,
    parameters=_parameters(
        window=14,
        oversold_threshold=20.0,
        overbought_threshold=80.0,
    ),
    transition_only=True,
    buy_rule="BUY when 14-period MFI crosses upward through 20.",
    sell_rule="SELL when 14-period MFI crosses downward through 80.",
    hold_rule="HOLD when no new MFI extreme-reversion transition occurs.",
)


BULK_INDICATOR_STRATEGY_CONTRACTS_V2 = MappingProxyType(
    {
        contract.strategy_name: contract
        for contract in (
            STOCHASTIC_PULLBACK_IN_TREND,
            HIGH_LOW_MOMENTUM,
            PRICE_ACCELERATION,
            ADX_BREAKOUT,
            ADX_TREND_FOLLOWING,
            DMI_CROSSOVER,
            HULL_MOVING_AVERAGE_TREND,
            MOVING_AVERAGE_RIBBON,
            ENVELOPE_MEAN_REVERSION,
            MOVING_AVERAGE_DEVIATION_REVERSION,
            MOVING_AVERAGE_CROSSOVER_WITH_ATR_FILTER,
            MOVING_AVERAGE_SLOPE,
            TRIPLE_MOVING_AVERAGE_TREND,
            ATR_COMPRESSION_EXPANSION,
            MONEY_FLOW_INDEX_REVERSION,
        )
    }
)


def get_bulk_indicator_strategy_contract_v2(
    strategy_name: str,
) -> BulkIndicatorStrategyContractV2:
    normalized = str(
        strategy_name
    ).strip()

    contract = BULK_INDICATOR_STRATEGY_CONTRACTS_V2.get(
        normalized
    )

    if contract is None:
        raise KeyError(
            "No deterministic second-batch strategy contract: "
            f"{normalized or '<empty>'}"
        )

    return contract


def healthcheck() -> dict[str, object]:
    return {
        "component": "bulk_15_parameter_contracts_v2",
        "healthy": True,
        "contract_count": len(
            BULK_INDICATOR_STRATEGY_CONTRACTS_V2
        ),
        "strategy_names": tuple(
            BULK_INDICATOR_STRATEGY_CONTRACTS_V2
        ),
        "immutable": True,
        "truthful_daily_ohlcv_only": True,
        "stateful_position_required": False,
        "position_sizing_enabled": False,
        "evaluator_implementations_present": False,
        "registry_activated": False,
        "owner_integration_present": False,
        "execution_enabled": False,
    }

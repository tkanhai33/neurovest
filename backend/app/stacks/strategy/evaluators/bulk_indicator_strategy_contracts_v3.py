"""Immutable contracts for the third pure daily-OHLCV batch."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping


Number = int | float


@dataclass(
    frozen=True,
    slots=True,
)
class BulkIndicatorStrategyContractV3:
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
) -> BulkIndicatorStrategyContractV3:
    return BulkIndicatorStrategyContractV3(
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


PARABOLIC_SAR_TREND = _contract(
    strategy_name="Parabolic SAR Trend",
    evaluator_id="parabolic_sar_trend_v1",
    family="trend",
    minimum_bars=3,
    parameters=_parameters(
        acceleration_step=0.02,
        acceleration_maximum=0.20,
    ),
    transition_only=True,
    buy_rule="BUY when close crosses above Parabolic SAR.",
    sell_rule="SELL when close crosses below Parabolic SAR.",
    hold_rule="HOLD when no new close-to-SAR transition occurs.",
)

AROON_TREND = _contract(
    strategy_name="Aroon Trend",
    evaluator_id="aroon_trend_v1",
    family="trend",
    minimum_bars=26,
    parameters=_parameters(
        window=25,
        trend_threshold=70.0,
        opposite_threshold=30.0,
    ),
    transition_only=False,
    buy_rule=(
        "BUY when Aroon Up is at least 70 and Aroon Down is at most 30."
    ),
    sell_rule=(
        "SELL when Aroon Down is at least 70 and Aroon Up is at most 30."
    ),
    hold_rule="HOLD when neither directional Aroon state is dominant.",
)

ICHIMOKU_TREND = _contract(
    strategy_name="Ichimoku Trend",
    evaluator_id="ichimoku_trend_v1",
    family="trend",
    minimum_bars=78,
    parameters=_parameters(
        conversion_window=9,
        base_window=26,
        span_b_window=52,
        displacement=26,
    ),
    transition_only=False,
    buy_rule=(
        "BUY when close is above the displaced cloud and the conversion "
        "line is above the base line."
    ),
    sell_rule=(
        "SELL when close is below the displaced cloud and the conversion "
        "line is below the base line."
    ),
    hold_rule="HOLD when price or line direction is mixed.",
)

SUPERTREND = _contract(
    strategy_name="Supertrend",
    evaluator_id="supertrend_v1",
    family="atr_trend",
    minimum_bars=16,
    parameters=_parameters(
        atr_window=14,
        multiplier=3.0,
    ),
    transition_only=True,
    buy_rule="BUY when close crosses above the active Supertrend band.",
    sell_rule="SELL when close crosses below the active Supertrend band.",
    hold_rule="HOLD when no Supertrend direction change occurs.",
)

N_DAY_HIGH_BREAKOUT = _contract(
    strategy_name="N-Day High Breakout",
    evaluator_id="n_day_high_breakout_v1",
    family="breakout",
    minimum_bars=21,
    parameters=_parameters(
        window=20,
    ),
    transition_only=True,
    buy_rule="BUY when close breaks above the prior 20-bar high.",
    sell_rule="SELL when close breaks below the prior 20-bar low.",
    hold_rule="HOLD when close remains within the prior 20-bar range.",
)

N_DAY_LOW_BREAKDOWN = _contract(
    strategy_name="N-Day Low Breakdown",
    evaluator_id="n_day_low_breakdown_v1",
    family="failed_breakdown_reversal",
    minimum_bars=22,
    parameters=_parameters(
        window=20,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when the previous close was below the low of its preceding "
        "20 bars and the current close reclaims that broken boundary."
    ),
    sell_rule=(
        "SELL when the current close breaks below the low of the prior "
        "20 bars."
    ),
    hold_rule=(
        "HOLD when no new 20-bar downside break or failed-breakdown "
        "reclaim occurs."
    ),
)

NR4_BREAKOUT = _contract(
    strategy_name="NR4 Breakout",
    evaluator_id="nr4_breakout_v1",
    family="range_compression",
    minimum_bars=5,
    parameters=_parameters(
        compression_window=4,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when the previous bar is the narrowest range of four and "
        "current close breaks above its high."
    ),
    sell_rule=(
        "SELL when the previous bar is the narrowest range of four and "
        "current close breaks below its low."
    ),
    hold_rule="HOLD when compression or breakout confirmation is absent.",
)

NR7_BREAKOUT = _contract(
    strategy_name="NR7 Breakout",
    evaluator_id="nr7_breakout_v1",
    family="range_compression",
    minimum_bars=8,
    parameters=_parameters(
        compression_window=7,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when the previous bar is the narrowest range of seven and "
        "current close breaks above its high."
    ),
    sell_rule=(
        "SELL when the previous bar is the narrowest range of seven and "
        "current close breaks below its low."
    ),
    hold_rule="HOLD when compression or breakout confirmation is absent.",
)

INSIDE_BAR_BREAKOUT = _contract(
    strategy_name="Inside Bar Breakout",
    evaluator_id="inside_bar_breakout_v1",
    family="price_action",
    minimum_bars=3,
    parameters=_parameters(
        mother_bar_lookback=1,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when the prior bar is inside its predecessor and current "
        "close breaks above the mother-bar high."
    ),
    sell_rule=(
        "SELL when the prior bar is inside its predecessor and current "
        "close breaks below the mother-bar low."
    ),
    hold_rule="HOLD when no confirmed inside-bar breakout occurs.",
)

TRIANGLE_BREAKOUT = _contract(
    strategy_name="Triangle Breakout",
    evaluator_id="triangle_breakout_v1",
    family="price_pattern",
    minimum_bars=22,
    parameters=_parameters(
        structure_window=20,
        minimum_touches=2,
        volume_window=20,
        volume_multiplier=1.2,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when converging 20-bar resistance and support are present, "
        "close breaks resistance, and volume exceeds 1.2 times average."
    ),
    sell_rule=(
        "SELL when converging 20-bar resistance and support are present, "
        "close breaks support, and volume exceeds 1.2 times average."
    ),
    hold_rule="HOLD when convergence, breakout, or volume is unconfirmed.",
)

Z_SCORE_MEAN_REVERSION = _contract(
    strategy_name="Z-Score Mean Reversion",
    evaluator_id="z_score_mean_reversion_v1",
    family="statistical_reversion",
    minimum_bars=21,
    parameters=_parameters(
        window=20,
        entry_z=2.0,
    ),
    transition_only=True,
    buy_rule="BUY when close z-score crosses below negative 2.",
    sell_rule="SELL when close z-score crosses above positive 2.",
    hold_rule="HOLD when no new adopted z-score extreme is crossed.",
)

WILLIAMS_R_REVERSION = _contract(
    strategy_name="Williams %R Reversion",
    evaluator_id="williams_r_reversion_v1",
    family="oscillator_reversion",
    minimum_bars=16,
    parameters=_parameters(
        window=14,
        oversold_threshold=-80.0,
        overbought_threshold=-20.0,
    ),
    transition_only=True,
    buy_rule="BUY when Williams percent R crosses upward through -80.",
    sell_rule="SELL when Williams percent R crosses downward through -20.",
    hold_rule="HOLD when no new Williams percent R reversion occurs.",
)

GAP_FADE = _contract(
    strategy_name="Gap Fade",
    evaluator_id="gap_fade_v1",
    family="daily_gap",
    minimum_bars=2,
    parameters=_parameters(
        minimum_gap_fraction=0.02,
    ),
    transition_only=False,
    buy_rule=(
        "BUY when current open gaps at least two percent below the prior "
        "close and current close confirms an upward fade."
    ),
    sell_rule=(
        "SELL when current open gaps at least two percent above the prior "
        "close and current close confirms a downward fade."
    ),
    hold_rule="HOLD when no qualifying confirmed daily gap fade exists.",
)

OVERNIGHT_REVERSAL = _contract(
    strategy_name="Overnight Reversal",
    evaluator_id="overnight_reversal_v1",
    family="daily_gap",
    minimum_bars=2,
    parameters=_parameters(
        minimum_overnight_return=0.01,
    ),
    transition_only=False,
    buy_rule=(
        "BUY when the overnight return is at most negative one percent "
        "and the regular-session close finishes above the open."
    ),
    sell_rule=(
        "SELL when the overnight return is at least positive one percent "
        "and the regular-session close finishes below the open."
    ),
    hold_rule="HOLD when overnight and regular-session directions do not reverse.",
)

SHORT_TERM_REVERSAL_FACTOR = _contract(
    strategy_name="Short-Term Reversal Factor",
    evaluator_id="short_term_reversal_factor_v1",
    family="return_reversion",
    minimum_bars=6,
    parameters=_parameters(
        return_window=5,
        reversal_threshold=0.05,
    ),
    transition_only=False,
    buy_rule="BUY when the trailing five-session return is at most -5 percent.",
    sell_rule="SELL when the trailing five-session return is at least 5 percent.",
    hold_rule="HOLD when the trailing return remains inside the thresholds.",
)


BULK_INDICATOR_STRATEGY_CONTRACTS_V3 = MappingProxyType(
    {
        contract.strategy_name: contract
        for contract in (
            PARABOLIC_SAR_TREND,
            AROON_TREND,
            ICHIMOKU_TREND,
            SUPERTREND,
            N_DAY_HIGH_BREAKOUT,
            N_DAY_LOW_BREAKDOWN,
            NR4_BREAKOUT,
            NR7_BREAKOUT,
            INSIDE_BAR_BREAKOUT,
            TRIANGLE_BREAKOUT,
            Z_SCORE_MEAN_REVERSION,
            WILLIAMS_R_REVERSION,
            GAP_FADE,
            OVERNIGHT_REVERSAL,
            SHORT_TERM_REVERSAL_FACTOR,
        )
    }
)


def get_bulk_indicator_strategy_contract_v3(
    strategy_name: str,
) -> BulkIndicatorStrategyContractV3:
    normalized = str(
        strategy_name
    ).strip()

    contract = BULK_INDICATOR_STRATEGY_CONTRACTS_V3.get(
        normalized
    )

    if contract is None:
        raise KeyError(
            "No deterministic third-batch strategy contract: "
            f"{normalized or '<empty>'}"
        )

    return contract


def healthcheck() -> dict[str, object]:
    return {
        "component": "bulk_15_parameter_contracts_v3",
        "healthy": True,
        "contract_count": len(
            BULK_INDICATOR_STRATEGY_CONTRACTS_V3
        ),
        "strategy_names": tuple(
            BULK_INDICATOR_STRATEGY_CONTRACTS_V3
        ),
        "immutable": True,
        "truthful_daily_ohlcv_only": True,
        "single_symbol_only": True,
        "stateful_position_required": False,
        "event_data_required": False,
        "universe_data_required": False,
        "evaluator_implementations_present": False,
        "registry_activated": False,
        "owner_integration_present": False,
        "execution_enabled": False,
    }

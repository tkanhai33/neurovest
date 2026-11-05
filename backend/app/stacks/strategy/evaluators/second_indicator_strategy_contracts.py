"""Immutable contracts for the second deterministic indicator family."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal


Decision = Literal[
    "BUY",
    "SELL",
    "HOLD",
    "ABSTAIN",
]


@dataclass(
    frozen=True,
    slots=True,
)
class SecondIndicatorStrategyContract:
    strategy_name: str
    evaluator_id: str
    indicator_family: str
    minimum_bars: int
    transition_only: bool
    buy_rule: str
    sell_rule: str
    hold_rule: str
    abstain_rule: str
    channel_window: int | None = None
    ema_window: int | None = None
    atr_window: int | None = None
    atr_multiplier: float | None = None
    reference_rule: str | None = None
    dual_trigger_rule: str | None = None


DONCHIAN_WINDOW = 20
DONCHIAN_MINIMUM_BARS = DONCHIAN_WINDOW + 2

ATR_WINDOW = 14
ATR_BREAKOUT_MULTIPLIER = 2.0
ATR_BREAKOUT_MINIMUM_BARS = ATR_WINDOW + 2

KELTNER_EMA_WINDOW = 20
KELTNER_ATR_WINDOW = 14
KELTNER_MULTIPLIER = 2.0
KELTNER_MINIMUM_BARS = max(
    KELTNER_EMA_WINDOW + 1,
    KELTNER_ATR_WINDOW + 2,
)

PREVIOUS_CLOSE_ATR_WINDOW = 14
PREVIOUS_CLOSE_ATR_MULTIPLIER = 1.0
PREVIOUS_CLOSE_MINIMUM_BARS = (
    PREVIOUS_CLOSE_ATR_WINDOW + 1
)


DONCHIAN_CHANNEL_BREAKOUT = (
    SecondIndicatorStrategyContract(
        strategy_name=
            "Donchian Channel Breakout",

        evaluator_id=
            "donchian_channel_breakout_v1",

        indicator_family=
            "donchian_channels",

        minimum_bars=
            DONCHIAN_MINIMUM_BARS,

        channel_window=
            DONCHIAN_WINDOW,

        transition_only=
            True,

        reference_rule=(
            "For every evaluated close, the upper and lower "
            "channels use only the preceding 20 completed bars "
            "and exclude the evaluated bar."
        ),

        buy_rule=(
            "BUY only when the previous close was at or below "
            "its prior 20-bar upper channel and the current close "
            "is above its prior 20-bar upper channel."
        ),

        sell_rule=(
            "SELL only when the previous close was at or above "
            "its prior 20-bar lower channel and the current close "
            "is below its prior 20-bar lower channel."
        ),

        hold_rule=(
            "HOLD when no new upper-channel or lower-channel "
            "close transition occurs."
        ),

        abstain_rule=(
            "ABSTAIN when fewer than 22 truthful bars are "
            "available, required OHLC values are invalid, or "
            "both directional transitions are simultaneously true."
        ),

        dual_trigger_rule=(
            "ABSTAIN if both BUY and SELL transition conditions "
            "are simultaneously true."
        ),
    )
)


ATR_VOLATILITY_BREAKOUT = (
    SecondIndicatorStrategyContract(
        strategy_name=
            "ATR Volatility Breakout",

        evaluator_id=
            "atr_volatility_breakout_v1",

        indicator_family=
            "average_true_range",

        minimum_bars=
            ATR_BREAKOUT_MINIMUM_BARS,

        atr_window=
            ATR_WINDOW,

        atr_multiplier=
            ATR_BREAKOUT_MULTIPLIER,

        transition_only=
            True,

        reference_rule=(
            "The reference for each bar is its immediately "
            "preceding truthful close. Wilder-smoothed ATR uses "
            "a 14-bar window."
        ),

        buy_rule=(
            "BUY only when the previous close was at or below "
            "its previous-close reference plus 2.0 times its ATR "
            "and the current close is above the immediately "
            "preceding close plus 2.0 times current ATR."
        ),

        sell_rule=(
            "SELL only when the previous close was at or above "
            "its previous-close reference minus 2.0 times its ATR "
            "and the current close is below the immediately "
            "preceding close minus 2.0 times current ATR."
        ),

        hold_rule=(
            "HOLD when the current close produces no new "
            "volatility-scaled directional transition."
        ),

        abstain_rule=(
            "ABSTAIN when fewer than 16 truthful bars are "
            "available, required OHLC values are invalid, ATR "
            "is unavailable, or both transitions are true."
        ),

        dual_trigger_rule=(
            "ABSTAIN if both BUY and SELL transition conditions "
            "are simultaneously true."
        ),
    )
)


KELTNER_CHANNEL_BREAKOUT = (
    SecondIndicatorStrategyContract(
        strategy_name=
            "Keltner Channel Breakout",

        evaluator_id=
            "keltner_channel_breakout_v1",

        indicator_family=
            "keltner_channels",

        minimum_bars=
            KELTNER_MINIMUM_BARS,

        ema_window=
            KELTNER_EMA_WINDOW,

        atr_window=
            KELTNER_ATR_WINDOW,

        atr_multiplier=
            KELTNER_MULTIPLIER,

        transition_only=
            True,

        reference_rule=(
            "Middle is the 20-bar EMA using an SMA seed. Upper "
            "and lower bands equal the current middle plus or "
            "minus 2.0 times 14-bar Wilder ATR."
        ),

        buy_rule=(
            "BUY only when the previous close was at or below "
            "its previous upper Keltner band and the current close "
            "is above its current upper Keltner band."
        ),

        sell_rule=(
            "SELL only when the previous close was at or above "
            "its previous lower Keltner band and the current close "
            "is below its current lower Keltner band."
        ),

        hold_rule=(
            "HOLD when no new upper-band or lower-band close "
            "transition occurs."
        ),

        abstain_rule=(
            "ABSTAIN when fewer than 21 truthful bars are "
            "available, required OHLC values are invalid, a "
            "required indicator is unavailable, or both "
            "transitions are true."
        ),

        dual_trigger_rule=(
            "ABSTAIN if both BUY and SELL transition conditions "
            "are simultaneously true."
        ),
    )
)


VOLATILITY_BREAKOUT_FROM_PREVIOUS_CLOSE = (
    SecondIndicatorStrategyContract(
        strategy_name=
            "Volatility Breakout from Previous Close",

        evaluator_id=
            "volatility_breakout_previous_close_v1",

        indicator_family=
            "average_true_range",

        minimum_bars=
            PREVIOUS_CLOSE_MINIMUM_BARS,

        atr_window=
            PREVIOUS_CLOSE_ATR_WINDOW,

        atr_multiplier=
            PREVIOUS_CLOSE_ATR_MULTIPLIER,

        transition_only=
            False,

        reference_rule=(
            "Long and short triggers use the immediately preceding "
            "truthful close plus or minus 1.0 times current 14-bar "
            "Wilder ATR. Current truthful high and low determine "
            "whether a trigger was reached."
        ),

        buy_rule=(
            "BUY when current high reaches or exceeds the long "
            "trigger and current low remains strictly above the "
            "short trigger."
        ),

        sell_rule=(
            "SELL when current low reaches or falls below the short "
            "trigger and current high remains strictly below the "
            "long trigger."
        ),

        hold_rule=(
            "HOLD when neither the long trigger nor short trigger "
            "is reached."
        ),

        abstain_rule=(
            "ABSTAIN when fewer than 15 truthful bars are "
            "available, required OHLC values are invalid, ATR is "
            "unavailable, or both triggers are reached in one bar."
        ),

        dual_trigger_rule=(
            "ABSTAIN when both triggers are reached because daily "
            "OHLC cannot reveal which trigger occurred first."
        ),
    )
)


SECOND_INDICATOR_STRATEGY_CONTRACTS = (
    MappingProxyType(
        {
            contract.strategy_name:
                contract
            for contract in (
                DONCHIAN_CHANNEL_BREAKOUT,
                ATR_VOLATILITY_BREAKOUT,
                KELTNER_CHANNEL_BREAKOUT,
                VOLATILITY_BREAKOUT_FROM_PREVIOUS_CLOSE,
            )
        }
    )
)


def get_second_indicator_strategy_contract(
    strategy_name: str,
) -> SecondIndicatorStrategyContract:
    normalized_name = str(
        strategy_name
    ).strip()

    contract = (
        SECOND_INDICATOR_STRATEGY_CONTRACTS.get(
            normalized_name
        )
    )

    if contract is None:
        raise KeyError(
            "No deterministic second-family contract: "
            f"{normalized_name or '<empty>'}"
        )

    return contract


def healthcheck() -> dict[str, object]:
    return {
        "component":
            "second_indicator_family_parameter_contracts_v1",

        "healthy":
            True,

        "contract_count":
            len(
                SECOND_INDICATOR_STRATEGY_CONTRACTS
            ),

        "strategy_names":
            tuple(
                SECOND_INDICATOR_STRATEGY_CONTRACTS
            ),

        "immutable":
            True,

        "truthful_daily_ohlc_only":
            True,

        "dual_trigger_fails_closed":
            True,

        "evaluator_implementations_present":
            False,

        "registry_activated":
            False,

        "owner_integration_present":
            False,

        "execution_enabled":
            False,
    }

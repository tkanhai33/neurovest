"""Immutable contracts for deterministic Bollinger and RSI evaluators."""

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
class IndicatorStrategyContract:
    strategy_name: str
    evaluator_id: str
    indicator_family: str
    minimum_bars: int
    window: int
    transition_only: bool
    buy_rule: str
    sell_rule: str
    hold_rule: str
    abstain_rule: str
    multiplier: float | None = None
    overbought_threshold: float | None = None
    oversold_threshold: float | None = None
    neutral_threshold: float | None = None


BOLLINGER_WINDOW = 20
BOLLINGER_MULTIPLIER = 2.0
BOLLINGER_MINIMUM_BARS = (
    BOLLINGER_WINDOW + 1
)

RSI_WINDOW = 14
RSI_OVERBOUGHT = 70.0
RSI_OVERSOLD = 30.0
RSI_NEUTRAL = 50.0
RSI_MINIMUM_BARS = (
    RSI_WINDOW + 2
)


BOLLINGER_BREAKOUT = (
    IndicatorStrategyContract(
        strategy_name=
            "Bollinger Band Breakout",

        evaluator_id=
            "bollinger_band_breakout_v1",

        indicator_family=
            "bollinger_bands",

        minimum_bars=
            BOLLINGER_MINIMUM_BARS,

        window=
            BOLLINGER_WINDOW,

        multiplier=
            BOLLINGER_MULTIPLIER,

        transition_only=
            True,

        buy_rule=(
            "BUY only when the previous close is at or below "
            "its previous upper band and the current close is "
            "above its current upper band."
        ),

        sell_rule=(
            "SELL only when the previous close is at or above "
            "its previous lower band and the current close is "
            "below its current lower band."
        ),

        hold_rule=(
            "HOLD when no new upper-band or lower-band "
            "transition occurs."
        ),

        abstain_rule=(
            "ABSTAIN when fewer than 21 truthful bars are "
            "available or any required value is invalid."
        ),
    )
)


BOLLINGER_MEAN_REVERSION = (
    IndicatorStrategyContract(
        strategy_name=
            "Bollinger Band Mean Reversion",

        evaluator_id=
            "bollinger_band_mean_reversion_v1",

        indicator_family=
            "bollinger_bands",

        minimum_bars=
            BOLLINGER_MINIMUM_BARS,

        window=
            BOLLINGER_WINDOW,

        multiplier=
            BOLLINGER_MULTIPLIER,

        transition_only=
            True,

        buy_rule=(
            "BUY only when the previous close is at or above "
            "its previous lower band and the current close is "
            "below its current lower band."
        ),

        sell_rule=(
            "SELL only when the previous close is at or below "
            "its previous upper band and the current close is "
            "above its current upper band."
        ),

        hold_rule=(
            "HOLD while price remains within a band, remains "
            "outside without a new transition, or returns "
            "toward the neutral middle band."
        ),

        abstain_rule=(
            "ABSTAIN when fewer than 21 truthful bars are "
            "available or any required value is invalid."
        ),
    )
)


RSI_OVERBOUGHT_MEAN_REVERSION = (
    IndicatorStrategyContract(
        strategy_name=
            "RSI Overbought Mean Reversion",

        evaluator_id=
            "rsi_overbought_mean_reversion_v1",

        indicator_family=
            "relative_strength_index",

        minimum_bars=
            RSI_MINIMUM_BARS,

        window=
            RSI_WINDOW,

        overbought_threshold=
            RSI_OVERBOUGHT,

        neutral_threshold=
            RSI_NEUTRAL,

        transition_only=
            True,

        buy_rule=(
            "No BUY entry is produced by this short-side "
            "overbought evaluator."
        ),

        sell_rule=(
            "SELL only when previous RSI is at or below 70 "
            "and current RSI rises above 70."
        ),

        hold_rule=(
            "HOLD when RSI remains above 70 without a new "
            "transition or returns toward the neutral level 50."
        ),

        abstain_rule=(
            "ABSTAIN when fewer than 16 truthful closes are "
            "available or any required value is invalid."
        ),
    )
)


RSI_OVERSOLD_MEAN_REVERSION = (
    IndicatorStrategyContract(
        strategy_name=
            "RSI Oversold Mean Reversion",

        evaluator_id=
            "rsi_oversold_mean_reversion_v1",

        indicator_family=
            "relative_strength_index",

        minimum_bars=
            RSI_MINIMUM_BARS,

        window=
            RSI_WINDOW,

        oversold_threshold=
            RSI_OVERSOLD,

        neutral_threshold=
            RSI_NEUTRAL,

        transition_only=
            True,

        buy_rule=(
            "BUY only when previous RSI is at or above 30 "
            "and current RSI falls below 30."
        ),

        sell_rule=(
            "No SELL entry is produced by this long-side "
            "oversold evaluator."
        ),

        hold_rule=(
            "HOLD when RSI remains below 30 without a new "
            "transition or returns toward the neutral level 50."
        ),

        abstain_rule=(
            "ABSTAIN when fewer than 16 truthful closes are "
            "available or any required value is invalid."
        ),
    )
)


INDICATOR_STRATEGY_CONTRACTS = (
    MappingProxyType(
        {
            contract.strategy_name:
                contract
            for contract in (
                BOLLINGER_BREAKOUT,
                BOLLINGER_MEAN_REVERSION,
                RSI_OVERBOUGHT_MEAN_REVERSION,
                RSI_OVERSOLD_MEAN_REVERSION,
            )
        }
    )
)


def get_indicator_strategy_contract(
    strategy_name: str,
) -> IndicatorStrategyContract:
    normalized_name = str(
        strategy_name
    ).strip()

    contract = (
        INDICATOR_STRATEGY_CONTRACTS.get(
            normalized_name
        )
    )

    if contract is None:
        raise KeyError(
            "No deterministic indicator strategy contract: "
            f"{normalized_name or '<empty>'}"
        )

    return contract


def healthcheck() -> dict[str, object]:
    return {
        "component":
            "indicator_strategy_parameter_contracts_v1",

        "healthy":
            True,

        "contract_count":
            len(
                INDICATOR_STRATEGY_CONTRACTS
            ),

        "strategy_names":
            tuple(
                INDICATOR_STRATEGY_CONTRACTS
            ),

        "immutable":
            True,

        "transition_only":
            True,

        "evaluator_implementations_present":
            False,

        "registry_activated":
            False,

        "execution_enabled":
            False,
    }

from types import MappingProxyType

import pytest

from backend.app.stacks.strategy.evaluators.bulk_indicator_strategy_contracts_v4 import (
    BULK_INDICATOR_STRATEGY_CONTRACTS_V4,
    BULK_INDICATOR_STRATEGY_CONTRACTS_V4_BY_NAME,
    KAMA_TREND,
)


EXPECTED_NAMES = (
    "On-Balance Volume Trend",
    "Volume Breakout",
    "Chaikin Money Flow",
    "Accumulation Distribution Line",
    "Bollinger Bandwidth Expansion",
    "Channel Trend Following",
    "Regression Trend",
    "Regression Channel Breakout",
    "Momentum with Volatility Filter",
    "Breakout with Volume Confirmation",
    "Breakout Retest",
    "Support Resistance Reversion",
    "Median Reversion",
    "MAD Z-Score Reversion",
    "KAMA Trend",
)


def test_exact_fifteen_names_and_order():
    assert tuple(
        contract.strategy_name
        for contract in BULK_INDICATOR_STRATEGY_CONTRACTS_V4
    ) == EXPECTED_NAMES


def test_contract_mapping_is_exact_and_immutable():
    assert isinstance(
        BULK_INDICATOR_STRATEGY_CONTRACTS_V4_BY_NAME,
        MappingProxyType,
    )

    assert tuple(
        BULK_INDICATOR_STRATEGY_CONTRACTS_V4_BY_NAME
    ) == EXPECTED_NAMES

    with pytest.raises(TypeError):
        BULK_INDICATOR_STRATEGY_CONTRACTS_V4_BY_NAME[
            "Unknown Strategy"
        ] = object()


@pytest.mark.parametrize(
    "contract",
    BULK_INDICATOR_STRATEGY_CONTRACTS_V4,
)
def test_contracts_are_deterministic_and_read_only(
    contract,
):
    assert contract.minimum_bars >= 2
    assert contract.transition_only is True
    assert contract.stateful_position_required is False
    assert contract.buy_rule
    assert contract.sell_rule
    assert contract.hold_rule
    assert dict(contract.parameters)


def test_kama_contract_is_exact():
    assert KAMA_TREND.minimum_bars == 31
    assert KAMA_TREND.family == "adaptive_trend"

    assert dict(KAMA_TREND.parameters) == {
        "efficiency_window": 10,
        "fast_period": 2,
        "slow_period": 30,
    }

    assert "10-bar efficiency ratio" in KAMA_TREND.buy_rule
    assert "10-bar SMA seed" in KAMA_TREND.buy_rule
    assert "crosses" in KAMA_TREND.sell_rule


def test_preflight_repairs_are_explicit():
    contracts = BULK_INDICATOR_STRATEGY_CONTRACTS_V4_BY_NAME

    volume = contracts["Volume Breakout"]

    assert volume.family == "volume_surge"
    assert dict(volume.parameters) == {
        "volume_window": 20,
        "volume_multiplier": 1.5,
    }

    assert "respective prior 20-bar mean" in volume.buy_rule
    assert "prior 20-bar high" not in volume.buy_rule
    assert "prior 20-bar low" not in volume.sell_rule

    confirmed = contracts[
        "Breakout with Volume Confirmation"
    ]

    assert "prior 20-bar high" in confirmed.buy_rule
    assert "prior 20-bar low" in confirmed.sell_rule

    assert (
        "when high equals low"
        in contracts["Chaikin Money Flow"].hold_rule
    )

    assert (
        "when high equals low"
        in contracts[
            "Accumulation Distribution Line"
        ].hold_rule
    )

    bandwidth = contracts[
        "Bollinger Bandwidth Expansion"
    ]

    assert "nearest-rank" in bandwidth.buy_rule
    assert "middle band is zero" in bandwidth.hold_rule

    assert (
        "mean close is zero"
        in contracts["Regression Trend"].hold_rule
    )

    assert (
        "residual deviation is zero"
        in contracts[
            "Regression Channel Breakout"
        ].hold_rule
    )

    assert (
        "close is zero"
        in contracts[
            "Momentum with Volatility Filter"
        ].hold_rule
    )

    retest = contracts["Breakout Retest"]

    assert "most recent breakout" in retest.buy_rule
    assert "absolute" in retest.buy_rule
    assert "absolute" in retest.sell_rule
    assert "boundary is zero" in retest.hold_rule

    support = contracts[
        "Support Resistance Reversion"
    ]

    assert "absolute" in support.buy_rule
    assert "absolute" in support.sell_rule
    assert "boundary is zero" in support.hold_rule

    kama = contracts["KAMA Trend"]

    assert (
        "sum of absolute price changes is zero"
        in kama.hold_rule
    )

    assert "efficiency ratio is zero" in kama.hold_rule

from __future__ import annotations

from copy import deepcopy
from math import isclose

import pytest

from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v4 import (
    BULK_OFFLINE_EVALUATORS_V4,
    _adl,
    _kama,
    _mad_z,
    _money_flow_multiplier,
    _nearest_rank,
    _obv,
    _ratio_distance,
    _regression_channel,
    evaluate_bulk_indicator_strategy_v4,
)


def make_bars(
    closes,
    *,
    volumes=None,
    opens=None,
    highs=None,
    lows=None,
):
    count = len(closes)

    if volumes is None:
        volumes = [1000.0] * count

    if opens is None:
        opens = [value for value in closes]

    if highs is None:
        highs = [
            max(open_value, close) + 1.0
            for open_value, close in zip(
                opens,
                closes,
                strict=True,
            )
        ]

    if lows is None:
        lows = [
            min(open_value, close) - 1.0
            for open_value, close in zip(
                opens,
                closes,
                strict=True,
            )
        ]

    return [
        {
            "open": float(open_value),
            "high": float(high),
            "low": float(low),
            "close": float(close),
            "volume": float(volume),
        }
        for open_value, high, low, close, volume in zip(
            opens,
            highs,
            lows,
            closes,
            volumes,
            strict=True,
        )
    ]


def stable_bars(count=140):
    closes = [
        100.0 + index * 0.05
        for index in range(count)
    ]
    return make_bars(closes)


def decision(name, bars):
    return evaluate_bulk_indicator_strategy_v4(
        name,
        bars,
    )["decision"]


def test_money_flow_multiplier_formula_and_zero_range():
    assert _money_flow_multiplier(
        12.0,
        8.0,
        11.0,
    ) == pytest.approx(0.5)

    assert _money_flow_multiplier(
        10.0,
        10.0,
        10.0,
    ) == 0.0


def test_obv_formula_handles_up_down_and_flat():
    assert _obv(
        [10.0, 11.0, 10.0, 10.0],
        [100.0, 200.0, 300.0, 400.0],
    ) == [
        0.0,
        200.0,
        -100.0,
        -100.0,
    ]


def test_adl_formula_accumulates_money_flow_volume():
    output = _adl(
        [12.0, 12.0],
        [8.0, 8.0],
        [11.0, 9.0],
        [100.0, 100.0],
    )

    assert output == pytest.approx(
        [50.0, 0.0]
    )


def test_nearest_rank_is_one_based_and_non_interpolated():
    assert _nearest_rank(
        [50.0, 10.0, 40.0, 20.0, 30.0],
        0.20,
    ) == 10.0

    assert _nearest_rank(
        list(range(1, 101)),
        0.20,
    ) == 20


def test_relative_distance_uses_absolute_nonzero_boundary():
    assert _ratio_distance(
        99.5,
        100.0,
    ) == pytest.approx(0.005)

    assert _ratio_distance(
        -99.5,
        -100.0,
    ) == pytest.approx(0.005)

    assert _ratio_distance(
        1.0,
        0.0,
    ) is None


def test_mad_z_uses_scaled_median_absolute_deviation():
    values = [
        1.0,
        2.0,
        3.0,
        4.0,
        10.0,
    ]

    expected = (
        10.0 - 3.0
    ) / (
        1.4826 * 1.0
    )

    assert _mad_z(
        values,
        1.4826,
    ) == pytest.approx(expected)

    assert _mad_z(
        [5.0] * 20,
        1.4826,
    ) is None


def test_regression_channel_zero_residual_is_zero_width():
    endpoint, deviation = _regression_channel(
        [1.0, 2.0, 3.0, 4.0]
    )

    assert endpoint == pytest.approx(4.0)
    assert deviation == pytest.approx(0.0)


def test_kama_flat_window_uses_zero_efficiency_ratio():
    output = _kama(
        [100.0] * 31,
        10,
        2,
        30,
    )

    assert output[-1] == pytest.approx(100.0)


@pytest.mark.parametrize(
    "strategy_name",
    tuple(BULK_OFFLINE_EVALUATORS_V4),
)
def test_all_evaluators_are_deterministic_and_do_not_mutate_bars(
    strategy_name,
):
    supplied = stable_bars()
    original = deepcopy(supplied)

    first = evaluate_bulk_indicator_strategy_v4(
        strategy_name,
        supplied,
    )

    second = evaluate_bulk_indicator_strategy_v4(
        strategy_name,
        supplied,
    )

    assert first == second
    assert supplied == original


@pytest.mark.parametrize(
    ("last_close", "expected"),
    (
        (101.0, "BUY"),
        (99.0, "SELL"),
        (100.0, "HOLD"),
    ),
)
def test_volume_breakout_directional_transition(
    last_close,
    expected,
):
    closes = [100.0] * 21 + [last_close]
    volumes = [1000.0] * 21 + [2000.0]

    assert decision(
        "Volume Breakout",
        make_bars(
            closes,
            volumes=volumes,
        ),
    ) == expected


@pytest.mark.parametrize(
    ("last_close", "expected"),
    (
        (103.0, "BUY"),
        (97.0, "SELL"),
        (100.0, "HOLD"),
    ),
)
def test_channel_trend_following_directional_transition(
    last_close,
    expected,
):
    closes = [100.0] * 21 + [last_close]
    highs = [102.0] * 21 + [last_close + 0.5]
    lows = [98.0] * 21 + [last_close - 0.5]

    assert decision(
        "Channel Trend Following",
        make_bars(
            closes,
            highs=highs,
            lows=lows,
        ),
    ) == expected


@pytest.mark.parametrize(
    ("last_close", "expected"),
    (
        (103.0, "BUY"),
        (97.0, "SELL"),
        (100.0, "HOLD"),
    ),
)
def test_volume_confirmed_breakout_direction(
    last_close,
    expected,
):
    closes = [100.0] * 21 + [last_close]
    highs = [102.0] * 21 + [last_close + 0.5]
    lows = [98.0] * 21 + [last_close - 0.5]
    volumes = [1000.0] * 21 + [2000.0]

    assert decision(
        "Breakout with Volume Confirmation",
        make_bars(
            closes,
            highs=highs,
            lows=lows,
            volumes=volumes,
        ),
    ) == expected


def test_volume_confirmation_blocks_price_only_breakout():
    closes = [100.0] * 21 + [103.0]
    highs = [102.0] * 21 + [103.5]
    lows = [98.0] * 21 + [102.5]
    volumes = [1000.0] * 22

    assert decision(
        "Breakout with Volume Confirmation",
        make_bars(
            closes,
            highs=highs,
            lows=lows,
            volumes=volumes,
        ),
    ) == "HOLD"


def test_support_rejection_produces_buy():
    closes = [105.0] * 20 + [100.5, 101.0]
    opens = [105.0] * 20 + [100.5, 100.0]
    highs = [110.0] * 22
    lows = [100.0] * 21 + [99.8]

    assert decision(
        "Support Resistance Reversion",
        make_bars(
            closes,
            opens=opens,
            highs=highs,
            lows=lows,
        ),
    ) == "BUY"


def test_resistance_rejection_produces_sell():
    closes = [105.0] * 20 + [109.5, 109.0]
    opens = [105.0] * 20 + [109.5, 110.0]
    highs = [110.0] * 21 + [110.2]
    lows = [100.0] * 22

    assert decision(
        "Support Resistance Reversion",
        make_bars(
            closes,
            opens=opens,
            highs=highs,
            lows=lows,
        ),
    ) == "SELL"


def test_median_reversion_crosses_lower_boundary():
    closes = [100.0] * 20 + [100.0, 90.0]

    assert decision(
        "Median Reversion",
        make_bars(closes),
    ) == "BUY"


def test_median_reversion_crosses_upper_boundary():
    closes = [100.0] * 20 + [100.0, 110.0]

    assert decision(
        "Median Reversion",
        make_bars(closes),
    ) == "SELL"


@pytest.mark.parametrize(
    "strategy_name",
    (
        "Bollinger Bandwidth Expansion",
        "Regression Trend",
        "Momentum with Volatility Filter",
        "Breakout Retest",
        "Support Resistance Reversion",
        "MAD Z-Score Reversion",
        "KAMA Trend",
    ),
)
def test_zero_valued_price_boundaries_fail_closed_or_hold(
    strategy_name,
):
    supplied = make_bars(
        [0.0] * 140,
        opens=[0.0] * 140,
        highs=[0.0] * 140,
        lows=[0.0] * 140,
    )

    output = evaluate_bulk_indicator_strategy_v4(
        strategy_name,
        supplied,
    )

    assert output["decision"] in {
        "HOLD",
        "ABSTAIN",
    }
    assert output["confidence"] == 0.0

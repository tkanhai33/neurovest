from __future__ import annotations

from copy import deepcopy

import pytest

import backend.app.stacks.strategy.evaluators.bulk_indicator_family_v4 as family
from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v4 import (
    evaluate_bulk_indicator_strategy_v4,
)


REMAINING_STRATEGIES = (
    "On-Balance Volume Trend",
    "Chaikin Money Flow",
    "Accumulation Distribution Line",
    "Bollinger Bandwidth Expansion",
    "Regression Trend",
    "Regression Channel Breakout",
    "Momentum with Volatility Filter",
    "Breakout Retest",
    "MAD Z-Score Reversion",
    "KAMA Trend",
)

PREVIOUSLY_QUALIFIED_STRATEGIES = (
    "Volume Breakout",
    "Channel Trend Following",
    "Breakout with Volume Confirmation",
    "Support Resistance Reversion",
    "Median Reversion",
)

ALL_FIFTEEN_STRATEGIES = (
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
        opens = list(closes)

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
    return make_bars(
        [100.0] * count,
    )


def evaluate(name, supplied):
    return evaluate_bulk_indicator_strategy_v4(
        name,
        supplied,
    )


def assert_decision(
    name,
    supplied,
    expected,
):
    original = deepcopy(supplied)

    first = evaluate(
        name,
        supplied,
    )

    second = evaluate(
        name,
        supplied,
    )

    assert first == second
    assert supplied == original
    assert first["strategy_name"] == name
    assert first["decision"] == expected
    assert first["signal"] == expected
    assert first["status"] == "ok"
    assert 0.0 <= first["confidence"] <= 1.0
    assert first["reason"]

    if expected == "HOLD":
        assert first["confidence"] == 0.0
    else:
        assert first["confidence"] > 0.0


def synthetic_change_series(
    *,
    previous,
    current,
    count=140,
    lookback=20,
):
    values = [0.0] * count

    previous_reference = count - lookback - 2
    current_reference = count - lookback - 1

    values[previous_reference] = 0.0
    values[current_reference] = 0.0
    values[-2] = float(previous)
    values[-1] = float(current)

    return values


@pytest.mark.parametrize(
    ("previous", "current", "expected"),
    (
        (0.0, 10.0, "BUY"),
        (0.0, -10.0, "SELL"),
        (0.0, 0.0, "HOLD"),
    ),
)
def test_on_balance_volume_exact_transitions(
    monkeypatch,
    previous,
    current,
    expected,
):
    monkeypatch.setattr(
        family,
        "_obv",
        lambda closes, volumes: synthetic_change_series(
            previous=previous,
            current=current,
        ),
    )

    assert_decision(
        "On-Balance Volume Trend",
        stable_bars(),
        expected,
    )


@pytest.mark.parametrize(
    ("previous", "current", "expected"),
    (
        (0.05, 0.10, "BUY"),
        (-0.05, -0.10, "SELL"),
        (0.00, 0.00, "HOLD"),
    ),
)
def test_chaikin_money_flow_exact_transitions(
    monkeypatch,
    previous,
    current,
    expected,
):
    def fake_cmf(
        highs,
        lows,
        closes,
        volumes,
        end,
        window,
    ):
        if end == len(closes) - 2:
            return previous

        if end == len(closes) - 1:
            return current

        raise AssertionError(
            f"Unexpected CMF endpoint: {end}"
        )

    monkeypatch.setattr(
        family,
        "_cmf",
        fake_cmf,
    )

    assert_decision(
        "Chaikin Money Flow",
        stable_bars(),
        expected,
    )


@pytest.mark.parametrize(
    ("previous", "current", "expected"),
    (
        (0.0, 10.0, "BUY"),
        (0.0, -10.0, "SELL"),
        (0.0, 0.0, "HOLD"),
    ),
)
def test_accumulation_distribution_exact_transitions(
    monkeypatch,
    previous,
    current,
    expected,
):
    monkeypatch.setattr(
        family,
        "_adl",
        lambda highs, lows, closes, volumes:
            synthetic_change_series(
                previous=previous,
                current=current,
            ),
    )

    assert_decision(
        "Accumulation Distribution Line",
        stable_bars(),
        expected,
    )


@pytest.mark.parametrize(
    ("current_close", "expected"),
    (
        (160.0, "BUY"),
        (40.0, "SELL"),
        (100.0, "HOLD"),
    ),
)
def test_bollinger_bandwidth_expansion_exact_transitions(
    monkeypatch,
    current_close,
    expected,
):
    supplied = stable_bars()
    supplied[-1] = {
        "open": current_close,
        "high": current_close + 1.0,
        "low": current_close - 1.0,
        "close": current_close,
        "volume": 1000.0,
    }

    def fake_bandwidth(
        values,
        end,
        window,
        deviations,
    ):
        if end == len(values) - 2:
            return 0.10, 150.0, 50.0

        if end == len(values) - 1:
            return 0.30, 150.0, 50.0

        return 0.20, 150.0, 50.0

    monkeypatch.setattr(
        family,
        "_bandwidth",
        fake_bandwidth,
    )

    assert_decision(
        "Bollinger Bandwidth Expansion",
        supplied,
        expected,
    )


@pytest.mark.parametrize(
    ("previous_slope", "current_slope", "expected"),
    (
        (0.0, 0.20, "BUY"),
        (0.0, -0.20, "SELL"),
        (0.0, 0.0, "HOLD"),
    ),
)
def test_regression_trend_exact_transitions(
    monkeypatch,
    previous_slope,
    current_slope,
    expected,
):
    calls = iter(
        (
            (previous_slope, 100.0),
            (current_slope, 100.0),
        )
    )

    monkeypatch.setattr(
        family,
        "_linear_regression",
        lambda values: next(calls),
    )

    output = evaluate(
        "Regression Trend",
        stable_bars(),
    )

    assert output["decision"] == expected
    assert output["signal"] == expected
    assert output["status"] == "ok"

    if expected == "HOLD":
        assert output["confidence"] == 0.0
    else:
        assert output["confidence"] > 0.0


@pytest.mark.parametrize(
    ("previous_close", "current_close", "expected"),
    (
        (100.0, 103.0, "BUY"),
        (100.0, 97.0, "SELL"),
        (100.0, 100.0, "HOLD"),
    ),
)
def test_regression_channel_breakout_exact_transitions(
    monkeypatch,
    previous_close,
    current_close,
    expected,
):
    closes = [100.0] * 138 + [
        previous_close,
        current_close,
    ]

    monkeypatch.setattr(
        family,
        "_regression_channel",
        lambda values: (100.0, 1.0),
    )

    assert_decision(
        "Regression Channel Breakout",
        make_bars(closes),
        expected,
    )


@pytest.mark.parametrize(
    ("current_close", "expected"),
    (
        (101.0, "BUY"),
        (99.0, "SELL"),
        (100.0, "HOLD"),
    ),
)
def test_momentum_volatility_filter_exact_transitions(
    monkeypatch,
    current_close,
    expected,
):
    closes = [100.0] * 140
    closes[-1] = current_close

    monkeypatch.setattr(
        family,
        "_rolling_atr",
        lambda closes, highs, lows, window:
            [None] * (len(closes) - 1) + [1.0],
    )

    assert_decision(
        "Momentum with Volatility Filter",
        make_bars(closes),
        expected,
    )


def breakout_retest_bars(
    direction,
):
    closes = [100.0] * 27
    opens = [100.0] * 27
    highs = [101.0] * 27
    lows = [99.0] * 27

    if direction == "up":
        closes[-2] = 103.0
        opens[-2] = 102.0
        highs[-2] = 104.0
        lows[-2] = 100.0

        closes[-1] = 102.0
        opens[-1] = 101.5
        highs[-1] = 103.0
        lows[-1] = 100.8

    elif direction == "down":
        closes[-2] = 97.0
        opens[-2] = 98.0
        highs[-2] = 100.0
        lows[-2] = 96.0

        closes[-1] = 98.0
        opens[-1] = 98.5
        highs[-1] = 99.2
        lows[-1] = 97.0

    elif direction != "none":
        raise AssertionError(
            f"Unknown fixture direction: {direction}"
        )

    return make_bars(
        closes,
        opens=opens,
        highs=highs,
        lows=lows,
    )


@pytest.mark.parametrize(
    ("fixture_direction", "expected"),
    (
        ("up", "BUY"),
        ("down", "SELL"),
        ("none", "HOLD"),
    ),
)
def test_breakout_retest_exact_transitions(
    fixture_direction,
    expected,
):
    assert_decision(
        "Breakout Retest",
        breakout_retest_bars(
            fixture_direction,
        ),
        expected,
    )


@pytest.mark.parametrize(
    ("previous", "current", "expected"),
    (
        (-2.5, -3.0, "BUY"),
        (2.5, 3.0, "SELL"),
        (0.0, 0.0, "HOLD"),
    ),
)
def test_mad_z_score_reversion_exact_transitions(
    monkeypatch,
    previous,
    current,
    expected,
):
    calls = iter(
        (
            previous,
            current,
        )
    )

    monkeypatch.setattr(
        family,
        "_mad_z",
        lambda values, scale: next(calls),
    )

    output = evaluate(
        "MAD Z-Score Reversion",
        stable_bars(),
    )

    assert output["decision"] == expected
    assert output["signal"] == expected
    assert output["status"] == "ok"

    if expected == "HOLD":
        assert output["confidence"] == 0.0
    else:
        assert output["confidence"] > 0.0


@pytest.mark.parametrize(
    (
        "previous_close",
        "current_close",
        "previous_kama",
        "current_kama",
        "expected",
    ),
    (
        (100.0, 102.0, 101.0, 101.0, "BUY"),
        (102.0, 100.0, 101.0, 101.0, "SELL"),
        (100.0, 100.0, 101.0, 101.0, "HOLD"),
    ),
)
def test_kama_trend_exact_transitions(
    monkeypatch,
    previous_close,
    current_close,
    previous_kama,
    current_kama,
    expected,
):
    closes = [100.0] * 138 + [
        previous_close,
        current_close,
    ]

    def fake_kama(
        values,
        efficiency_window,
        fast_period,
        slow_period,
    ):
        output = [None] * len(values)
        output[-2] = previous_kama
        output[-1] = current_kama
        return output

    monkeypatch.setattr(
        family,
        "_kama",
        fake_kama,
    )

    assert_decision(
        "KAMA Trend",
        make_bars(closes),
        expected,
    )


def test_transition_inventory_is_exactly_fifteen():
    assert len(REMAINING_STRATEGIES) == 10
    assert len(PREVIOUSLY_QUALIFIED_STRATEGIES) == 5

    assert set(
        REMAINING_STRATEGIES
    ).isdisjoint(
        PREVIOUSLY_QUALIFIED_STRATEGIES
    )

    assert set(
        REMAINING_STRATEGIES
    ) | set(
        PREVIOUSLY_QUALIFIED_STRATEGIES
    ) == set(
        ALL_FIFTEEN_STRATEGIES
    )

    assert tuple(
        family.BULK_OFFLINE_EVALUATORS_V4
    ) == ALL_FIFTEEN_STRATEGIES

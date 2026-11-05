import math

import pytest

from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v3 import (
    BULK_OFFLINE_EVALUATORS_V3,
    evaluate_bulk_indicator_strategy_v3,
    healthcheck,
)
from backend.app.stacks.strategy.evaluators.bulk_indicator_strategy_contracts_v3 import (
    BULK_INDICATOR_STRATEGY_CONTRACTS_V3,
)
from backend.app.stacks.strategy.evaluators.registry import (
    ALLOWLISTED_EVALUATORS,
)


NAMES = tuple(
    BULK_INDICATOR_STRATEGY_CONTRACTS_V3
)


def bars(
    count=300,
    *,
    mode="wave",
):
    output = []

    for index in range(count):
        if mode == "up":
            close = 100.0 + index * 1.0
        elif mode == "down":
            close = 500.0 - index * 1.0
        elif mode == "flat":
            close = 100.0
        else:
            close = (
                100.0
                + index * 0.04
                + 6.0
                * math.sin(index / 4.0)
            )

        output.append(
            {
                "symbol": "AAPL",
                "open": close,
                "high": close + 2.0,
                "low": close - 2.0,
                "close": close,
                "volume": 1000.0 + index,
                "provider": "fixture",
            }
        )

    return output


def assert_schema(result, name):
    assert result["strategy_name"] == name
    assert result["status"] in (
        "ok",
        "abstain",
    )
    assert result["decision"] in (
        "BUY",
        "SELL",
        "HOLD",
        "ABSTAIN",
    )
    assert result["signal"] == result["decision"]
    assert 0.0 <= result["confidence"] <= 1.0

    if result["decision"] in (
        "HOLD",
        "ABSTAIN",
    ):
        assert result["confidence"] == 0.0


def test_exact_fifteen_offline_evaluators():
    assert tuple(
        BULK_OFFLINE_EVALUATORS_V3
    ) == NAMES

    assert len(
        BULK_OFFLINE_EVALUATORS_V3
    ) == 15


@pytest.mark.parametrize(
    "name",
    NAMES,
)
def test_each_evaluator_abstains_on_short_history(
    name,
):
    result = (
        BULK_OFFLINE_EVALUATORS_V3[name](
            []
        )
    )

    assert result["status"] == "abstain"
    assert result["decision"] == "ABSTAIN"
    assert result["reason"] == "insufficient_history"


@pytest.mark.parametrize(
    "name",
    NAMES,
)
def test_each_evaluator_is_deterministic(
    name,
):
    supplied = bars()

    first = (
        BULK_OFFLINE_EVALUATORS_V3[name](
            supplied
        )
    )

    second = (
        BULK_OFFLINE_EVALUATORS_V3[name](
            supplied
        )
    )

    assert first == second


@pytest.mark.parametrize(
    "name",
    NAMES,
)
def test_each_evaluator_returns_bounded_schema(
    name,
):
    result = (
        BULK_OFFLINE_EVALUATORS_V3[name](
            bars()
        )
    )

    assert_schema(result, name)


@pytest.mark.parametrize(
    "name",
    NAMES,
)
def test_invalid_truthful_bar_fails_closed(
    name,
):
    supplied = bars()

    supplied[-1]["high"] = (
        supplied[-1]["low"] - 1.0
    )

    result = (
        BULK_OFFLINE_EVALUATORS_V3[name](
            supplied
        )
    )

    assert result["status"] == "abstain"
    assert result["decision"] == "ABSTAIN"
    assert result["reason"] == (
        "invalid_truthful_daily_ohlcv"
    )


@pytest.mark.parametrize(
    "name",
    NAMES,
)
def test_nonfinite_bar_fails_closed(
    name,
):
    supplied = bars()

    supplied[-1]["close"] = float("nan")

    result = (
        BULK_OFFLINE_EVALUATORS_V3[name](
            supplied
        )
    )

    assert result["decision"] == "ABSTAIN"


@pytest.mark.parametrize(
    "name",
    NAMES,
)
def test_flat_history_never_emits_directional_vote(
    name,
):
    result = (
        BULK_OFFLINE_EVALUATORS_V3[name](
            bars(
                mode="flat"
            )
        )
    )

    assert result["decision"] in (
        "HOLD",
        "ABSTAIN",
    )


def test_aroon_bullish_and_bearish_states():
    bullish = evaluate_bulk_indicator_strategy_v3(
        "Aroon Trend",
        bars(
            40,
            mode="up",
        ),
    )

    bearish = evaluate_bulk_indicator_strategy_v3(
        "Aroon Trend",
        bars(
            40,
            mode="down",
        ),
    )

    assert bullish["decision"] == "BUY"
    assert bearish["decision"] == "SELL"


def test_ichimoku_bullish_and_bearish_states():
    bullish = evaluate_bulk_indicator_strategy_v3(
        "Ichimoku Trend",
        bars(
            100,
            mode="up",
        ),
    )

    bearish = evaluate_bulk_indicator_strategy_v3(
        "Ichimoku Trend",
        bars(
            100,
            mode="down",
        ),
    )

    assert bullish["decision"] == "BUY"
    assert bearish["decision"] == "SELL"


@pytest.mark.parametrize(
    ("open_value", "close_value", "expected"),
    [
        (97.0, 99.0, "BUY"),
        (103.0, 101.0, "SELL"),
    ],
)
def test_gap_fade_directional_states(
    open_value,
    close_value,
    expected,
):
    supplied = [
        {
            "open": 100.0,
            "high": 101.0,
            "low": 99.0,
            "close": 100.0,
            "volume": 1000.0,
        },
        {
            "open": open_value,
            "high": max(
                open_value,
                close_value,
            ) + 1.0,
            "low": min(
                open_value,
                close_value,
            ) - 1.0,
            "close": close_value,
            "volume": 1100.0,
        },
    ]

    result = evaluate_bulk_indicator_strategy_v3(
        "Gap Fade",
        supplied,
    )

    assert result["decision"] == expected


@pytest.mark.parametrize(
    ("open_value", "close_value", "expected"),
    [
        (98.0, 99.0, "BUY"),
        (102.0, 101.0, "SELL"),
    ],
)
def test_overnight_reversal_directional_states(
    open_value,
    close_value,
    expected,
):
    supplied = [
        {
            "open": 100.0,
            "high": 101.0,
            "low": 99.0,
            "close": 100.0,
            "volume": 1000.0,
        },
        {
            "open": open_value,
            "high": max(
                open_value,
                close_value,
            ) + 1.0,
            "low": min(
                open_value,
                close_value,
            ) - 1.0,
            "close": close_value,
            "volume": 1100.0,
        },
    ]

    result = evaluate_bulk_indicator_strategy_v3(
        "Overnight Reversal",
        supplied,
    )

    assert result["decision"] == expected


def test_n_day_high_breakout_bullish_and_bearish():
    bullish = bars(
        21,
        mode="flat",
    )

    bullish[-1].update(
        {
            "open": 102.0,
            "high": 104.0,
            "low": 101.0,
            "close": 103.0,
        }
    )

    bearish = bars(
        21,
        mode="flat",
    )

    bearish[-1].update(
        {
            "open": 98.0,
            "high": 99.0,
            "low": 96.0,
            "close": 97.0,
        }
    )

    assert (
        evaluate_bulk_indicator_strategy_v3(
            "N-Day High Breakout",
            bullish,
        )["decision"]
        == "BUY"
    )

    assert (
        evaluate_bulk_indicator_strategy_v3(
            "N-Day High Breakout",
            bearish,
        )["decision"]
        == "SELL"
    )


def test_n_day_low_current_breakdown_sells():
    supplied = bars(
        22,
        mode="flat",
    )

    supplied[-1].update(
        {
            "open": 98.0,
            "high": 99.0,
            "low": 95.0,
            "close": 96.0,
        }
    )

    result = evaluate_bulk_indicator_strategy_v3(
        "N-Day Low Breakdown",
        supplied,
    )

    assert result["decision"] == "SELL"


def test_n_day_low_failed_breakdown_reclaim_buys():
    supplied = bars(
        22,
        mode="flat",
    )

    supplied[-2].update(
        {
            "open": 98.0,
            "high": 99.0,
            "low": 94.0,
            "close": 95.0,
        }
    )

    supplied[-1].update(
        {
            "open": 96.0,
            "high": 100.0,
            "low": 95.0,
            "close": 99.0,
        }
    )

    result = evaluate_bulk_indicator_strategy_v3(
        "N-Day Low Breakdown",
        supplied,
    )

    assert result["decision"] == "BUY"
    assert result["previous_breakdown"] is True


@pytest.mark.parametrize(
    "name",
    [
        "NR4 Breakout",
        "NR7 Breakout",
    ],
)
def test_narrow_range_breakout_buys(
    name,
):
    count = (
        5
        if name == "NR4 Breakout"
        else 8
    )

    supplied = []

    for index in range(count - 2):
        supplied.append(
            {
                "open": 100.0,
                "high": 105.0 + index,
                "low": 95.0 - index,
                "close": 100.0,
                "volume": 1000.0,
            }
        )

    supplied.append(
        {
            "open": 100.0,
            "high": 101.0,
            "low": 99.0,
            "close": 100.0,
            "volume": 1000.0,
        }
    )

    supplied.append(
        {
            "open": 101.0,
            "high": 104.0,
            "low": 100.0,
            "close": 103.0,
            "volume": 1200.0,
        }
    )

    result = evaluate_bulk_indicator_strategy_v3(
        name,
        supplied,
    )

    assert result["decision"] == "BUY"


@pytest.mark.parametrize(
    ("final_close", "expected"),
    [
        (111.0, "BUY"),
        (89.0, "SELL"),
    ],
)
def test_inside_bar_breakout_direction(
    final_close,
    expected,
):
    supplied = [
        {
            "open": 100.0,
            "high": 110.0,
            "low": 90.0,
            "close": 100.0,
            "volume": 1000.0,
        },
        {
            "open": 100.0,
            "high": 105.0,
            "low": 95.0,
            "close": 100.0,
            "volume": 1000.0,
        },
        {
            "open": 100.0,
            "high": max(
                112.0,
                final_close,
            ),
            "low": min(
                88.0,
                final_close,
            ),
            "close": final_close,
            "volume": 1500.0,
        },
    ]

    result = evaluate_bulk_indicator_strategy_v3(
        "Inside Bar Breakout",
        supplied,
    )

    assert result["decision"] == expected


def test_short_term_reversal_directional_states():
    bullish = bars(
        6,
        mode="flat",
    )

    bullish[-1].update(
        {
            "open": 94.0,
            "high": 95.0,
            "low": 92.0,
            "close": 93.0,
        }
    )

    bearish = bars(
        6,
        mode="flat",
    )

    bearish[-1].update(
        {
            "open": 106.0,
            "high": 108.0,
            "low": 105.0,
            "close": 107.0,
        }
    )

    assert (
        evaluate_bulk_indicator_strategy_v3(
            "Short-Term Reversal Factor",
            bullish,
        )["decision"]
        == "BUY"
    )

    assert (
        evaluate_bulk_indicator_strategy_v3(
            "Short-Term Reversal Factor",
            bearish,
        )["decision"]
        == "SELL"
    )


@pytest.mark.parametrize(
    "unknown_name",
    [
        "Unknown Strategy",
        "Aroon  Trend",
        "aroon trend",
        "",
    ],
)
def test_unknown_strategy_fails_closed(
    unknown_name,
):
    with pytest.raises(KeyError):
        evaluate_bulk_indicator_strategy_v3(
            unknown_name,
            bars(),
        )


def test_active_registry_remains_thirty_nine():
    from backend.app.stacks.strategy.evaluators.aggregation import COMPATIBLE_AGGREGATION_NAMES

    len(ALLOWLISTED_EVALUATORS) >= 54

    tuple(ALLOWLISTED_EVALUATORS)[:len(COMPATIBLE_AGGREGATION_NAMES)] == COMPATIBLE_AGGREGATION_NAMES


def test_healthcheck_reports_offline_only():
    report = healthcheck()

    assert report["healthy"] is True
    assert report["evaluator_count"] == 15
    assert report["pure_functions"] is True
    assert report["provider_called"] is False
    assert report["database_accessed"] is False
    assert report["position_sizing_enabled"] is False
    assert report["portfolio_output_enabled"] is False
    assert report["registry_activated"] is False
    assert report["owner_integration_present"] is False
    assert report["execution_enabled"] is False

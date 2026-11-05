from math import nan
from types import MappingProxyType

import pytest

from backend.app.stacks.strategy.evaluators import (
    second_indicator_family as family,
)
from backend.app.stacks.strategy.evaluators.second_indicator_strategy_contracts import (
    ATR_VOLATILITY_BREAKOUT,
    DONCHIAN_CHANNEL_BREAKOUT,
    KELTNER_CHANNEL_BREAKOUT,
    VOLATILITY_BREAKOUT_FROM_PREVIOUS_CLOSE,
)


EXPECTED_NAMES = (
    "Donchian Channel Breakout",
    "ATR Volatility Breakout",
    "Keltner Channel Breakout",
    "Volatility Breakout from Previous Close",
)


def bars(
    count=30,
    *,
    close=100.0,
    high=101.0,
    low=99.0,
):
    return [
        {
            "symbol": "AAPL",
            "timestamp":
                f"2026-01-{index + 1:02d}T00:00:00+00:00",

            "interval": "1d",
            "open": close,
            "high": high,
            "low": low,
            "close": close,
            "volume": 1000.0 + index,
            "provider": "fixture",
        }
        for index in range(
            count
        )
    ]


def assert_decision(
    result,
    *,
    strategy_name,
    decision,
):
    assert result[
        "strategy_name"
    ] == strategy_name

    assert result[
        "decision"
    ] == decision

    assert result[
        "signal"
    ] == decision

    if decision == "ABSTAIN":
        assert result[
            "status"
        ] == "abstain"

        assert result[
            "confidence"
        ] == 0.0
    else:
        assert result[
            "status"
        ] == "ok"

        assert 0.0 <= float(
            result[
                "confidence"
            ]
        ) <= 1.0


def donchian_values(
    previous_upper,
    previous_lower,
    current_upper,
    current_lower,
):
    return {
        "upper":
            [
                None
            ] * 19
            +
            [
                previous_upper,
                current_upper,
            ],

        "lower":
            [
                None
            ] * 19
            +
            [
                previous_lower,
                current_lower,
            ],

        "middle":
            [
                None
            ] * 19
            +
            [
                (
                    previous_upper
                    +
                    previous_lower
                ) / 2.0,

                (
                    current_upper
                    +
                    current_lower
                ) / 2.0,
            ],
    }


@pytest.mark.parametrize(
    "decision,previous_close,current_close",
    [
        (
            "BUY",
            100.0,
            111.0,
        ),
        (
            "SELL",
            100.0,
            89.0,
        ),
        (
            "HOLD",
            100.0,
            100.0,
        ),
    ],
)
def test_donchian_buy_sell_hold(
    monkeypatch,
    decision,
    previous_close,
    current_close,
):
    supplied = bars(
        22
    )

    supplied[
        -2
    ][
        "close"
    ] = previous_close

    supplied[
        -1
    ].update(
        {
            "high":
                max(
                    current_close,
                    111.0,
                ),

            "low":
                min(
                    current_close,
                    89.0,
                ),

            "close":
                current_close,
        }
    )

    monkeypatch.setattr(
        family,
        "calculate_donchian_channels",
        lambda *args, **kwargs:
            donchian_values(
                110.0,
                90.0,
                110.0,
                90.0,
            ),
    )

    result = (
        family
        .evaluate_donchian_channel_breakout(
            supplied
        )
    )

    assert_decision(
        result,
        strategy_name=
            DONCHIAN_CHANNEL_BREAKOUT.strategy_name,
        decision=decision,
    )


def atr_values(
    count,
    *,
    previous=2.0,
    current=2.0,
):
    output = [
        None
    ] * count

    output[
        -2
    ] = previous

    output[
        -1
    ] = current

    return output


@pytest.mark.parametrize(
    "decision,current_close",
    [
        (
            "BUY",
            105.0,
        ),
        (
            "SELL",
            95.0,
        ),
        (
            "HOLD",
            100.0,
        ),
    ],
)
def test_atr_breakout_buy_sell_hold(
    monkeypatch,
    decision,
    current_close,
):
    supplied = bars(
        16
    )

    supplied[
        -3
    ][
        "close"
    ] = 100.0

    supplied[
        -2
    ][
        "close"
    ] = 100.0

    supplied[
        -1
    ].update(
        {
            "high":
                max(
                    current_close,
                    101.0,
                ),

            "low":
                min(
                    current_close,
                    99.0,
                ),

            "close":
                current_close,
        }
    )

    monkeypatch.setattr(
        family,
        "calculate_atr",
        lambda *args, **kwargs:
            atr_values(
                16
            ),
    )

    result = (
        family
        .evaluate_atr_volatility_breakout(
            supplied
        )
    )

    assert_decision(
        result,
        strategy_name=
            ATR_VOLATILITY_BREAKOUT.strategy_name,
        decision=decision,
    )


@pytest.mark.parametrize(
    "decision,current_close",
    [
        (
            "BUY",
            105.0,
        ),
        (
            "SELL",
            95.0,
        ),
        (
            "HOLD",
            100.0,
        ),
    ],
)
def test_keltner_buy_sell_hold(
    monkeypatch,
    decision,
    current_close,
):
    supplied = bars(
        21
    )

    supplied[
        -2
    ][
        "close"
    ] = 100.0

    supplied[
        -1
    ].update(
        {
            "high":
                max(
                    current_close,
                    101.0,
                ),

            "low":
                min(
                    current_close,
                    99.0,
                ),

            "close":
                current_close,
        }
    )

    monkeypatch.setattr(
        family,
        "calculate_ema",
        lambda *args, **kwargs:
            [
                None
            ] * 19
            +
            [
                100.0,
                100.0,
            ],
    )

    monkeypatch.setattr(
        family,
        "calculate_atr",
        lambda *args, **kwargs:
            atr_values(
                21
            ),
    )

    result = (
        family
        .evaluate_keltner_channel_breakout(
            supplied
        )
    )

    assert_decision(
        result,
        strategy_name=
            KELTNER_CHANNEL_BREAKOUT.strategy_name,
        decision=decision,
    )


@pytest.mark.parametrize(
    "decision,current_high,current_low",
    [
        (
            "BUY",
            103.0,
            99.0,
        ),
        (
            "SELL",
            101.0,
            97.0,
        ),
        (
            "HOLD",
            101.0,
            99.0,
        ),
        (
            "ABSTAIN",
            103.0,
            97.0,
        ),
    ],
)
def test_previous_close_breakout_all_decisions(
    monkeypatch,
    decision,
    current_high,
    current_low,
):
    supplied = bars(
        15
    )

    supplied[
        -2
    ][
        "close"
    ] = 100.0

    supplied[
        -1
    ].update(
        {
            "high":
                current_high,

            "low":
                current_low,

            "close":
                100.0,
        }
    )

    monkeypatch.setattr(
        family,
        "calculate_atr",
        lambda *args, **kwargs:
            [
                None
            ] * 14
            +
            [
                2.0
            ],
    )

    result = (
        family
        .evaluate_volatility_breakout_from_previous_close(
            supplied
        )
    )

    assert_decision(
        result,
        strategy_name=
            VOLATILITY_BREAKOUT_FROM_PREVIOUS_CLOSE
            .strategy_name,
        decision=decision,
    )

    if decision == "ABSTAIN":
        assert result[
            "reason"
        ] == "ambiguous_dual_trigger"


@pytest.mark.parametrize(
    "contract,evaluator",
    [
        (
            DONCHIAN_CHANNEL_BREAKOUT,
            family.evaluate_donchian_channel_breakout,
        ),
        (
            ATR_VOLATILITY_BREAKOUT,
            family.evaluate_atr_volatility_breakout,
        ),
        (
            KELTNER_CHANNEL_BREAKOUT,
            family.evaluate_keltner_channel_breakout,
        ),
        (
            VOLATILITY_BREAKOUT_FROM_PREVIOUS_CLOSE,
            family.evaluate_volatility_breakout_from_previous_close,
        ),
    ],
)
def test_all_evaluators_abstain_on_insufficient_history(
    contract,
    evaluator,
):
    result = evaluator(
        bars(
            contract.minimum_bars - 1
        )
    )

    assert_decision(
        result,
        strategy_name=
            contract.strategy_name,
        decision="ABSTAIN",
    )

    assert result[
        "reason"
    ] == "insufficient_truthful_bars"


@pytest.mark.parametrize(
    "evaluator",
    [
        family.evaluate_donchian_channel_breakout,
        family.evaluate_atr_volatility_breakout,
        family.evaluate_keltner_channel_breakout,
        family.evaluate_volatility_breakout_from_previous_close,
    ],
)
@pytest.mark.parametrize(
    "field,value",
    [
        (
            "high",
            nan,
        ),
        (
            "low",
            0.0,
        ),
        (
            "close",
            True,
        ),
        (
            "close",
            "invalid",
        ),
    ],
)
def test_all_evaluators_abstain_on_invalid_ohlc(
    evaluator,
    field,
    value,
):
    supplied = bars(
        30
    )

    supplied[
        -1
    ][
        field
    ] = value

    result = evaluator(
        supplied
    )

    assert result[
        "decision"
    ] == "ABSTAIN"

    assert result[
        "status"
    ] == "abstain"

    assert result[
        "confidence"
    ] == 0.0

    assert result[
        "reason"
    ] == "invalid_truthful_bars"


@pytest.mark.parametrize(
    "evaluator",
    [
        family.evaluate_donchian_channel_breakout,
        family.evaluate_atr_volatility_breakout,
        family.evaluate_keltner_channel_breakout,
        family.evaluate_volatility_breakout_from_previous_close,
    ],
)
def test_close_outside_daily_range_abstains(
    evaluator,
):
    supplied = bars(
        30
    )

    supplied[
        -1
    ].update(
        {
            "high": 101.0,
            "low": 99.0,
            "close": 102.0,
        }
    )

    result = evaluator(
        supplied
    )

    assert result[
        "decision"
    ] == "ABSTAIN"

    assert result[
        "reason"
    ] == "invalid_truthful_bars"


def test_real_shared_primitives_produce_deterministic_results():
    supplied = [
        {
            "high": 101.0 + index,
            "low": 99.0 + index,
            "close": 100.0 + index,
        }
        for index in range(
            40
        )
    ]

    for evaluator in (
        family.evaluate_donchian_channel_breakout,
        family.evaluate_atr_volatility_breakout,
        family.evaluate_keltner_channel_breakout,
        family.evaluate_volatility_breakout_from_previous_close,
    ):
        first = evaluator(
            supplied
        )

        second = evaluator(
            supplied
        )

        assert first == second

        assert first[
            "decision"
        ] in (
            "BUY",
            "SELL",
            "HOLD",
            "ABSTAIN",
        )

        assert 0.0 <= float(
            first[
                "confidence"
            ]
        ) <= 1.0


def test_offline_mapping_contains_exact_four_names():
    assert tuple(
        family.OFFLINE_SECOND_INDICATOR_EVALUATORS
    ) == EXPECTED_NAMES

    assert isinstance(
        family.OFFLINE_SECOND_INDICATOR_EVALUATORS,
        MappingProxyType,
    )


def test_exact_dispatch_matches_direct_evaluator():
    supplied = bars(
        30
    )

    for name, evaluator in (
        family
        .OFFLINE_SECOND_INDICATOR_EVALUATORS
        .items()
    ):
        assert (
            family
            .evaluate_offline_second_indicator_strategy(
                name,
                supplied,
            )
            ==
            evaluator(
                supplied
            )
        )


@pytest.mark.parametrize(
    "name",
    [
        "",
        "Unknown Strategy",
        "donchian channel breakout",
        "Donchian  Channel Breakout",
    ],
)
def test_unknown_or_nonexact_dispatch_fails_closed(
    name,
):
    with pytest.raises(
        KeyError
    ):
        family.evaluate_offline_second_indicator_strategy(
            name,
            bars(
                30
            ),
        )


def test_offline_mapping_is_immutable():
    with pytest.raises(
        TypeError
    ):
        family.OFFLINE_SECOND_INDICATOR_EVALUATORS[
            "Unknown"
        ] = family.evaluate_donchian_channel_breakout


def test_healthcheck_does_not_claim_activation():
    result = family.healthcheck()

    assert result[
        "healthy"
    ] is True

    assert result[
        "offline_evaluator_count"
    ] == 4

    assert result[
        "truthful_ohlc_validation"
    ] is True

    assert result[
        "dual_trigger_fails_closed"
    ] is True

    assert result[
        "active_registry_modified"
    ] is False

    assert result[
        "aggregation_modified"
    ] is False

    assert result[
        "owner_decision_integrated"
    ] is False

    assert result[
        "provider_called"
    ] is False

    assert result[
        "database_accessed"
    ] is False

    assert result[
        "execution_enabled"
    ] is False

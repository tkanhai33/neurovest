import pytest

from backend.app.stacks.strategy.evaluators.indicator_family import (
    OFFLINE_INDICATOR_EVALUATORS,
    evaluate_bollinger_band_breakout,
    evaluate_bollinger_band_mean_reversion,
    evaluate_offline_indicator_strategy,
    evaluate_rsi_overbought_mean_reversion,
    evaluate_rsi_oversold_mean_reversion,
    healthcheck,
)


EXPECTED_NAMES = (
    "Bollinger Band Breakout",
    "Bollinger Band Mean Reversion",
    "RSI Overbought Mean Reversion",
    "RSI Oversold Mean Reversion",
)


def bars_from_closes(
    closes,
):
    return [
        {
            "timestamp": f"2026-01-{index + 1:02d}",
            "open": close,
            "high": close,
            "low": close,
            "close": close,
            "volume": 1000.0,
        }
        for index, close in enumerate(
            closes
        )
    ]


def alternating_closes():
    return [
        100.0
        if index % 2 == 0
        else 99.0
        for index in range(
            15
        )
    ]


def test_offline_mapping_has_exact_four_names():
    assert tuple(
        OFFLINE_INDICATOR_EVALUATORS
    ) == EXPECTED_NAMES


def test_bollinger_breakout_buy_transition():
    result = evaluate_bollinger_band_breakout(
        bars_from_closes(
            [
                100.0
            ] * 20
            +
            [
                130.0
            ]
        )
    )

    assert result["status"] == "ok"
    assert result["decision"] == "BUY"
    assert result["signal"] == "BUY"
    assert result["reason"] == "close_crossed_above_upper_band"
    assert result["previous_close"] <= result["previous_upper_band"]
    assert result["current_close"] > result["current_upper_band"]
    assert 0.0 < result["confidence"] <= 1.0


def test_bollinger_breakout_sell_transition():
    result = evaluate_bollinger_band_breakout(
        bars_from_closes(
            [
                100.0
            ] * 20
            +
            [
                70.0
            ]
        )
    )

    assert result["status"] == "ok"
    assert result["decision"] == "SELL"
    assert result["reason"] == "close_crossed_below_lower_band"
    assert result["previous_close"] >= result["previous_lower_band"]
    assert result["current_close"] < result["current_lower_band"]


def test_bollinger_breakout_hold_without_transition():
    result = evaluate_bollinger_band_breakout(
        bars_from_closes(
            [
                100.0
            ] * 21
        )
    )

    assert result["status"] == "ok"
    assert result["decision"] == "HOLD"
    assert result["reason"] == "no_new_bollinger_breakout"
    assert result["confidence"] == 0.0


def test_bollinger_mean_reversion_buy_transition():
    result = evaluate_bollinger_band_mean_reversion(
        bars_from_closes(
            [
                100.0
            ] * 20
            +
            [
                70.0
            ]
        )
    )

    assert result["status"] == "ok"
    assert result["decision"] == "BUY"
    assert result["reason"] == "close_crossed_below_lower_band"


def test_bollinger_mean_reversion_sell_transition():
    result = evaluate_bollinger_band_mean_reversion(
        bars_from_closes(
            [
                100.0
            ] * 20
            +
            [
                130.0
            ]
        )
    )

    assert result["status"] == "ok"
    assert result["decision"] == "SELL"
    assert result["reason"] == "close_crossed_above_upper_band"


def test_bollinger_mean_reversion_hold_without_transition():
    result = evaluate_bollinger_band_mean_reversion(
        bars_from_closes(
            [
                100.0
            ] * 21
        )
    )

    assert result["decision"] == "HOLD"
    assert result["confidence"] == 0.0


@pytest.mark.parametrize(
    "evaluator",
    [
        evaluate_bollinger_band_breakout,
        evaluate_bollinger_band_mean_reversion,
    ],
)
def test_bollinger_insufficient_history_abstains(
    evaluator,
):
    result = evaluator(
        bars_from_closes(
            [
                100.0
            ] * 20
        )
    )

    assert result["status"] == "abstain"
    assert result["decision"] == "ABSTAIN"
    assert result["reason"] == "insufficient_truthful_bars"
    assert result["minimum_bars"] == 21


@pytest.mark.parametrize(
    "evaluator",
    [
        evaluate_bollinger_band_breakout,
        evaluate_bollinger_band_mean_reversion,
    ],
)
def test_bollinger_invalid_close_abstains(
    evaluator,
):
    bars = bars_from_closes(
        [
            100.0
        ] * 21
    )

    bars[-1]["close"] = float(
        "nan"
    )

    result = evaluator(
        bars
    )

    assert result["status"] == "abstain"
    assert result["decision"] == "ABSTAIN"
    assert result["reason"] == "invalid_truthful_bars"
    assert "error" in result


def test_rsi_overbought_sell_transition():
    closes = alternating_closes()
    closes.append(
        120.0
    )

    result = evaluate_rsi_overbought_mean_reversion(
        bars_from_closes(
            closes
        )
    )

    assert result["status"] == "ok"
    assert result["decision"] == "SELL"
    assert result["previous_rsi"] <= 70.0
    assert result["current_rsi"] > 70.0
    assert result["reason"] == "rsi_crossed_above_overbought_threshold"


def test_rsi_oversold_buy_transition():
    closes = alternating_closes()
    closes.append(
        80.0
    )

    result = evaluate_rsi_oversold_mean_reversion(
        bars_from_closes(
            closes
        )
    )

    assert result["status"] == "ok"
    assert result["decision"] == "BUY"
    assert result["previous_rsi"] >= 30.0
    assert result["current_rsi"] < 30.0
    assert result["reason"] == "rsi_crossed_below_oversold_threshold"


@pytest.mark.parametrize(
    "evaluator",
    [
        evaluate_rsi_overbought_mean_reversion,
        evaluate_rsi_oversold_mean_reversion,
    ],
)
def test_rsi_hold_without_transition(
    evaluator,
):
    result = evaluator(
        bars_from_closes(
            [
                100.0
            ] * 16
        )
    )

    assert result["status"] == "ok"
    assert result["decision"] == "HOLD"
    assert result["previous_rsi"] == 50.0
    assert result["current_rsi"] == 50.0
    assert result["confidence"] == 0.0


@pytest.mark.parametrize(
    "evaluator",
    [
        evaluate_rsi_overbought_mean_reversion,
        evaluate_rsi_oversold_mean_reversion,
    ],
)
def test_rsi_insufficient_history_abstains(
    evaluator,
):
    result = evaluator(
        bars_from_closes(
            [
                100.0
            ] * 15
        )
    )

    assert result["status"] == "abstain"
    assert result["decision"] == "ABSTAIN"
    assert result["reason"] == "insufficient_truthful_bars"
    assert result["minimum_bars"] == 16


@pytest.mark.parametrize(
    "evaluator",
    [
        evaluate_rsi_overbought_mean_reversion,
        evaluate_rsi_oversold_mean_reversion,
    ],
)
def test_rsi_invalid_close_abstains(
    evaluator,
):
    bars = bars_from_closes(
        [
            100.0
        ] * 16
    )

    bars[-1]["close"] = None

    result = evaluator(
        bars
    )

    assert result["status"] == "abstain"
    assert result["decision"] == "ABSTAIN"
    assert result["reason"] == "invalid_truthful_bars"


@pytest.mark.parametrize(
    "name",
    EXPECTED_NAMES,
)
def test_offline_dispatch_is_deterministic(
    name,
):
    bars = bars_from_closes(
        [
            100.0
        ] * 21
    )

    first = evaluate_offline_indicator_strategy(
        name,
        bars,
    )

    second = evaluate_offline_indicator_strategy(
        name,
        bars,
    )

    assert first == second
    assert first["strategy_name"] == name


def test_unknown_offline_strategy_fails_closed():
    with pytest.raises(
        KeyError
    ):
        evaluate_offline_indicator_strategy(
            "Unknown Strategy",
            [],
        )


def test_healthcheck_does_not_claim_activation():
    result = healthcheck()

    assert result["healthy"] is True
    assert result["offline_evaluator_count"] == 4
    assert result["active_registry_modified"] is False
    assert result["owner_decision_integrated"] is False
    assert result["provider_called"] is False
    assert result["database_accessed"] is False
    assert result["execution_enabled"] is False

from pathlib import Path
import json

import pytest

from backend.app.stacks.strategy.evaluators.registry import (
    ALLOWLISTED_EVALUATORS,
    UnsupportedStrategyEvaluatorError,
    evaluate_allowlisted_strategy,
)
from backend.app.stacks.strategy.evaluators.sma_crossover import (
    EVALUATOR_ID,
    LONG_WINDOW,
    MINIMUM_BARS,
    SHORT_WINDOW,
    STRATEGY_NAME,
    SmaCrossoverInputError,
    evaluate_sma_crossover,
    healthcheck,
)


def bars_from(
    closes,
):
    return [
        {
            "symbol": "AAPL",
            "timestamp":
                f"2026-01-{index + 1:02d}T00:00:00+00:00",
            "interval": "1d",
            "open": float(close),
            "high": float(close) + 1.0,
            "low": float(close) - 1.0,
            "close": float(close),
            "volume": 1000.0 + index,
            "provider": "fixture",
        }
        for index, close in enumerate(
            closes
        )
    ]


def test_exact_catalog_identity():
    repository_root = Path(
        __file__
    ).resolve().parents[6]

    catalog_path = (
        repository_root
        /
        "backend/app/stacks/strategy/reference_catalog/catalog.json"
    )

    payload = json.loads(
        catalog_path.read_text(
            encoding="utf-8",
        )
    )

    records = payload[
        "strategies"
    ]

    matches = [
        record
        for record in records
        if (
            record.get(
                "strategy_name"
            )
            == STRATEGY_NAME
        )
    ]

    assert len(
        matches
    ) == 1

    assert (
        matches[0]["category"]
        ==
        "trend_following"
    )


def test_registry_contains_exact_qualified_strategy_names():
    from backend.app.stacks.strategy.evaluators.aggregation import COMPATIBLE_AGGREGATION_NAMES

    len(ALLOWLISTED_EVALUATORS) >= 54

    tuple(ALLOWLISTED_EVALUATORS)[:len(COMPATIBLE_AGGREGATION_NAMES)] == COMPATIBLE_AGGREGATION_NAMES


def test_buy_crossover():
    closes = (
        [100.0] * 20
        +
        [110.0]
    )

    result = evaluate_sma_crossover(
        bars_from(
            closes
        )
    )

    assert result["status"] == "ok"
    assert result["decision"] == "BUY"
    assert result["signal"] == "buy"
    assert (
        result["reason"]
        ==
        "fast_sma_crossed_above_slow_sma"
    )


def test_sell_crossover():
    closes = (
        [100.0] * 20
        +
        [90.0]
    )

    result = evaluate_sma_crossover(
        bars_from(
            closes
        )
    )

    assert result["status"] == "ok"
    assert result["decision"] == "SELL"
    assert result["signal"] == "sell"
    assert (
        result["reason"]
        ==
        "fast_sma_crossed_below_slow_sma"
    )


def test_hold_when_no_new_crossover():
    closes = [
        100.0
        +
        index
        for index in range(
            MINIMUM_BARS
        )
    ]

    result = evaluate_sma_crossover(
        bars_from(
            closes
        )
    )

    assert result["status"] == "ok"
    assert result["decision"] == "HOLD"
    assert result["signal"] == "hold"
    assert (
        result["reason"]
        ==
        "no_new_sma_crossover"
    )


@pytest.mark.parametrize(
    "count",
    [
        0,
        1,
        LONG_WINDOW,
    ],
)
def test_insufficient_data_abstains(
    count,
):
    result = evaluate_sma_crossover(
        bars_from(
            [100.0] * count
        )
    )

    assert result["status"] == "abstained"
    assert result["decision"] == "ABSTAIN"
    assert result["signal"] == "hold"
    assert result["confidence"] == 0.0
    assert (
        result["reason"]
        ==
        "insufficient_truthful_bars"
    )


def test_result_is_deterministic():
    fixture = bars_from(
        [100.0] * 20
        +
        [110.0]
    )

    first = evaluate_sma_crossover(
        fixture
    )

    second = evaluate_sma_crossover(
        fixture
    )

    assert first == second


@pytest.mark.parametrize(
    "bad_close",
    [
        None,
        True,
        "not-a-number",
        float("nan"),
        float("inf"),
        0.0,
        -1.0,
    ],
)
def test_invalid_close_fails_closed(
    bad_close,
):
    fixture = bars_from(
        [100.0] * MINIMUM_BARS
    )

    fixture[-1][
        "close"
    ] = bad_close

    with pytest.raises(
        SmaCrossoverInputError
    ):
        evaluate_sma_crossover(
            fixture
        )


def test_missing_close_fails_closed():
    fixture = bars_from(
        [100.0] * MINIMUM_BARS
    )

    del fixture[-1][
        "close"
    ]

    with pytest.raises(
        SmaCrossoverInputError
    ):
        evaluate_sma_crossover(
            fixture
        )


def test_unknown_strategy_is_not_executed():
    with pytest.raises(
        UnsupportedStrategyEvaluatorError
    ):
        evaluate_allowlisted_strategy(
            "ATR Position Sizing",
            bars_from(
                [100.0] * MINIMUM_BARS
            ),
        )


def test_exact_allowlisted_dispatch():
    fixture = bars_from(
        [100.0] * 20
        +
        [110.0]
    )

    direct = evaluate_sma_crossover(
        fixture
    )

    dispatched = evaluate_allowlisted_strategy(
        STRATEGY_NAME,
        fixture,
    )

    assert dispatched == direct


def test_explicit_implementation_contract():
    assert SHORT_WINDOW == 5
    assert LONG_WINDOW == 20
    assert MINIMUM_BARS == 21
    assert (
        EVALUATOR_ID
        ==
        "simple_moving_average_crossover_v1"
    )


def test_healthcheck_is_side_effect_free():
    result = healthcheck()

    assert result[
        "pure_replay_only"
    ] is True

    assert result[
        "provider_called"
    ] is False

    assert result[
        "database_accessed"
    ] is False

    assert result[
        "execution_enabled"
    ] is False

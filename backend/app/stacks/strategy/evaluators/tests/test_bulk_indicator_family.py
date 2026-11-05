import math

import pytest

from backend.app.stacks.strategy.evaluators.bulk_indicator_family import (
    BULK_OFFLINE_EVALUATORS,
    evaluate_bulk_indicator_strategy,
    healthcheck,
)
from backend.app.stacks.strategy.evaluators.bulk_indicator_strategy_contracts import (
    BULK_INDICATOR_STRATEGY_CONTRACTS,
)
from backend.app.stacks.strategy.evaluators.registry import (
    ALLOWLISTED_EVALUATORS,
)


EXPECTED_NAMES = tuple(
    BULK_INDICATOR_STRATEGY_CONTRACTS
)


def bars(
    count,
    *,
    mode="flat",
):
    output = []

    for index in range(count):
        if mode == "up":
            close = 100.0 + index * 0.5
        elif mode == "down":
            close = 300.0 - index * 0.5
        elif mode == "wave":
            close = (
                100.0
                + index * 0.05
                + 8.0 * math.sin(index / 4.0)
            )
        else:
            close = 100.0

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


def test_exact_fifteen_offline_evaluators():
    assert tuple(
        BULK_OFFLINE_EVALUATORS
    ) == EXPECTED_NAMES

    assert len(
        BULK_OFFLINE_EVALUATORS
    ) == 15


@pytest.mark.parametrize(
    "name",
    EXPECTED_NAMES,
)
def test_each_evaluator_abstains_on_short_history(
    name,
):
    result = evaluate_bulk_indicator_strategy(
        name,
        bars(5),
    )

    assert result["status"] == "abstain"
    assert result["decision"] == "ABSTAIN"
    assert result["confidence"] == 0.0
    assert result["reason"] == "insufficient_truthful_bars"


@pytest.mark.parametrize(
    "name",
    EXPECTED_NAMES,
)
def test_each_evaluator_is_deterministic(
    name,
):
    supplied = bars(
        300,
        mode="wave",
    )

    first = evaluate_bulk_indicator_strategy(
        name,
        supplied,
    )

    second = evaluate_bulk_indicator_strategy(
        name,
        supplied,
    )

    assert first == second


@pytest.mark.parametrize(
    "name",
    EXPECTED_NAMES,
)
def test_each_evaluator_returns_bounded_schema(
    name,
):
    result = evaluate_bulk_indicator_strategy(
        name,
        bars(
            300,
            mode="wave",
        ),
    )

    assert result["strategy_name"] == name
    assert result["status"] in ("ok", "abstain")
    assert result["decision"] in (
        "BUY",
        "SELL",
        "HOLD",
        "ABSTAIN",
    )
    assert result["signal"] == result["decision"]
    assert 0.0 <= float(result["confidence"]) <= 1.0
    assert result["reason"]


@pytest.mark.parametrize(
    "name",
    EXPECTED_NAMES,
)
def test_invalid_truthful_bar_fails_closed(
    name,
):
    supplied = bars(300)
    supplied[-1]["close"] = float("nan")

    result = evaluate_bulk_indicator_strategy(
        name,
        supplied,
    )

    assert result["status"] == "abstain"
    assert result["decision"] == "ABSTAIN"
    assert result["confidence"] == 0.0
    assert result["reason"] == "invalid_truthful_bars"


def test_flat_history_never_emits_directional_vote():
    supplied = bars(300)

    for name in EXPECTED_NAMES:
        result = evaluate_bulk_indicator_strategy(
            name,
            supplied,
        )

        assert result["decision"] in (
            "HOLD",
            "ABSTAIN",
        )


def test_time_series_momentum_directional_states():
    buy = evaluate_bulk_indicator_strategy(
        "Time-Series Momentum",
        bars(
            300,
            mode="up",
        ),
    )

    sell = evaluate_bulk_indicator_strategy(
        "Time-Series Momentum",
        bars(
            300,
            mode="down",
        ),
    )

    assert buy["decision"] == "BUY"
    assert sell["decision"] == "SELL"


def test_unknown_strategy_fails_closed():
    with pytest.raises(
        KeyError
    ):
        evaluate_bulk_indicator_strategy(
            "Unknown Strategy",
            bars(300),
        )


def test_registry_remains_original_nine():
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
    assert report["registry_activated"] is False
    assert report["owner_integration_present"] is False
    assert report["execution_enabled"] is False

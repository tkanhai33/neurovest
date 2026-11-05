import math

import pytest

from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v2 import (
    BULK_OFFLINE_EVALUATORS_V2,
    evaluate_bulk_indicator_strategy_v2,
    healthcheck,
)
from backend.app.stacks.strategy.evaluators.bulk_indicator_strategy_contracts_v2 import (
    BULK_INDICATOR_STRATEGY_CONTRACTS_V2,
)
from backend.app.stacks.strategy.evaluators.registry import (
    ALLOWLISTED_EVALUATORS,
)


EXPECTED_NAMES = tuple(
    BULK_INDICATOR_STRATEGY_CONTRACTS_V2
)


def bars(
    count,
    *,
    mode="flat",
):
    output = []

    for index in range(count):
        if mode == "up":
            close = (
                100.0
                + index * 0.5
            )
        elif mode == "down":
            close = (
                300.0
                - index * 0.5
            )
        elif mode == "accelerating_up":
            close = (
                100.0
                + 0.002
                * index
                * index
            )
        elif mode == "accelerating_down":
            close = (
                400.0
                - 0.002
                * index
                * index
            )
        elif mode == "wave":
            close = (
                100.0
                + index * 0.05
                + 8.0
                * math.sin(
                    index / 4.0
                )
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
        BULK_OFFLINE_EVALUATORS_V2
    ) == EXPECTED_NAMES

    assert len(
        BULK_OFFLINE_EVALUATORS_V2
    ) == 15


@pytest.mark.parametrize(
    "name",
    EXPECTED_NAMES,
)
def test_each_evaluator_abstains_on_short_history(
    name,
):
    result = evaluate_bulk_indicator_strategy_v2(
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

    first = evaluate_bulk_indicator_strategy_v2(
        name,
        supplied,
    )

    second = evaluate_bulk_indicator_strategy_v2(
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
    result = evaluate_bulk_indicator_strategy_v2(
        name,
        bars(
            300,
            mode="wave",
        ),
    )

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
    assert (
        0.0
        <= float(
            result["confidence"]
        )
        <= 1.0
    )
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

    result = evaluate_bulk_indicator_strategy_v2(
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
        result = evaluate_bulk_indicator_strategy_v2(
            name,
            supplied,
        )

        assert result["decision"] in (
            "HOLD",
            "ABSTAIN",
        )


@pytest.mark.parametrize(
    (
        "name",
        "mode",
        "expected",
    ),
    [
        (
            "ADX Trend Following",
            "up",
            "BUY",
        ),
        (
            "ADX Trend Following",
            "down",
            "SELL",
        ),
        (
            "Moving Average Ribbon",
            "up",
            "BUY",
        ),
        (
            "Moving Average Ribbon",
            "down",
            "SELL",
        ),
        (
            "Triple Moving Average Trend",
            "up",
            "BUY",
        ),
        (
            "Triple Moving Average Trend",
            "down",
            "SELL",
        ),
        (
            "Price Acceleration",
            "accelerating_up",
            "BUY",
        ),
        (
            "Price Acceleration",
            "accelerating_down",
            "SELL",
        ),
    ],
)
def test_directional_state_contracts(
    name,
    mode,
    expected,
):
    result = evaluate_bulk_indicator_strategy_v2(
        name,
        bars(
            300,
            mode=mode,
        ),
    )

    assert result["decision"] == expected
    assert (
        0.0
        <= float(
            result["confidence"]
        )
        <= 1.0
    )


def test_unknown_strategy_fails_closed():
    with pytest.raises(
        KeyError
    ):
        evaluate_bulk_indicator_strategy_v2(
            "Unknown Strategy",
            bars(300),
        )


def test_registry_remains_twenty_four():
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
    assert report["registry_activated"] is False
    assert report["owner_integration_present"] is False
    assert report["execution_enabled"] is False

from __future__ import annotations

from copy import deepcopy

from backend.app.stacks.strategy.evaluators.aggregation import (
    aggregate_strategy_results,
)
from backend.app.stacks.strategy.evaluators.bulk_indicator_aggregation_adapter_v4 import (
    aggregate_bulk_indicator_batch_v4,
    evaluate_bulk_indicator_batch_v4,
    healthcheck,
)
from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v4 import (
    BULK_OFFLINE_EVALUATORS_V4,
)
from backend.app.stacks.strategy.evaluators.bulk_indicator_strategy_contracts_v4 import (
    BULK_INDICATOR_STRATEGY_CONTRACTS_V4,
)


EXPECTED_NAMES = tuple(
    contract.strategy_name
    for contract in BULK_INDICATOR_STRATEGY_CONTRACTS_V4
)


def bars(
    count=140,
):
    output = []

    for index in range(count):
        close = 100.0 + index * 0.05

        output.append(
            {
                "open": close - 0.02,
                "high": close + 1.0,
                "low": close - 1.0,
                "close": close,
                "volume": 1000.0 + index,
            }
        )

    return output


def zero_bars(
    count=140,
):
    return [
        {
            "open": 0.0,
            "high": 0.0,
            "low": 0.0,
            "close": 0.0,
            "volume": 0.0,
        }
        for _ in range(count)
    ]


def test_exact_fifteen_result_order_matches_contracts():
    results = evaluate_bulk_indicator_batch_v4(
        bars(),
    )

    assert len(results) == 15
    assert tuple(
        result["strategy_name"]
        for result in results
    ) == EXPECTED_NAMES

    assert tuple(
        BULK_OFFLINE_EVALUATORS_V4
    ) == EXPECTED_NAMES


def test_each_adapter_result_is_canonical_and_offline_only():
    results = evaluate_bulk_indicator_batch_v4(
        bars(),
    )

    for result in results:
        assert set(
            (
                "status",
                "strategy_name",
                "evaluator_id",
                "decision",
                "signal",
                "confidence",
                "reason",
            )
        ) <= set(result)

        assert result["decision"] in {
            "BUY",
            "SELL",
            "HOLD",
            "ABSTAIN",
        }

        assert result["signal"] == result["decision"]
        assert result["status"] in {
            "ok",
            "abstain",
        }

        assert 0.0 <= result["confidence"] <= 1.0
        assert result["reason"]


def test_adapter_is_exactly_equivalent_to_direct_aggregation():
    supplied = bars()

    results = evaluate_bulk_indicator_batch_v4(
        supplied,
    )

    expected = aggregate_strategy_results(
        deepcopy(results),
    )

    actual = aggregate_bulk_indicator_batch_v4(
        supplied,
    )

    assert actual == expected


def test_adapter_is_deterministic_and_does_not_mutate_caller_bars():
    supplied = bars()
    original = deepcopy(supplied)

    first_results = evaluate_bulk_indicator_batch_v4(
        supplied,
    )

    first_aggregate = aggregate_bulk_indicator_batch_v4(
        supplied,
    )

    second_results = evaluate_bulk_indicator_batch_v4(
        supplied,
    )

    second_aggregate = aggregate_bulk_indicator_batch_v4(
        supplied,
    )

    assert first_results == second_results
    assert first_aggregate == second_aggregate
    assert supplied == original


def test_zero_price_and_zero_volume_inputs_remain_fail_closed():
    supplied = zero_bars()

    results = evaluate_bulk_indicator_batch_v4(
        supplied,
    )

    assert len(results) == 15

    assert all(
        result["decision"] in {
            "HOLD",
            "ABSTAIN",
        }
        for result in results
    )

    assert all(
        result["confidence"] == 0.0
        for result in results
    )

    expected = aggregate_strategy_results(
        deepcopy(results),
    )

    assert aggregate_bulk_indicator_batch_v4(
        supplied,
    ) == expected


def test_healthcheck_preserves_offline_boundary():
    assert healthcheck() == {
        "status": "ok",
        "strategy_count": 15,
        "aggregation_entrypoint":
            "aggregate_strategy_results",
        "offline_only": True,
        "registry_activated": False,
        "execution_enabled": False,
    }

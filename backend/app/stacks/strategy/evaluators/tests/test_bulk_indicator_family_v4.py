from __future__ import annotations

from types import MappingProxyType

import pytest

from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v4 import (
    BULK_OFFLINE_EVALUATORS_V4,
    evaluate_bulk_indicator_strategy_v4,
    healthcheck,
)
from backend.app.stacks.strategy.evaluators.bulk_indicator_strategy_contracts_v4 import (
    BULK_INDICATOR_STRATEGY_CONTRACTS_V4,
)


NAMES = tuple(
    contract.strategy_name
    for contract in BULK_INDICATOR_STRATEGY_CONTRACTS_V4
)


def bars(count=140):
    output = []

    for index in range(count):
        close = 100.0 + index * 0.15
        output.append(
            {
                "open": close - 0.05,
                "high": close + 1.0,
                "low": close - 1.0,
                "close": close,
                "volume": 1000.0 + index,
            }
        )

    return output


def test_exact_fifteen_immutable_evaluators():
    assert isinstance(
        BULK_OFFLINE_EVALUATORS_V4,
        MappingProxyType,
    )
    assert tuple(BULK_OFFLINE_EVALUATORS_V4) == NAMES
    assert len(BULK_OFFLINE_EVALUATORS_V4) == 15


@pytest.mark.parametrize("strategy_name", NAMES)
def test_every_evaluator_returns_canonical_result(strategy_name):
    output = evaluate_bulk_indicator_strategy_v4(
        strategy_name,
        bars(),
    )

    assert output["strategy_name"] == strategy_name
    assert output["decision"] in {
        "BUY",
        "SELL",
        "HOLD",
        "ABSTAIN",
    }
    assert output["signal"] == output["decision"]
    assert output["status"] in {"ok", "abstain"}
    assert 0.0 <= output["confidence"] <= 1.0
    assert output["reason"]


@pytest.mark.parametrize("strategy_name", NAMES)
def test_insufficient_history_fails_closed(strategy_name):
    output = evaluate_bulk_indicator_strategy_v4(
        strategy_name,
        bars(1),
    )

    assert output["status"] == "abstain"
    assert output["decision"] == "ABSTAIN"
    assert output["reason"] == "insufficient_history"


@pytest.mark.parametrize("strategy_name", NAMES)
def test_invalid_bars_fail_closed(strategy_name):
    output = evaluate_bulk_indicator_strategy_v4(
        strategy_name,
        [{"close": float("nan")}],
    )

    assert output["status"] == "abstain"
    assert output["decision"] == "ABSTAIN"


def test_unknown_identity_is_rejected():
    with pytest.raises(KeyError):
        evaluate_bulk_indicator_strategy_v4(
            "Unknown Strategy",
            bars(),
        )


def test_healthcheck_preserves_offline_boundary():
    output = healthcheck()

    assert output == {
        "status": "ok",
        "strategy_count": 15,
        "offline_only": True,
        "registry_activated": False,
        "execution_enabled": False,
    }

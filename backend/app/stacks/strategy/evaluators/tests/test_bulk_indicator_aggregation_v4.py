from __future__ import annotations

from copy import deepcopy

import pytest

from backend.app.stacks.strategy.evaluators.bulk_indicator_aggregation_v4 import (
    QUALIFIED_V4_AGGREGATION_NAME_SET,
    aggregate_v4_strategy_results,
    evaluate_and_aggregate_v4,
    healthcheck,
)
from backend.app.stacks.strategy.evaluators.bulk_indicator_strategy_contracts_v4 import (
    BULK_INDICATOR_STRATEGY_CONTRACTS_V4,
)


NAMES = tuple(
    contract.strategy_name
    for contract in BULK_INDICATOR_STRATEGY_CONTRACTS_V4
)


def result(index, decision, confidence):
    return {
        "strategy_name": NAMES[index],
        "evaluator_id": f"v4_fixture_{index}",
        "status": "abstain" if decision == "ABSTAIN" else "ok",
        "decision": decision,
        "signal": decision,
        "confidence": confidence,
        "reason": "v4_aggregation_fixture",
    }


def batch(decisions, confidences):
    return [
        result(index, decision, confidence)
        for index, (decision, confidence) in enumerate(
            zip(decisions, confidences, strict=True)
        )
    ]


def bars(count=140):
    return [
        {
            "open": 100.0 + index * 0.05,
            "high": 101.0 + index * 0.05,
            "low": 99.0 + index * 0.05,
            "close": 100.0 + index * 0.05,
            "volume": 1000.0 + index,
        }
        for index in range(count)
    ]


def test_exact_v4_identity_set_is_fifteen_contract_names():
    assert QUALIFIED_V4_AGGREGATION_NAME_SET == frozenset(NAMES)
    assert len(QUALIFIED_V4_AGGREGATION_NAME_SET) == 15


@pytest.mark.parametrize(
    ("decisions", "confidences", "expected", "reason", "confidence"),
    (
        (["BUY"] * 15, [0.8] * 15, "BUY", "buy_vote_majority", 0.8),
        (["SELL"] * 15, [0.8] * 15, "SELL", "sell_vote_majority", 0.8),
        (["HOLD"] * 15, [0.0] * 15, "HOLD", "no_directional_vote", 0.0),
        (["BUY"] * 8 + ["SELL"] * 7, [0.7] * 8 + [0.4] * 7, "BUY", "buy_vote_majority", 0.7 * 8 / 15),
        (["SELL"] * 8 + ["BUY"] * 7, [0.7] * 8 + [0.4] * 7, "SELL", "sell_vote_majority", 0.7 * 8 / 15),
        (["BUY"] * 7 + ["SELL"] * 7 + ["HOLD"], [0.9] * 14 + [0.0], "HOLD", "directional_vote_tie", 0.0),
    ),
)
def test_exact_recorded_voting_and_confidence_policy(
    decisions,
    confidences,
    expected,
    reason,
    confidence,
):
    supplied = batch(decisions, confidences)
    original = deepcopy(supplied)

    first = aggregate_v4_strategy_results(supplied)
    second = aggregate_v4_strategy_results(deepcopy(original))

    assert first == second
    assert supplied == original
    assert first["decision"] == expected
    assert first["signal"] == expected
    assert first["reason"] == reason
    assert first["confidence"] == pytest.approx(confidence)
    assert first["received_results"] == 15
    assert first["eligible_results"] == 15
    assert first["execution_enabled"] is False


def test_abstentions_are_excluded_but_retained_in_evidence():
    output = aggregate_v4_strategy_results(
        batch(
            ["ABSTAIN"] * 11 + ["BUY"] * 3 + ["SELL"],
            [0.0] * 11 + [0.9] * 4,
        )
    )

    assert output["decision"] == "BUY"
    assert output["eligible_results"] == 4
    assert output["abstaining_results"] == 11
    assert output["buy_votes"] == 3
    assert output["sell_votes"] == 1
    assert len(output["abstaining_strategies"]) == 11


def test_all_abstentions_fail_closed():
    output = aggregate_v4_strategy_results(
        batch(["ABSTAIN"] * 15, [0.0] * 15)
    )

    assert output["status"] == "abstain"
    assert output["decision"] == "ABSTAIN"
    assert output["reason"] == "all_evaluators_abstained"
    assert output["confidence"] == 0.0
    assert output["abstaining_results"] == 15


def test_unqualified_identity_fails_closed():
    supplied = batch(["BUY"] * 15, [0.8] * 15)
    supplied[0]["strategy_name"] = "Not a V4 Strategy"

    output = aggregate_v4_strategy_results(supplied)

    assert output["status"] == "abstain"
    assert output["decision"] == "ABSTAIN"
    assert output["reason"] == "invalid_evaluator_results"
    assert "unqualified V4 strategy result" in output["error"]


def test_duplicate_v4_identity_fails_closed():
    supplied = batch(["BUY"] * 15, [0.8] * 15)
    supplied[-1]["strategy_name"] = supplied[0]["strategy_name"]

    output = aggregate_v4_strategy_results(supplied)

    assert output["status"] == "abstain"
    assert output["decision"] == "ABSTAIN"
    assert output["reason"] == "duplicate_strategy_results"


def test_real_v4_evaluation_aggregates_without_active_registry():
    supplied = bars()
    original = deepcopy(supplied)

    first = evaluate_and_aggregate_v4(supplied)
    second = evaluate_and_aggregate_v4(supplied)

    assert first == second
    assert supplied == original
    assert first["received_results"] == 15
    assert len(first["strategy_results"]) == 15
    assert first["decision"] in {"BUY", "SELL", "HOLD", "ABSTAIN"}
    assert first["execution_enabled"] is False


def test_healthcheck_preserves_offline_boundary():
    assert healthcheck() == {
        "status": "ok",
        "strategy_count": 15,
        "offline_only": True,
        "registry_activated": False,
        "execution_enabled": False,
    }

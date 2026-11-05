from __future__ import annotations

import pytest

from backend.app.stacks.strategy.allocation_paper_evaluation import (
    AllocationPaperEvaluationError,
    evaluate_fixed_weight_proposal_snapshot,
)
from backend.app.stacks.strategy.allocation_proposal import (
    build_allocation_proposal,
)


def _bars(
    closes: list[float],
    *,
    prefix: str = "2026-01",
) -> list[dict[str, object]]:
    return [
        {
            "timestamp": f"{prefix}-{index + 1:02d}T00:00:00+00:00",
            "close": close,
        }
        for index, close in enumerate(closes)
    ]


def _proposal() -> dict[str, object]:
    return build_allocation_proposal(
        strategy_name="Equal Weight Portfolio",
        universe_symbols=("SPY", "TLT"),
        target_weights={
            "SPY": 0.5,
            "TLT": 0.5,
        },
    )


def _history() -> dict[str, list[dict[str, object]]]:
    return {
        "SPY": _bars([100.0, 110.0, 121.0, 133.1]),
        "TLT": _bars([100.0, 100.0, 100.0, 100.0]),
    }


def test_paper_evaluation_is_non_executable_and_not_a_backtest():
    output = evaluate_fixed_weight_proposal_snapshot(
        proposal=_proposal(),
        universe_bars=_history(),
        rebalance_interval_bars=21,
    )

    assert output["status"] == "ok"
    assert output["strategy_backtest"] is False
    assert output["ending_value"] > 1.0
    assert output["estimated_transaction_cost"] == 0.0
    assert output["broker_order_generation_enabled"] is False
    assert output["execution_enabled"] is False


def test_transaction_cost_reduces_ending_value_when_rebalancing():
    no_cost = evaluate_fixed_weight_proposal_snapshot(
        proposal=_proposal(),
        universe_bars=_history(),
        rebalance_interval_bars=1,
        transaction_cost_bps=0.0,
    )

    with_cost = evaluate_fixed_weight_proposal_snapshot(
        proposal=_proposal(),
        universe_bars=_history(),
        rebalance_interval_bars=1,
        transaction_cost_bps=25.0,
    )

    assert with_cost["estimated_transaction_cost"] > 0.0
    assert with_cost["ending_value"] < no_cost["ending_value"]


def test_unshared_target_history_fails_closed():
    history = {
        "SPY": _bars([100.0, 101.0]),
        "TLT": _bars([100.0, 101.0], prefix="2026-02"),
    }

    with pytest.raises(
        AllocationPaperEvaluationError,
        match="shared observations",
    ):
        evaluate_fixed_weight_proposal_snapshot(
            proposal=_proposal(),
            universe_bars=history,
        )


def test_cash_only_snapshot_is_explicitly_not_evaluable():
    proposal = build_allocation_proposal(
        strategy_name="Trend-Following Asset Allocation",
        universe_symbols=("SPY", "TLT", "GLD"),
        target_weights={},
        cash_weight=1.0,
    )

    output = evaluate_fixed_weight_proposal_snapshot(
        proposal=proposal,
        universe_bars={},
    )

    assert output["status"] == "not_evaluable"
    assert output["reason"] == "cash_only_proposal_snapshot"
    assert output["execution_enabled"] is False

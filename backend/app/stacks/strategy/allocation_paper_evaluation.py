"""Paper-only evaluation of a fixed allocation-proposal snapshot."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from math import isfinite, sqrt
from statistics import pstdev
from typing import Any

from backend.app.stacks.strategy.allocation_proposal import (
    AllocationProposalError,
    build_allocation_proposal,
)

TRADING_DAYS_PER_YEAR = 252


class AllocationPaperEvaluationError(ValueError):
    """Raised when historical input cannot support a paper evaluation."""


def _canonical_proposal(
    proposal: object,
) -> dict[str, object]:
    if not isinstance(proposal, Mapping):
        raise AllocationPaperEvaluationError(
            "proposal must be a mapping"
        )

    try:
        return build_allocation_proposal(
            strategy_name=proposal.get("strategy_name"),
            target_weights=proposal.get("target_weights"),
            universe_symbols=proposal.get("universe_symbols"),
            cash_weight=proposal.get("cash_weight", 0.0),
        )

    except AllocationProposalError as exc:
        raise AllocationPaperEvaluationError(
            f"invalid allocation proposal: {exc}"
        ) from exc


def _close_history(
    universe_bars: object,
    symbols: Sequence[str],
) -> dict[str, dict[str, float]]:
    if not isinstance(universe_bars, Mapping):
        raise AllocationPaperEvaluationError(
            "universe_bars must be a mapping"
        )

    histories: dict[str, dict[str, float]] = {}

    for symbol in symbols:
        bars = universe_bars.get(symbol)

        if (
            isinstance(bars, (str, bytes))
            or not isinstance(bars, Sequence)
            or len(bars) < 2
        ):
            raise AllocationPaperEvaluationError(
                f"insufficient historical bars for {symbol}"
            )

        history: dict[str, float] = {}

        for bar in bars:
            try:
                timestamp = str(bar["timestamp"]).strip()
                close = float(bar["close"])
            except (KeyError, TypeError, ValueError) as exc:
                raise AllocationPaperEvaluationError(
                    f"invalid historical bar for {symbol}"
                ) from exc

            if (
                not timestamp
                or timestamp in history
                or not isfinite(close)
                or close <= 0.0
            ):
                raise AllocationPaperEvaluationError(
                    f"invalid historical bar for {symbol}"
                )

            history[timestamp] = close

        histories[symbol] = history

    return histories


def evaluate_fixed_weight_proposal_snapshot(
    *,
    proposal: object,
    universe_bars: object,
    rebalance_interval_bars: int = 21,
    transaction_cost_bps: float = 0.0,
) -> dict[str, object]:
    """Evaluate a fixed allocation snapshot; this is not a strategy backtest."""

    if (
        isinstance(rebalance_interval_bars, bool)
        or not isinstance(rebalance_interval_bars, int)
        or rebalance_interval_bars < 1
    ):
        raise AllocationPaperEvaluationError(
            "rebalance_interval_bars must be a positive integer"
        )

    try:
        cost_bps = float(transaction_cost_bps)
    except (TypeError, ValueError) as exc:
        raise AllocationPaperEvaluationError(
            "transaction_cost_bps must be numeric"
        ) from exc

    if not isfinite(cost_bps) or cost_bps < 0.0:
        raise AllocationPaperEvaluationError(
            "transaction_cost_bps must be finite and non-negative"
        )

    canonical = _canonical_proposal(proposal)
    target_weights = dict(canonical["target_weights"])
    cash_weight = float(canonical["cash_weight"])

    if not target_weights:
        return {
            "status": "not_evaluable",
            "reason": "cash_only_proposal_snapshot",
            "evaluation_kind":
                "historical_fixed_weight_proposal_snapshot",
            "strategy_backtest": False,
            "proposal": canonical,
            "broker_order_generation_enabled": False,
            "execution_enabled": False,
        }

    symbols = tuple(target_weights)
    histories = _close_history(universe_bars, symbols)

    timestamps = sorted(
        set.intersection(
            *[
                set(history)
                for history in histories.values()
            ]
        )
    )

    if len(timestamps) < 2:
        raise AllocationPaperEvaluationError(
            "target histories have fewer than two shared observations"
        )

    positions = {
        symbol: float(weight)
        for symbol, weight in target_weights.items()
    }
    cash_balance = cash_weight
    ending_value = 1.0
    previous_value = 1.0
    peak_value = 1.0
    max_drawdown = 0.0
    daily_returns: list[float] = []
    rebalance_count = 0
    total_transaction_cost = 0.0
    cost_rate = cost_bps / 10_000.0

    for index in range(1, len(timestamps)):
        previous_timestamp = timestamps[index - 1]
        timestamp = timestamps[index]

        for symbol in symbols:
            positions[symbol] *= (
                histories[symbol][timestamp]
                / histories[symbol][previous_timestamp]
            )

        ending_value = cash_balance + sum(
            positions.values()
        )

        if index % rebalance_interval_bars == 0:
            current_weights = {
                symbol: positions[symbol] / ending_value
                for symbol in symbols
            }
            current_cash_weight = cash_balance / ending_value

            turnover = 0.5 * (
                sum(
                    abs(
                        current_weights[symbol]
                        - target_weights[symbol]
                    )
                    for symbol in symbols
                )
                + abs(current_cash_weight - cash_weight)
            )

            transaction_cost = ending_value * turnover * cost_rate
            ending_value -= transaction_cost
            total_transaction_cost += transaction_cost
            rebalance_count += 1

            positions = {
                symbol: ending_value * float(weight)
                for symbol, weight in target_weights.items()
            }
            cash_balance = ending_value * cash_weight

        daily_returns.append(
            ending_value / previous_value - 1.0
        )
        previous_value = ending_value
        peak_value = max(peak_value, ending_value)
        max_drawdown = min(
            max_drawdown,
            ending_value / peak_value - 1.0,
        )

    periods = len(daily_returns)
    cumulative_return = ending_value - 1.0
    annualized_return = (
        ending_value ** (
            TRADING_DAYS_PER_YEAR / periods
        )
        - 1.0
    )

    annualized_volatility = (
        pstdev(daily_returns)
        * sqrt(TRADING_DAYS_PER_YEAR)
        if len(daily_returns) > 1
        else 0.0
    )

    return {
        "status": "ok",
        "evaluation_kind":
            "historical_fixed_weight_proposal_snapshot",
        "strategy_backtest": False,
        "proposal": canonical,
        "observation_count": len(timestamps),
        "rebalance_interval_bars": rebalance_interval_bars,
        "transaction_cost_bps": cost_bps,
        "rebalance_count": rebalance_count,
        "starting_value": 1.0,
        "ending_value": ending_value,
        "cumulative_return": cumulative_return,
        "annualized_return": annualized_return,
        "annualized_volatility": annualized_volatility,
        "max_drawdown": max_drawdown,
        "estimated_transaction_cost": total_transaction_cost,
        "broker_order_generation_enabled": False,
        "execution_enabled": False,
    }

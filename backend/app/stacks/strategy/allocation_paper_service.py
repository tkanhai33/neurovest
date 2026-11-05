"""Owner-scoped paper evaluation of enabled allocation proposal snapshots."""

from __future__ import annotations

from backend.app.stacks.market_data.multi_symbol_bars import (
    get_daily_bars_for_symbols,
)
from backend.app.stacks.strategy.allocation_paper_evaluation import (
    AllocationPaperEvaluationError,
    evaluate_fixed_weight_proposal_snapshot,
)
from backend.app.stacks.strategy.allocation_service import (
    get_owner_allocation_proposals,
)


class OwnerAllocationPaperEvaluationUnavailableError(RuntimeError):
    """Raised when owner allocation snapshots cannot be paper-evaluated."""


from backend.app.stacks.strategy import (
    allocation_service as _allocation_service,
)


async def get_owner_allocation_paper_evaluations(
    *,
    owner_subject: str,
    rebalance_interval_bars: int = 21,
    transaction_cost_bps: float = 10.0,
) -> dict[str, object]:
    """Evaluate current proposal snapshots; this is not a strategy backtest."""

    try:
        proposals_output = (
            await get_owner_allocation_proposals(
                owner_subject=owner_subject,
            )
        )
    except (
        _allocation_service.
        OwnerAllocationProposalsUnavailableError
    ) as exc:
        return {
            "status": "ok",
            "evaluation_count": 0,
            "evaluations": [],
            "owner_allocation_strategy_applied": False,
            "reason": str(exc),
            "provider_data_read": False,
            "evaluation_kind":
                "historical_fixed_weight_proposal_snapshot",
            "strategy_backtest": False,
            "broker_order_generation_enabled": False,
            "execution_enabled": False,
        }

    if proposals_output.get("proposal_count") == 0:
        return {
            "status": "ok",
            "evaluation_count": 0,
            "evaluations": [],
            "owner_allocation_strategy_applied": False,
            "reason": proposals_output.get("reason"),
            "provider_data_read": False,
            "evaluation_kind":
                "historical_fixed_weight_proposal_snapshot",
            "strategy_backtest": False,
            "broker_order_generation_enabled": False,
            "execution_enabled": False,
        }

    symbols = proposals_output.get("universe_symbols")

    if not isinstance(symbols, list) or len(symbols) < 2:
        raise OwnerAllocationPaperEvaluationUnavailableError(
            "owner proposal universe is unavailable"
        )

    try:
        universe_bars = get_daily_bars_for_symbols(
            symbols,
            limit=253,
        )

        evaluations = [
            evaluate_fixed_weight_proposal_snapshot(
                proposal=proposal,
                universe_bars=universe_bars,
                rebalance_interval_bars=rebalance_interval_bars,
                transaction_cost_bps=transaction_cost_bps,
            )
            for proposal in proposals_output["proposals"]
        ]

    except AllocationPaperEvaluationError as exc:
        raise OwnerAllocationPaperEvaluationUnavailableError(
            f"paper evaluation failed closed: {exc}"
        ) from exc

    except Exception as exc:
        raise OwnerAllocationPaperEvaluationUnavailableError(
            "paper evaluation retrieval failed closed: "
            f"{type(exc).__name__}: {exc}"
        ) from exc

    return {
        "status": "ok",
        "universe_name": proposals_output.get("universe_name"),
        "universe_symbols": symbols,
        "evaluation_count": len(evaluations),
        "evaluations": evaluations,
        "owner_allocation_strategy_applied": True,
        "enabled_allocation_strategy_names": (
            proposals_output.get("enabled_allocation_strategy_names", [])
        ),
        "provider_data_read": True,
        "evaluation_kind":
            "historical_fixed_weight_proposal_snapshot",
        "strategy_backtest": False,
        "broker_order_generation_enabled": False,
        "execution_enabled": False,
    }

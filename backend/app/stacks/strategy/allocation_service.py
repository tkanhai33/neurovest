"""Owner-scoped, read-only allocation-proposal facade."""

from __future__ import annotations

from backend.app.stacks.market_data.multi_symbol_bars import (
    get_daily_bars_for_symbols,
)
from backend.app.stacks.strategy.allocation_proposals_v1 import (
    AllocationProposalUnavailableError as BuilderUnavailableError,
)
from backend.app.stacks.strategy.allocation_registry import (
    ALLOCATION_PROPOSAL_EVALUATORS,
    selected_allocation_proposal_names,
)
from backend.app.stacks.strategy.user_activation.service import (
    DEFAULT_OWNER_UNIVERSE_NAME,
    list_enabled_strategy_names,
    list_owner_universe_symbols,
)


class OwnerAllocationProposalsUnavailableError(RuntimeError):
    """Owner allocation proposals could not be safely assembled."""


async def get_owner_allocation_proposals(
    *,
    owner_subject: str,
) -> dict[str, object]:
    """Return validated proposal-only allocations for an owner's universe."""

    symbols = await list_owner_universe_symbols(
        owner_subject=owner_subject,
        universe_name=DEFAULT_OWNER_UNIVERSE_NAME,
    )

    if len(symbols) < 2:
        raise OwnerAllocationProposalsUnavailableError(
            "owner universe requires at least two symbols"
        )

    enabled_names = await list_enabled_strategy_names(
        owner_subject=owner_subject,
    )

    selected_names = selected_allocation_proposal_names(
        enabled_names,
    )

    if not selected_names:
        return {
            "status": "ok",
            "universe_name": DEFAULT_OWNER_UNIVERSE_NAME,
            "universe_symbols": list(symbols),
            "proposal_count": 0,
            "proposals": [],
            "owner_allocation_strategy_applied": False,
            "reason": "no_enabled_allocation_proposal_strategies",
            "provider_data_read": False,
            "broker_order_generation_enabled": False,
            "execution_enabled": False,
        }

    try:
        universe_bars = get_daily_bars_for_symbols(
            symbols,
            limit=253,
        )

        proposals = [
            ALLOCATION_PROPOSAL_EVALUATORS[name](
                universe_symbols=symbols,
                universe_bars=universe_bars,
            )
            for name in selected_names
        ]

    except BuilderUnavailableError as exc:
        raise OwnerAllocationProposalsUnavailableError(
            f"truthful allocation proposal data unavailable: {exc}"
        ) from exc

    except Exception as exc:
        raise OwnerAllocationProposalsUnavailableError(
            f"allocation proposal retrieval failed closed: "
            f"{type(exc).__name__}: {exc}"
        ) from exc

    return {
        "status": "ok",
        "universe_name": DEFAULT_OWNER_UNIVERSE_NAME,
        "universe_symbols": list(symbols),
        "proposal_count": len(proposals),
        "proposals": proposals,
        "owner_allocation_strategy_applied": True,
        "enabled_allocation_strategy_names": list(selected_names),
        "provider_data_read": True,
        "broker_order_generation_enabled": False,
        "execution_enabled": False,
    }

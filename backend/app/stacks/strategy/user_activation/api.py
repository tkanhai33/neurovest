from __future__ import annotations

from typing import (
    Any,
)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from pydantic import (
    BaseModel,
    Field,
)

from backend.app.stacks.identity_auth.api_dependencies import (
    require_authenticated_principal,
)

from backend.app.stacks.notification.api_router import (
    principal_subject,
)

from backend.app.stacks.strategy.allocation_service import (
    OwnerAllocationProposalsUnavailableError,
    get_owner_allocation_proposals,
)

from backend.app.stacks.strategy.allocation_paper_service import (
    OwnerAllocationPaperEvaluationUnavailableError,
    get_owner_allocation_paper_evaluations,
)

from .service import (
    clear_enabled_strategies,
    list_enabled_reference_strategies,
    list_enabled_strategy_names,
    list_reference_library,
    replace_enabled_strategies,
    list_owner_universe_symbols,
    replace_owner_universe_symbols,
)


router = APIRouter(
    prefix="/api/v1/strategy-library",
    tags=["strategy-library"],
)


class StrategySelectionReplaceRequest(
    BaseModel
):

    strategy_names: list[str] = Field(
        default_factory=list,
        max_length=361,
    )


@router.get("")
async def get_strategy_library(
    market: str | None = None,
    principal=Depends(
        require_authenticated_principal
    ),
) -> dict[str, Any]:

    owner = principal_subject(
        principal
    )

    enabled = set(
        await list_enabled_strategy_names(
            owner_subject=owner,
        )
    )

    strategies = []

    for row in list_reference_library(
        market=market,
    ):

        item = dict(row)

        item["enabled"] = (
            item.get(
                "strategy_name"
            )
            in enabled
        )

        strategies.append(
            item
        )


    return {
        "strategy_count":
            len(
                strategies
            ),

        "catalog_total":
            len(
                list_reference_library()
            ),

        "enabled_count":
            len(
                enabled
            ),

        "market_filter":
            market
            or "all",

        "strategies":
            strategies,
    }


@router.get("/enabled")
async def get_enabled_strategies(
    principal=Depends(
        require_authenticated_principal
    ),
) -> dict[str, Any]:

    owner = principal_subject(
        principal
    )

    strategies = (
        await list_enabled_reference_strategies(
            owner_subject=owner,
        )
    )

    return {
        "enabled_count":
            len(
                strategies
            ),

        "strategies":
            strategies,
    }


@router.put("/enabled")
async def replace_enabled_strategy_selection(
    request: StrategySelectionReplaceRequest,
    principal=Depends(
        require_authenticated_principal
    ),
) -> dict[str, Any]:

    owner = principal_subject(
        principal
    )

    try:

        names = await replace_enabled_strategies(
            owner_subject=owner,
            strategy_names=request.strategy_names,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(
                exc
            ),
        ) from exc


    return {
        "enabled_count":
            len(
                names
            ),

        "strategy_names":
            names,
    }


@router.delete("/enabled")
async def clear_strategy_selection(
    principal=Depends(
        require_authenticated_principal
    ),
) -> dict[str, Any]:

    owner = principal_subject(
        principal
    )

    await clear_enabled_strategies(
        owner_subject=owner,
    )

    return {
        "enabled_count":
            0,

        "strategy_names":
            [],
    }


class StrategyUniverseReplaceRequest(
    BaseModel
):
    symbols: list[str] = Field(
        default_factory=list,
        min_length=2,
        max_length=32,
    )


@router.get("/universe")
async def get_owner_universe(
    principal=Depends(
        require_authenticated_principal
    ),
) -> dict[str, Any]:
    owner = principal_subject(principal)

    symbols = await list_owner_universe_symbols(
        owner_subject=owner,
    )

    return {
        "universe_name": "default",
        "symbol_count": len(symbols),
        "symbols": symbols,
        "execution_enabled": False,
    }


@router.put("/universe")
async def replace_owner_universe(
    request: StrategyUniverseReplaceRequest,
    principal=Depends(
        require_authenticated_principal
    ),
) -> dict[str, Any]:
    owner = principal_subject(principal)

    try:
        symbols = await replace_owner_universe_symbols(
            owner_subject=owner,
            symbols=request.symbols,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return {
        "universe_name": "default",
        "symbol_count": len(symbols),
        "symbols": symbols,
        "execution_enabled": False,
    }


@router.get("/allocation-proposals")
async def get_allocation_proposals(
    principal=Depends(
        require_authenticated_principal
    ),
) -> dict[str, Any]:
    """Return owner-scoped proposal-only portfolio allocations."""

    owner = principal_subject(
        principal
    )

    try:
        return await get_owner_allocation_proposals(
            owner_subject=owner,
        )

    except OwnerAllocationProposalsUnavailableError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc


@router.get("/allocation-proposals/paper-evaluations")
async def get_allocation_paper_evaluations(
    principal=Depends(
        require_authenticated_principal
    ),
) -> dict[str, Any]:
    """Return read-only fixed-weight proposal snapshot evaluations."""

    try:
        return await get_owner_allocation_paper_evaluations(
            owner_subject=principal_subject(principal),
        )
    except OwnerAllocationPaperEvaluationUnavailableError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

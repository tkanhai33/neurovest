from __future__ import annotations

from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from pydantic import (
    BaseModel,
    Field,
)

from backend.app.stacks.db_runtime.database import (
    async_session,
)
from backend.app.stacks.identity_auth.api_dependencies import (
    require_authenticated_principal,
)
from backend.app.stacks.snaptrade.application.connection_service import (
    SnapTradeConnectionRejectedError,
    SnapTradeConnectionService,
    SnapTradeProviderUnavailableError,
)

from backend.app.stacks.snaptrade.application.live_portfolio_sync_service import (
    SnapTradeLivePortfolioSyncService,
)

from backend.app.stacks.snaptrade.application.external_portfolio_inventory import (
    get_external_snaptrade_portfolio,
)

from backend.app.stacks.snaptrade.application.external_balance_inventory import (
    get_external_snaptrade_balances,
)

from backend.app.stacks.snaptrade.application.external_portfolio_value_history import (
    list_external_portfolio_value_history,
    stage_external_portfolio_value_observation,
)



router = APIRouter(
    prefix="/api/v1/snaptrade",
    tags=[
        "snaptrade-readonly",
    ],
)


class ConnectionPortalRequest(
    BaseModel
):
    custom_redirect: str | None = Field(
        default=None,
        max_length=2048,
    )

    dark_mode: bool = True


def principal_subject(
    principal: Any,
) -> str:
    subject = getattr(
        principal,
        "subject",
        None,
    )

    if (
        not isinstance(
            subject,
            str,
        )
        or not subject.strip()
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Authentication required",
        )

    return subject.strip()


def provider_error(
    exc: Exception,
) -> HTTPException:
    if isinstance(
        exc,
        SnapTradeConnectionRejectedError,
    ):
        return HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=str(
                exc
            ),
        )

    return HTTPException(
        status_code=(
            status.HTTP_503_SERVICE_UNAVAILABLE
        ),
        detail=(
            "SnapTrade read-only service is unavailable"
        ),
    )


@router.get(
    "/status",
)
async def get_snaptrade_status(
    principal=Depends(
        require_authenticated_principal
    ),
) -> dict[str, object]:
    owner = principal_subject(
        principal
    )

    try:
        async with async_session() as session:
            service = (
                SnapTradeConnectionService(
                    session
                )
            )

            return await service.get_local_status(
                neurovest_user_id=owner
            )

    except (
        SnapTradeConnectionRejectedError,
        SnapTradeProviderUnavailableError,
    ) as exc:
        raise provider_error(
            exc
        ) from exc


@router.post(
    "/register",
    status_code=(
        status.HTTP_201_CREATED
    ),
)
async def register_snaptrade_owner(
    principal=Depends(
        require_authenticated_principal
    ),
) -> dict[str, object]:
    owner = principal_subject(
        principal
    )

    try:
        async with async_session() as session:
            service = (
                SnapTradeConnectionService(
                    session
                )
            )

            return await service.register_owner(
                neurovest_user_id=owner
            )

    except (
        SnapTradeConnectionRejectedError,
        SnapTradeProviderUnavailableError,
    ) as exc:
        raise provider_error(
            exc
        ) from exc


@router.post(
    "/connection-portal",
)
async def create_snaptrade_connection_portal(
    request: ConnectionPortalRequest,
    principal=Depends(
        require_authenticated_principal
    ),
) -> dict[str, object]:
    owner = principal_subject(
        principal
    )

    try:
        async with async_session() as session:
            service = (
                SnapTradeConnectionService(
                    session
                )
            )

            return (
                await service
                .create_readonly_portal(
                    neurovest_user_id=owner,
                    custom_redirect=(
                        request.custom_redirect
                    ),
                    dark_mode=(
                        request.dark_mode
                    ),
                )
            )

    except (
        SnapTradeConnectionRejectedError,
        SnapTradeProviderUnavailableError,
    ) as exc:
        raise provider_error(
            exc
        ) from exc


@router.post(
    "/synchronize",
)
async def synchronize_snaptrade_status(
    principal=Depends(
        require_authenticated_principal
    ),
) -> dict[str, object]:
    owner = principal_subject(
        principal
    )

    try:
        async with async_session() as session:

            try:
                connection_service = (
                    SnapTradeConnectionService(
                        session
                    )
                )

                connection_state = (
                    await connection_service
                    .synchronize_status(
                        neurovest_user_id=owner
                    )
                )

                portfolio_service = (
                    SnapTradeLivePortfolioSyncService(
                        session
                    )
                )

                synchronized = (
                    await portfolio_service
                    .synchronize(
                        neurovest_user_id=owner
                    )
                )

                await stage_external_portfolio_value_observation(
                    session=session,
                    neurovest_user_id=owner,
                    snapshot=synchronized.snapshot,
                )

                await session.commit()

            except Exception:
                await session.rollback()
                raise

            response = dict(
                connection_state
            )

            response[
                "portfolio_sync"
            ] = {
                "status":
                    "synchronized",

                "read_only":
                    synchronized.snapshot.read_only,

                "trading_enabled":
                    synchronized.snapshot.trading_enabled,

                "order_operations_enabled":
                    synchronized.snapshot.order_operations_enabled,

                "account_count":
                    synchronized.snapshot.account_count,

                "position_count":
                    synchronized.snapshot.position_count,

                "balance_record_count":
                    synchronized.snapshot.balance_record_count,

                "network_request_count":
                    synchronized.snapshot.network_request_count,

                "symbols":
                    list(
                        synchronized.snapshot.symbols
                    ),

                "inserted":
                    synchronized.persistence.inserted,

                "updated":
                    synchronized.persistence.updated,
            }

            return response

    except (
        SnapTradeConnectionRejectedError,
        SnapTradeProviderUnavailableError,
    ) as exc:
        raise provider_error(
            exc
        ) from exc

@router.get(
    "/balances",
)
async def get_snaptrade_external_balances(
    principal=Depends(
        require_authenticated_principal
    ),
) -> dict[str, object]:
    """
    Return the authenticated owner's durable external SnapTrade
    balance inventory.

    This endpoint performs no provider call and has no order or
    execution capability.
    """

    owner = principal_subject(
        principal
    )

    async with async_session() as session:

        return await get_external_snaptrade_balances(
            session=session,
            neurovest_user_id=owner,
        )


@router.get(
    "/portfolio",
)
async def get_snaptrade_external_portfolio(
    principal=Depends(
        require_authenticated_principal
    ),
) -> dict[str, object]:
    """
    Return the authenticated owner's durable external SnapTrade
    portfolio inventory.

    This endpoint performs no provider call and has no order or
    execution capability.
    """

    owner = principal_subject(
        principal
    )

    async with async_session() as session:

        return await get_external_snaptrade_portfolio(
            session=session,
            neurovest_user_id=owner,
        )



@router.get("/portfolio/history")
async def snaptrade_portfolio_value_history(
    limit: int = 1000,
    principal=Depends(
        require_authenticated_principal
    ),
) -> dict[str, object]:

    owner = principal_subject(
        principal
    )

    async with async_session() as session:

        points = (
            await list_external_portfolio_value_history(
                session=session,
                neurovest_user_id=owner,
                limit=limit,
            )
        )

    return {
        "status": "ok",
        "read_only": True,
        "source_provider": "snaptrade",
        "value_formula": "market_value + cash",
        "point_count": len(points),
        "points": points,
    }

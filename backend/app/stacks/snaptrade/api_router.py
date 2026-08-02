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
            service = (
                SnapTradeConnectionService(
                    session
                )
            )

            return (
                await service
                .synchronize_status(
                    neurovest_user_id=owner
                )
            )

    except (
        SnapTradeConnectionRejectedError,
        SnapTradeProviderUnavailableError,
    ) as exc:
        raise provider_error(
            exc
        ) from exc

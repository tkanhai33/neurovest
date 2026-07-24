from __future__ import annotations

from typing import Literal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from backend.app.stacks.identity_auth.admin_read_api_models import (
    AdministrativeIntrospectionResponse,
    AdministrativeSessionDetail,
    AdministrativeSessionListResponse,
    AdministrativeUserDetail,
    AdministrativeUserListResponse,
)
from backend.app.stacks.identity_auth.admin_read_api_models import (
    AdministrativeAccessTokenRevocationDetail,
    AdministrativeAccessTokenRevocationListResponse,
)

from backend.app.stacks.identity_auth.admin_read_dependencies import (
    AdministrativePrincipal,
    get_administrative_read_service,
    require_administrative_principal,
)
from backend.app.stacks.identity_auth.admin_read_models import (
    AdministrativeReadService,
)


router = APIRouter(
    prefix="/api/v1/admin",
    tags=[
        "administrative-read",
    ],
)


@router.get(
    "/introspection",
    response_model=(
        AdministrativeIntrospectionResponse
    ),
)
async def administrative_introspection(
    _principal: AdministrativePrincipal = Depends(
        require_administrative_principal
    ),
) -> AdministrativeIntrospectionResponse:
    return AdministrativeIntrospectionResponse(
        status="available",
        authorization_source=(
            "canonical_identity_database"
        ),
        access_mode="read_only",
        user_read_model="available",
        session_read_model="available",
        mutations_enabled=False,
    )


@router.get(
    "/users",
    response_model=(
        AdministrativeUserListResponse
    ),
)
async def list_administrative_users(
    offset: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    _principal: AdministrativePrincipal = Depends(
        require_administrative_principal
    ),
    service: AdministrativeReadService = Depends(
        get_administrative_read_service
    ),
) -> AdministrativeUserListResponse:
    return await service.list_users(
        offset=offset,
        limit=limit,
    )


@router.get(
    "/users/{user_id}",
    response_model=(
        AdministrativeUserDetail
    ),
)
async def get_administrative_user(
    user_id: str,
    _principal: AdministrativePrincipal = Depends(
        require_administrative_principal
    ),
    service: AdministrativeReadService = Depends(
        get_administrative_read_service
    ),
) -> AdministrativeUserDetail:
    result = await service.get_user(
        user_id=user_id
    )

    if result is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="User not found",
        )

    return result


@router.get(
    "/sessions",
    response_model=(
        AdministrativeSessionListResponse
    ),
)
async def list_administrative_sessions(
    offset: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    user_id: str | None = Query(
        default=None,
    ),
    state: (
        Literal[
            "active",
            "expired",
            "revoked",
            "replaced",
        ]
        | None
    ) = Query(
        default=None,
    ),
    _principal: AdministrativePrincipal = Depends(
        require_administrative_principal
    ),
    service: AdministrativeReadService = Depends(
        get_administrative_read_service
    ),
) -> AdministrativeSessionListResponse:
    return await service.list_sessions(
        offset=offset,
        limit=limit,
        user_id=user_id,
        state=state,
    )


@router.get(
    "/sessions/{session_id}",
    response_model=(
        AdministrativeSessionDetail
    ),
)
async def get_administrative_session(
    session_id: str,
    _principal: AdministrativePrincipal = Depends(
        require_administrative_principal
    ),
    service: AdministrativeReadService = Depends(
        get_administrative_read_service
    ),
) -> AdministrativeSessionDetail:
    result = await service.get_session(
        session_id=session_id
    )

    if result is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Session not found",
        )

    return result

# IQC STAGE 5B-C ADMINISTRATIVE REVOCATION ROUTES
@router.get(
    "/access-token-revocations",
    response_model=(
        AdministrativeAccessTokenRevocationListResponse
    ),
)
async def list_access_token_revocations(
    offset: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    user_id: str | None = Query(
        default=None,
    ),
    state: Literal[
        "active",
        "expired",
    ] | None = Query(
        default=None,
    ),
    _principal: AdministrativePrincipal = Depends(
        require_administrative_principal
    ),
    service: AdministrativeReadService = Depends(
        get_administrative_read_service
    ),
) -> AdministrativeAccessTokenRevocationListResponse:
    return await service.list_access_token_revocations(
        offset=offset,
        limit=limit,
        user_id=user_id,
        state=state,
    )


@router.get(
    "/access-token-revocations/{revocation_id}",
    response_model=(
        AdministrativeAccessTokenRevocationDetail
    ),
)
async def get_access_token_revocation(
    revocation_id: str,
    _principal: AdministrativePrincipal = Depends(
        require_administrative_principal
    ),
    service: AdministrativeReadService = Depends(
        get_administrative_read_service
    ),
) -> AdministrativeAccessTokenRevocationDetail:
    result = await service.get_access_token_revocation(
        revocation_id=revocation_id
    )

    if result is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Access-token revocation record "
                "not found"
            ),
        )

    return result

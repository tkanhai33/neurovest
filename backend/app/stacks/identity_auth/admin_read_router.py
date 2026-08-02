from __future__ import annotations

from typing import Literal


from pydantic import (
    BaseModel,
    Field,
)

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

from backend.app.stacks.execution.execution_control import (
    ExecutionControlError,
    InvalidOperatingModeTransition,
    OperatingMode,
    execution_control,
)

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.stacks.db_runtime.database import (
    async_session,
)
from backend.app.stacks.journal_ledger.decision_audit_query_facade import (
    DecisionAuditQueryFacade,
)
from backend.app.stacks.journal_ledger.decision_audit_service import (
    build_decision_audit_service,
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
        default=500,
        ge=1,
        le=500,
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

@router.get(
    "/audit",
    response_model=dict,
)
async def list_administrative_audit_records(
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
    ),
    _principal: AdministrativePrincipal = Depends(
        require_administrative_principal
    ),
) -> dict:
    """
    Return recent immutable decision-audit records.

    This route is administrative, authenticated, and read-only.
    It exposes serialized DTOs only and cannot mutate ledger records.
    """

    async with async_session() as session:
        audit_service = build_decision_audit_service(
            session
        )

        facade = DecisionAuditQueryFacade(
            audit_service
        )

        records = await facade.list_recent(
            limit=limit
        )

        return {
            "status": "available",
            "access_mode": "read_only",
            "mutations_enabled": False,
            "count": len(records),
            "records": [
                record.to_dict()
                for record in records
            ],
        }

class ExecutionModeTransitionRequest(
    BaseModel
):
    mode: OperatingMode

    reason: str = Field(
        min_length=3,
        max_length=500,
    )


class EmergencyStopRequest(
    BaseModel
):
    reason: str = Field(
        min_length=3,
        max_length=500,
    )


def administrative_actor(
    principal: AdministrativePrincipal,
) -> str:
    for attribute in (
        "subject",
        "user_id",
        "principal_id",
        "email",
    ):
        value = getattr(
            principal,
            attribute,
            None,
        )

        if isinstance(
            value,
            str,
        ) and value.strip():
            return value.strip()

    return "authenticated-administrator"


@router.get(
    "/execution-control",
    response_model=dict,
)
async def get_execution_control_status(
    _principal: AdministrativePrincipal = Depends(
        require_administrative_principal
    ),
) -> dict:
    """
    Return the current server-authoritative execution mode.

    This route is administrative and read-only.
    """

    return {
        "status": "available",
        "control": (
            execution_control.snapshot_dict()
        ),
    }


@router.post(
    "/execution-control/transition",
    response_model=dict,
)
async def transition_execution_control(
    request: ExecutionModeTransitionRequest,
    principal: AdministrativePrincipal = Depends(
        require_administrative_principal
    ),
) -> dict:
    """
    Apply one validated operating-mode transition.

    Invalid transitions fail closed and do not change persisted state.
    """

    try:
        snapshot = execution_control.transition(
            request.mode,
            actor=administrative_actor(
                principal
            ),
            reason=request.reason,
        )

    except (
        InvalidOperatingModeTransition,
        ExecutionControlError,
        ValueError,
    ) as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Operating-mode transition was rejected"
            ),
        ) from exc

    return {
        "status": "transitioned",
        "control": {
            "mode": snapshot.mode,
            "revision": snapshot.revision,
            "updated_at": snapshot.updated_at,
            "reason": snapshot.reason,
            "actor": snapshot.actor,
            "paper_execution_enabled": (
                snapshot.paper_execution_enabled
            ),
            "live_execution_enabled": (
                snapshot.live_execution_enabled
            ),
            "emergency_stop_active": (
                snapshot.emergency_stop_active
            ),
        },
    }


@router.post(
    "/execution-control/emergency-stop",
    response_model=dict,
)
async def activate_execution_emergency_stop(
    request: EmergencyStopRequest,
    principal: AdministrativePrincipal = Depends(
        require_administrative_principal
    ),
) -> dict:
    """
    Immediately activate the persistent emergency-stop state.
    """

    try:
        snapshot = execution_control.emergency_stop(
            actor=administrative_actor(
                principal
            ),
            reason=request.reason,
        )

    except ExecutionControlError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Emergency stop could not be activated"
            ),
        ) from exc

    return {
        "status": "emergency_stop_active",
        "control": {
            "mode": snapshot.mode,
            "revision": snapshot.revision,
            "updated_at": snapshot.updated_at,
            "reason": snapshot.reason,
            "actor": snapshot.actor,
            "paper_execution_enabled": (
                snapshot.paper_execution_enabled
            ),
            "live_execution_enabled": (
                snapshot.live_execution_enabled
            ),
            "emergency_stop_active": (
                snapshot.emergency_stop_active
            ),
        },
    }


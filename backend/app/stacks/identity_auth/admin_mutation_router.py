from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.app.stacks.identity_auth.admin_mutation_api_models import (
    AdministrativeDeleteResponse,
    AdministrativeMutationResponse,
    AdministrativeTemporaryPasswordResponse,
)
from backend.app.stacks.identity_auth.admin_mutation_dependencies import (
    get_administrative_user_mutation_service,
)
from backend.app.stacks.identity_auth.admin_mutation_service import (
    AdministrativeUserMutationService,
)
from backend.app.stacks.identity_auth.admin_read_dependencies import (
    AdministrativePrincipal,
    require_administrative_principal,
)


router = APIRouter(
    prefix="/api/v1/admin/users",
    tags=[
        "administrative-user-management",
    ],
)


@router.post(
    "/{user_id}/require-password-reset",
    response_model=AdministrativeMutationResponse,
)
async def require_password_reset(
    user_id: str,
    principal: AdministrativePrincipal = Depends(
        require_administrative_principal
    ),
    service: AdministrativeUserMutationService = Depends(
        get_administrative_user_mutation_service
    ),
) -> AdministrativeMutationResponse:
    return await service.require_password_reset(
        principal=principal,
        user_id=user_id,
    )


@router.post(
    "/{user_id}/temporary-password",
    response_model=(
        AdministrativeTemporaryPasswordResponse
    ),
)
async def issue_temporary_password(
    user_id: str,
    principal: AdministrativePrincipal = Depends(
        require_administrative_principal
    ),
    service: AdministrativeUserMutationService = Depends(
        get_administrative_user_mutation_service
    ),
) -> AdministrativeTemporaryPasswordResponse:
    return await service.issue_temporary_password(
        principal=principal,
        user_id=user_id,
    )


@router.post(
    "/{user_id}/disable",
    response_model=AdministrativeMutationResponse,
)
async def disable_account(
    user_id: str,
    principal: AdministrativePrincipal = Depends(
        require_administrative_principal
    ),
    service: AdministrativeUserMutationService = Depends(
        get_administrative_user_mutation_service
    ),
) -> AdministrativeMutationResponse:
    return await service.disable_account(
        principal=principal,
        user_id=user_id,
    )


@router.post(
    "/{user_id}/enable",
    response_model=AdministrativeMutationResponse,
)
async def enable_account(
    user_id: str,
    principal: AdministrativePrincipal = Depends(
        require_administrative_principal
    ),
    service: AdministrativeUserMutationService = Depends(
        get_administrative_user_mutation_service
    ),
) -> AdministrativeMutationResponse:
    return await service.enable_account(
        principal=principal,
        user_id=user_id,
    )


@router.delete(
    "/{user_id}",
    response_model=AdministrativeDeleteResponse,
)
async def delete_account(
    user_id: str,
    principal: AdministrativePrincipal = Depends(
        require_administrative_principal
    ),
    service: AdministrativeUserMutationService = Depends(
        get_administrative_user_mutation_service
    ),
) -> AdministrativeDeleteResponse:
    return await service.delete_account(
        principal=principal,
        user_id=user_id,
    )

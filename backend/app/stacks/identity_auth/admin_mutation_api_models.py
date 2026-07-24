from __future__ import annotations

from pydantic import BaseModel, Field


class AdministrativeMutationResponse(BaseModel):
    status: str
    action: str
    user_id: str
    sessions_revoked: int = Field(
        default=0,
        ge=0,
    )


class AdministrativeTemporaryPasswordResponse(
    AdministrativeMutationResponse
):
    temporary_password: str = Field(
        min_length=16,
    )
    must_change_password: bool = True


class AdministrativeDeleteResponse(BaseModel):
    status: str
    action: str
    user_id: str
    deleted: bool

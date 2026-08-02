from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class AdministrativeUserSummary(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    user_id: str = Field(
        min_length=1,
    )

    email: str = Field(
        min_length=1,
    )

    role: str = Field(
        min_length=1,
    )

    status: str = Field(
        min_length=1,
    )

    is_active: bool
    must_change_password: bool

    created_at: datetime | None = None
    updated_at: datetime | None = None


class AdministrativeUserDetail(
    AdministrativeUserSummary
):
    active_session_count: int = Field(
        ge=0,
    )

    total_session_count: int = Field(
        ge=0,
    )


class AdministrativeSessionSummary(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    session_id: str = Field(
        min_length=1,
    )

    user_id: str = Field(
        min_length=1,
    )

    state: str = Field(
        min_length=1,
    )

    issued_at: datetime | None = None
    expires_at: datetime | None = None
    revoked_at: datetime | None = None

    replaced: bool = False


class AdministrativeSessionDetail(
    AdministrativeSessionSummary
):
    token_family_id: str | None = None
    replacement_session_id: str | None = None


class AdministrativeUserListResponse(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    items: tuple[
        AdministrativeUserSummary,
        ...,
    ]

    offset: int = Field(
        ge=0,
    )

    limit: int = Field(
        ge=1,
        le=500,
    )

    returned: int = Field(
        ge=0,
    )


    total: int = Field(
        ge=0,
    )

class AdministrativeSessionListResponse(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    items: tuple[
        AdministrativeSessionSummary,
        ...,
    ]

    offset: int = Field(
        ge=0,
    )

    limit: int = Field(
        ge=1,
        le=100,
    )

    returned: int = Field(
        ge=0,
    )


class AdministrativeIntrospectionResponse(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    status: str
    authorization_source: str
    access_mode: str
    user_read_model: str
    session_read_model: str
    mutations_enabled: bool

# IQC STAGE 5B-C ACCESS-TOKEN REVOCATION MODELS
class AdministrativeAccessTokenRevocationSummary(
    BaseModel
):
    id: str
    user_id: str
    issued_at: datetime
    expires_at: datetime
    revoked_at: datetime
    reason: str
    created_at: datetime
    state: Literal[
        "active",
        "expired",
    ]


class AdministrativeAccessTokenRevocationDetail(
    AdministrativeAccessTokenRevocationSummary
):
    pass


class AdministrativeAccessTokenRevocationListResponse(
    BaseModel
):
    offset: int
    limit: int
    total: int
    records: list[
        AdministrativeAccessTokenRevocationSummary
    ]

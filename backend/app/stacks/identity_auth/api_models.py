from __future__ import annotations

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class RegistrationApiRequest(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    email: str = Field(
        min_length=3,
        max_length=320,
    )

    password: str = Field(
        min_length=12,
        max_length=1024,
    )

    display_name: str | None = Field(
        default=None,
        max_length=100,
    )


class LoginApiRequest(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    email: str = Field(
        min_length=3,
        max_length=320,
    )

    password: str = Field(
        min_length=1,
        max_length=1024,
    )


class RegistrationApiResponse(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    status: str = "registered"


class LoginTokenApiResponse(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    token_type: str = "bearer"

    access_token: str = Field(
        min_length=1,
    )

    refresh_token: str = Field(
        min_length=1,
    )

    password_change_required: bool | None = None


class ChangeRequiredPasswordApiRequest(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    current_password: str = Field(
        min_length=1,
        max_length=1024,
    )

    new_password: str = Field(
        min_length=12,
        max_length=1024,
    )


class ChangeRequiredPasswordApiResponse(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    status: str = "password_changed"

    revoked_sessions: int = Field(
        ge=0,
    )


class RefreshTokenApiRequest(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    refresh_token: str = Field(
        min_length=1,
        max_length=8192,
    )


class LogoutApiRequest(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    refresh_token: str = Field(
        min_length=1,
        max_length=8192,
    )


class SessionTokenApiResponse(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    token_type: str = "bearer"

    access_token: str = Field(
        min_length=1,
    )

    refresh_token: str = Field(
        min_length=1,
    )


class SessionActionApiResponse(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    status: str


class LogoutAllApiResponse(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    status: str = "logged_out_all"

    revoked_sessions: int = Field(
        ge=0,
    )

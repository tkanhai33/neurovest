from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import (
    Awaitable,
    Callable,
    Protocol,
)


class RegistrationRejectedError(
    Exception
):
    """Generic fail-closed registration rejection."""


class AuthenticationRejectedError(
    Exception
):
    """Generic fail-closed authentication rejection."""


class AuthenticationDependencyError(
    Exception
):
    """Raised when an injected auth dependency fails."""


@dataclass(frozen=True)
class RegistrationCommand:
    email: str
    password: str
    display_name: str | None = None


@dataclass(frozen=True)
class RegisteredIdentity:
    user_id: str
    email_normalized: str
    status: str


@dataclass(frozen=True)
class LoginCommand:
    email: str
    password: str


@dataclass(frozen=True)
class IssuedServiceToken:
    token: str
    token_id: str
    issued_at: datetime
    expires_at: datetime


@dataclass(frozen=True)
class AuthenticationTokenPair:
    access_token: str
    refresh_token: str
    token_type: str
    access_expires_at: datetime
    refresh_expires_at: datetime
    password_change_required: bool | None = None


PasswordHashFunction = Callable[
    [
        str,
    ],
    str,
]


PasswordVerifyFunction = Callable[
    [
        str,
        str,
    ],
    bool,
]


RefreshTokenHashFunction = Callable[
    [
        str,
    ],
    str,
]


class ServiceTokenIssuer(
    Protocol
):
    async def issue_access_token(
        self,
        *,
        subject: str,
    ) -> IssuedServiceToken:
        ...

    async def issue_refresh_token(
        self,
        *,
        subject: str,
    ) -> IssuedServiceToken:
        ...


CommitFunction = Callable[
    [],
    Awaitable[
        None
    ],
]


RollbackFunction = Callable[
    [],
    Awaitable[
        None
    ],
]


@dataclass(frozen=True)
class SessionRefreshCommand:
    refresh_token: str


@dataclass(frozen=True)
class SessionLogoutCommand:
    refresh_token: str


@dataclass(frozen=True)
class SessionLogoutAllCommand:
    user_id: str

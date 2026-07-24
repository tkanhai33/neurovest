from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping


ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


@dataclass(frozen=True)
class JWTPolicy:
    issuer: str = "neurovest"
    audience: str = "neurovest-api"
    algorithm: str = "HS256"
    access_token_seconds: int = 900
    refresh_token_seconds: int = 604800
    clock_skew_seconds: int = 0

    def __post_init__(self) -> None:
        if self.algorithm != "HS256":
            raise ValueError(
                "Only HS256 is approved in JWT policy v1"
            )

        if self.access_token_seconds <= 0:
            raise ValueError(
                "Access-token lifetime must be positive"
            )

        if self.refresh_token_seconds <= (
            self.access_token_seconds
        ):
            raise ValueError(
                "Refresh-token lifetime must exceed "
                "access-token lifetime"
            )

        if self.clock_skew_seconds < 0:
            raise ValueError(
                "Clock skew cannot be negative"
            )


DEFAULT_JWT_POLICY = JWTPolicy()


@dataclass(frozen=True)
class TokenClaims:
    subject: str
    token_type: str
    token_id: str
    issuer: str
    audience: str
    issued_at: int
    not_before: int
    expires_at: int
    extra: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "extra",
            MappingProxyType(
                dict(
                    self.extra
                )
            ),
        )

        if not self.subject:
            raise ValueError(
                "Token subject cannot be empty"
            )

        if self.token_type not in {
            ACCESS_TOKEN_TYPE,
            REFRESH_TOKEN_TYPE,
        }:
            raise ValueError(
                "Unsupported token type"
            )

        if not self.token_id:
            raise ValueError(
                "Token identifier cannot be empty"
            )

        if self.expires_at <= self.issued_at:
            raise ValueError(
                "Token expiration must follow issuance"
            )


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    token_scheme: str = "Bearer"


@dataclass(frozen=True)
class AuthenticatedPrincipal:
    subject: str
    token_id: str
    claims: Mapping[str, Any]
    issued_at: int | None = None
    expires_at: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "claims",
            MappingProxyType(
                dict(
                    self.claims
                )
            ),
        )

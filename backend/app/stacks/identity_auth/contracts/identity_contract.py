from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class UserRole(StrEnum):
    USER = "user"
    ADMIN = "admin"
    DEVELOPER = "developer"


class AccountStatus(StrEnum):
    ACTIVE = "active"
    DISABLED = "disabled"


@dataclass(frozen=True)
class IdentityUserContract:
    id: str
    email: str
    role: UserRole
    status: AccountStatus


@dataclass(frozen=True)
class IdentityAuthSkeletonStatus:
    stack: str = "identity_auth"
    phase: str = "phase_2_skeleton"
    login_implemented: bool = False
    jwt_implemented: bool = False
    password_auth_implemented: bool = False
    business_logic_implemented: bool = False

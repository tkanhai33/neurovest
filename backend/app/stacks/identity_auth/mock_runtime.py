from __future__ import annotations

from typing import Any, Mapping

import hashlib
import hmac
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from backend.app.stacks.identity_auth.login_service import (
    LoginService,
)

from backend.app.stacks.identity_auth.registration_service import (
    RegistrationService,
)

from backend.app.stacks.identity_auth.service_contracts import (
    IssuedServiceToken,
)


@dataclass
class MockIdentityUser:
    id: str
    email_normalized: str
    password_hash: str
    display_name: str | None = None
    status: str = "active"
    is_active: bool = True

    role: str = "user"
    subscription_tier: str = "free"


@dataclass
class MockRefreshSession:
    user_id: str
    token_id: str
    token_hash: str
    issued_at: datetime
    expires_at: datetime


class MockIdentityUserRepository:
    def __init__(self) -> None:
        self.users_by_email: dict[
            str,
            MockIdentityUser,
        ] = {}

    async def get_by_email(
        self,
        email: str,
    ) -> MockIdentityUser | None:
        return self.users_by_email.get(
            email
        )

    async def create(
        self,
        *,
        email: str,
        password_hash: str,
        display_name: str | None = None,
    ) -> MockIdentityUser:
        if email in self.users_by_email:
            raise RuntimeError(
                "Duplicate identity"
            )

        user = MockIdentityUser(
            id=str(
                uuid4()
            ),
            email_normalized=email,
            password_hash=password_hash,
            display_name=display_name,
        )

        self.users_by_email[
            email
        ] = user

        return user


class MockRefreshSessionRepository:
    def __init__(self) -> None:
        self.sessions: list[
            MockRefreshSession
        ] = []

        self.fail_create = False

    async def create(
        self,
        *,
        user_id: str,
        token_id: str,
        token_hash: str,
        issued_at: datetime,
        expires_at: datetime,
    ) -> MockRefreshSession:
        if self.fail_create:
            raise RuntimeError(
                "Mock refresh-session failure"
            )

        record = MockRefreshSession(
            user_id=user_id,
            token_id=token_id,
            token_hash=token_hash,
            issued_at=issued_at,
            expires_at=expires_at,
        )

        self.sessions.append(
            record
        )

        return record


class MockTransactionBoundary:
    def __init__(self) -> None:
        self.commit_count = 0
        self.rollback_count = 0

        self.fail_commit = False

    async def commit(self) -> None:
        if self.fail_commit:
            raise RuntimeError(
                "Mock commit failure"
            )

        self.commit_count += 1

    async def rollback(self) -> None:
        self.rollback_count += 1


class MockServiceTokenIssuer:
    def __init__(self) -> None:
        self.fail_access = False
        self.fail_refresh = False

        self.access_issued = 0
        self.refresh_issued = 0

    async def issue_access_token(
        self,
        *,
        subject: str,
            extra_claims: Mapping[str, Any] | None = None,
) -> IssuedServiceToken:
        self.last_access_extra_claims = dict(
            extra_claims or {}
        )

        if self.fail_access:
            raise RuntimeError(
                "Mock access-token failure"
            )

        self.access_issued += 1

        now = datetime.now(
            UTC
        )

        return IssuedServiceToken(
            token=(
                f"mock-access-{subject}-"
                f"{self.access_issued}"
            ),
            token_id=(
                f"mock-access-id-"
                f"{self.access_issued}"
            ),
            issued_at=now,
            expires_at=(
                now
                + timedelta(
                    minutes=15
                )
            ),
        )

    async def issue_refresh_token(
        self,
        *,
        subject: str,
            extra_claims: Mapping[str, Any] | None = None,
) -> IssuedServiceToken:
        self.last_refresh_extra_claims = dict(
            extra_claims or {}
        )

        if self.fail_refresh:
            raise RuntimeError(
                "Mock refresh-token failure"
            )

        self.refresh_issued += 1

        now = datetime.now(
            UTC
        )

        return IssuedServiceToken(
            token=(
                f"mock-refresh-{subject}-"
                f"{self.refresh_issued}"
            ),
            token_id=(
                f"mock-refresh-id-"
                f"{self.refresh_issued}"
            ),
            issued_at=now,
            expires_at=(
                now
                + timedelta(
                    days=7
                )
            ),
        )


def mock_hash_password(
    password: str,
) -> str:
    if not password:
        raise ValueError(
            "Password cannot be empty"
        )

    digest = hashlib.sha256(
        (
            "mock-password-pepper:"
            + password
        ).encode(
            "utf-8"
        )
    ).hexdigest()

    return (
        "mock-sha256$"
        + digest
    )


def mock_verify_password(
    password: str,
    encoded_hash: str,
) -> bool:
    observed = mock_hash_password(
        password
    )

    return hmac.compare_digest(
        observed,
        encoded_hash,
    )


def mock_hash_refresh_token(
    token: str,
) -> str:
    if not token:
        raise ValueError(
            "Refresh token cannot be empty"
        )

    return hashlib.sha256(
        (
            "mock-refresh-pepper:"
            + token
        ).encode(
            "utf-8"
        )
    ).hexdigest()


class MockAuthenticationRuntime:
    def __init__(self) -> None:
        self.users = (
            MockIdentityUserRepository()
        )

        self.refresh_sessions = (
            MockRefreshSessionRepository()
        )

        self.registration_transaction = (
            MockTransactionBoundary()
        )

        self.login_transaction = (
            MockTransactionBoundary()
        )

        self.token_issuer = (
            MockServiceTokenIssuer()
        )

        self.registration = RegistrationService(
            user_repository=self.users,
            hash_password=mock_hash_password,
            commit=(
                self.registration_transaction.commit
            ),
            rollback=(
                self.registration_transaction.rollback
            ),
        )

        self.login = LoginService(
            user_repository=self.users,
            refresh_session_repository=(
                self.refresh_sessions
            ),
            verify_password=(
                mock_verify_password
            ),
            token_issuer=self.token_issuer,
            hash_refresh_token=(
                mock_hash_refresh_token
            ),
            dummy_password_hash=(
                mock_hash_password(
                    "mock-dummy-password"
                )
            ),
            commit=(
                self.login_transaction.commit
            ),
            rollback=(
                self.login_transaction.rollback
            ),
        )

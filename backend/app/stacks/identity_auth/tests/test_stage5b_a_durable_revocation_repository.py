from __future__ import annotations

from datetime import (
    UTC,
    datetime,
    timedelta,
)

import pytest

from backend.app.stacks.identity_auth.access_token_revocation_models import (
    IdentityAccessTokenRevocation,
)
from backend.app.stacks.identity_auth.access_token_revocation_repository import (
    AccessTokenRevocationRepository,
)


def test_revocation_model_exposes_only_safe_fields() -> None:
    columns = {
        column.name
        for column in (
            IdentityAccessTokenRevocation.__table__.columns
        )
    }

    assert columns == {
        "id",
        "token_id",
        "user_id",
        "issued_at",
        "expires_at",
        "revoked_at",
        "reason",
        "created_at",
    }

    forbidden = {
        "token",
        "raw_token",
        "jwt",
        "access_token",
        "refresh_token",
        "token_hash",
        "password",
        "password_hash",
    }

    assert not (
        columns
        & forbidden
    )


def test_revocation_token_id_is_unique() -> None:
    table = (
        IdentityAccessTokenRevocation.__table__
    )

    unique_columns = {
        tuple(
            column.name
            for column in constraint.columns
        )
        for constraint in table.constraints
        if constraint.__class__.__name__
        == "UniqueConstraint"
    }

    assert (
        "token_id",
    ) in unique_columns


@pytest.mark.parametrize(
    "token_id,user_id,reason",
    [
        (
            "",
            "user-1",
            "logout",
        ),
        (
            "token-1",
            "",
            "logout",
        ),
        (
            "token-1",
            "user-1",
            "",
        ),
    ],
)
@pytest.mark.asyncio
async def test_repository_rejects_invalid_identifiers(
    token_id: str,
    user_id: str,
    reason: str,
) -> None:
    class SessionStub:
        pass

    repository = AccessTokenRevocationRepository(
        SessionStub()  # type: ignore[arg-type]
    )

    now = datetime.now(
        UTC
    )

    with pytest.raises(
        ValueError
    ):
        await repository.revoke(
            token_id=token_id,
            user_id=user_id,
            issued_at=now,
            expires_at=(
                now
                + timedelta(
                    minutes=15
                )
            ),
            reason=reason,
        )


@pytest.mark.asyncio
async def test_repository_rejects_invalid_lifetime() -> None:
    class SessionStub:
        pass

    repository = AccessTokenRevocationRepository(
        SessionStub()  # type: ignore[arg-type]
    )

    now = datetime.now(
        UTC
    )

    with pytest.raises(
        ValueError,
        match="expiry",
    ):
        await repository.revoke(
            token_id="token-1",
            user_id="user-1",
            issued_at=now,
            expires_at=now,
            reason="logout",
        )

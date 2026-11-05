"""
NeuroVest F12-R3O credential-generation candidate.

A generation is incremented atomically when credentials change.

Integration requirements:
- Password update, refresh revocation and generation increment
  must share one database transaction.
- New access/refresh tokens must carry the current generation.
- Authenticated access must compare its generation with the
  current generation from the database.
- Refresh must check generation before issuing new tokens.
- No independent commit occurs inside these functions.

STAGED ONLY. Do not import into the live authentication runtime
until the migration and complete issuance/verification wiring
have passed integration tests.
"""

from fastapi import HTTPException
from sqlalchemy import (
    BigInteger,
    Column,
    ForeignKey,
    MetaData,
    String,
    Table,
    select,
)
from sqlalchemy.dialects.postgresql import insert

metadata = MetaData()

credential_generations = Table(
    "identity_credential_generations",
    metadata,
    Column(
        "user_id",
        String(36),
        ForeignKey(
            "identity_users.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),
    Column(
        "generation",
        BigInteger,
        nullable=False,
    ),
)

CLAIM_NAME = "credential_generation"
MAX_GENERATION = 2**63 - 1


class CredentialGenerationError(Exception):
    pass


def validate_generation(value):
    if (
        type(value) is not int
        or value < 0
        or value > MAX_GENERATION
    ):
        raise CredentialGenerationError(
            "Invalid credential generation"
        )
    return value


def require_owner(user_id):
    if (
        not isinstance(user_id, str)
        or not user_id.strip()
        or len(user_id) > 36
    ):
        raise CredentialGenerationError(
            "Invalid account identifier"
        )
    return user_id


async def current_generation(session, user_id):
    owner = require_owner(user_id)

    result = await session.execute(
        select(
            credential_generations.c.generation
        ).where(
            credential_generations.c.user_id == owner
        )
    )

    value = result.scalar_one_or_none()

    # Accounts predating this feature begin at generation 0.
    if value is None:
        return 0

    return validate_generation(value)


async def increment_generation(session, user_id):
    """
    Must be called inside the password-change transaction.

    PostgreSQL resolves concurrent increments atomically
    using INSERT ... ON CONFLICT DO UPDATE.
    """
    owner = require_owner(user_id)

    statement = insert(
        credential_generations
    ).values(
        user_id=owner,
        generation=1,
    )

    statement = statement.on_conflict_do_update(
        index_elements=[
            credential_generations.c.user_id
        ],
        set_={
            "generation":
                credential_generations.c.generation + 1
        },
    ).returning(
        credential_generations.c.generation
    )

    result = await session.execute(statement)
    return validate_generation(result.scalar_one())


def token_generation(claims):
    if not isinstance(claims, dict):
        try:
            claims = dict(claims)
        except (TypeError, ValueError):
            raise CredentialGenerationError(
                "Invalid token claims"
            ) from None

    value = claims.get(CLAIM_NAME)

    if value is None:
        # Transition policy:
        # Legacy tokens are generation 0 only.
        # Once credentials change, they must be rejected.
        return 0

    return validate_generation(value)


async def assert_token_generation(
    session,
    *,
    user_id,
    claims,
):
    try:
        expected = await current_generation(
            session,
            user_id,
        )
        presented = token_generation(claims)
    except CredentialGenerationError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
        ) from None

    if presented != expected:
        raise HTTPException(
            status_code=401,
            detail="Session invalidated; sign in again",
        )

    return expected


def claims_for_issuance(
    existing_claims,
    generation,
):
    validated = validate_generation(generation)

    claims = dict(existing_claims)

    # Prevent an untrusted caller from supplying a different
    # generation via preexisting extra claims.
    claims.pop(CLAIM_NAME, None)
    claims[CLAIM_NAME] = validated

    return claims

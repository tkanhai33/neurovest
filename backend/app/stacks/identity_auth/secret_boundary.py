from __future__ import annotations

import os

from backend.app.stacks.identity_auth.errors import (
    MissingSecretError,
)


JWT_SECRET_ENV = "NEUROVEST_JWT_SECRET"

MINIMUM_SECRET_BYTES = 32


def load_jwt_secret() -> bytes:
    """
    Load the JWT signing secret through the environment-only
    identity_auth boundary.

    The secret is never logged, persisted, cached globally,
    or returned in diagnostic output.
    """

    value = os.getenv(
        JWT_SECRET_ENV
    )

    if value is None:
        raise MissingSecretError(
            "JWT secret is not configured"
        )

    encoded = value.encode(
        "utf-8"
    )

    if len(encoded) < MINIMUM_SECRET_BYTES:
        raise MissingSecretError(
            "JWT secret does not satisfy the minimum length"
        )

    return encoded

from __future__ import annotations

import pytest

from backend.app.stacks.identity_auth.errors import (
    InvalidPasswordHashError,
)

from backend.app.stacks.identity_auth.passwords import (
    hash_password,
    verify_password,
)


def test_password_hash_is_salted_and_not_plaintext() -> None:
    password = "correct horse battery staple"

    first = hash_password(
        password
    )

    second = hash_password(
        password
    )

    assert first != second
    assert password not in first
    assert first.startswith(
        "scrypt$"
    )


def test_password_verification_accepts_correct_password() -> None:
    encoded = hash_password(
        "valid-password"
    )

    assert verify_password(
        "valid-password",
        encoded,
    ) is True


def test_password_verification_rejects_wrong_password() -> None:
    encoded = hash_password(
        "valid-password"
    )

    assert verify_password(
        "wrong-password",
        encoded,
    ) is False


def test_empty_password_is_rejected() -> None:
    with pytest.raises(
        ValueError
    ):
        hash_password(
            ""
        )


def test_malformed_password_hash_is_rejected() -> None:
    with pytest.raises(
        InvalidPasswordHashError
    ):
        verify_password(
            "password",
            "not-a-valid-hash",
        )

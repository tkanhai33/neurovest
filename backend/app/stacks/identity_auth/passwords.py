from __future__ import annotations

import base64
import hashlib
import hmac
import os

from backend.app.stacks.identity_auth.errors import (
    InvalidPasswordHashError,
)


PASSWORD_SCHEME = "scrypt"

SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1
SCRYPT_DKLEN = 32
SALT_BYTES = 16


def _derive(
    password: str,
    salt: bytes,
    *,
    n: int,
    r: int,
    p: int,
    dklen: int,
) -> bytes:
    if not isinstance(
        password,
        str,
    ):
        raise TypeError(
            "Password must be a string"
        )

    if not password:
        raise ValueError(
            "Password cannot be empty"
        )

    return hashlib.scrypt(
        password.encode(
            "utf-8"
        ),
        salt=salt,
        n=n,
        r=r,
        p=p,
        dklen=dklen,
    )


def hash_password(
    password: str,
) -> str:
    salt = os.urandom(
        SALT_BYTES
    )

    derived = _derive(
        password,
        salt,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        dklen=SCRYPT_DKLEN,
    )

    salt_text = base64.urlsafe_b64encode(
        salt
    ).decode(
        "ascii"
    )

    hash_text = base64.urlsafe_b64encode(
        derived
    ).decode(
        "ascii"
    )

    return (
        f"{PASSWORD_SCHEME}"
        f"${SCRYPT_N}"
        f"${SCRYPT_R}"
        f"${SCRYPT_P}"
        f"${SCRYPT_DKLEN}"
        f"${salt_text}"
        f"${hash_text}"
    )


def verify_password(
    password: str,
    encoded_hash: str,
) -> bool:
    try:
        (
            scheme,
            n_text,
            r_text,
            p_text,
            dklen_text,
            salt_text,
            hash_text,
        ) = encoded_hash.split(
            "$"
        )

        if scheme != PASSWORD_SCHEME:
            raise InvalidPasswordHashError(
                "Unsupported password-hash scheme"
            )

        n = int(
            n_text
        )
        r = int(
            r_text
        )
        p = int(
            p_text
        )
        dklen = int(
            dklen_text
        )

        if (
            n != SCRYPT_N
            or r != SCRYPT_R
            or p != SCRYPT_P
            or dklen != SCRYPT_DKLEN
        ):
            raise InvalidPasswordHashError(
                "Password-hash parameters are not approved"
            )

        salt = base64.urlsafe_b64decode(
            salt_text.encode(
                "ascii"
            )
        )

        expected = base64.urlsafe_b64decode(
            hash_text.encode(
                "ascii"
            )
        )

    except (
        AttributeError,
        TypeError,
        ValueError,
        UnicodeError,
    ) as exc:
        raise InvalidPasswordHashError(
            "Malformed password hash"
        ) from exc

    observed = _derive(
        password,
        salt,
        n=n,
        r=r,
        p=p,
        dklen=dklen,
    )

    return hmac.compare_digest(
        observed,
        expected,
    )

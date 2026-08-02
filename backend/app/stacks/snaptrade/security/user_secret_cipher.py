from __future__ import annotations

import base64
import hashlib
import os

from cryptography.fernet import (
    Fernet,
    InvalidToken,
)


ENCRYPTION_KEY_ENV = (
    "SNAPTRADE_USER_SECRET_ENCRYPTION_KEY"
)


class SnapTradeSecretConfigurationError(
    RuntimeError
):
    pass


class SnapTradeSecretDecryptionError(
    RuntimeError
):
    pass


def _normalized_fernet_key(
    raw_key: str,
) -> bytes:
    value = str(raw_key).strip()

    if not value:
        raise SnapTradeSecretConfigurationError(
            "SnapTrade user-secret encryption key is empty"
        )

    encoded = value.encode("utf-8")

    try:
        Fernet(encoded)
        return encoded
    except Exception:
        digest = hashlib.sha256(
            encoded
        ).digest()

        return base64.urlsafe_b64encode(
            digest
        )


def load_snaptrade_user_secret_cipher(
    *,
    environ: dict[str, str] | None = None,
) -> Fernet:
    source = (
        os.environ
        if environ is None
        else environ
    )

    raw_key = source.get(
        ENCRYPTION_KEY_ENV
    )

    if raw_key is None:
        raise SnapTradeSecretConfigurationError(
            f"{ENCRYPTION_KEY_ENV} is required"
        )

    return Fernet(
        _normalized_fernet_key(
            raw_key
        )
    )


def encrypt_snaptrade_user_secret(
    user_secret: str,
    *,
    cipher: Fernet | None = None,
) -> bytes:
    secret = str(user_secret).strip()

    if not secret:
        raise ValueError(
            "SnapTrade user secret is required"
        )

    active_cipher = (
        cipher
        or load_snaptrade_user_secret_cipher()
    )

    return active_cipher.encrypt(
        secret.encode("utf-8")
    )


def decrypt_snaptrade_user_secret(
    ciphertext: bytes,
    *,
    cipher: Fernet | None = None,
) -> str:
    if not isinstance(
        ciphertext,
        bytes,
    ) or not ciphertext:
        raise SnapTradeSecretDecryptionError(
            "Encrypted SnapTrade credential is invalid"
        )

    active_cipher = (
        cipher
        or load_snaptrade_user_secret_cipher()
    )

    try:
        plaintext = active_cipher.decrypt(
            ciphertext
        )
    except InvalidToken as exc:
        raise SnapTradeSecretDecryptionError(
            "SnapTrade credential could not be decrypted"
        ) from exc

    decoded = plaintext.decode(
        "utf-8"
    ).strip()

    if not decoded:
        raise SnapTradeSecretDecryptionError(
            "Decrypted SnapTrade credential is empty"
        )

    return decoded

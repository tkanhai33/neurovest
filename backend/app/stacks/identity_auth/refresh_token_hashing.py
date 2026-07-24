from __future__ import annotations

import hashlib
import hmac


def hash_refresh_token(
    token: str,
    *,
    pepper: bytes,
) -> str:
    if not isinstance(
        token,
        str,
    ) or not token:
        raise ValueError(
            "Refresh token cannot be empty"
        )

    if not isinstance(
        pepper,
        bytes,
    ) or len(pepper) < 32:
        raise ValueError(
            "Refresh-token pepper must contain at least "
            "32 bytes"
        )

    return hmac.new(
        pepper,
        token.encode(
            "utf-8"
        ),
        hashlib.sha256,
    ).hexdigest()


def verify_refresh_token_hash(
    token: str,
    expected_hash: str,
    *,
    pepper: bytes,
) -> bool:
    observed = hash_refresh_token(
        token,
        pepper=pepper,
    )

    return hmac.compare_digest(
        observed,
        expected_hash,
    )

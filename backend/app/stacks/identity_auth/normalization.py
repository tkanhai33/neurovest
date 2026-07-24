from __future__ import annotations

import unicodedata


def normalize_email(
    value: str,
) -> str:
    if not isinstance(
        value,
        str,
    ):
        raise TypeError(
            "Email must be a string"
        )

    normalized = unicodedata.normalize(
        "NFKC",
        value,
    ).strip().casefold()

    if not normalized:
        raise ValueError(
            "Email cannot be empty"
        )

    if "@" not in normalized:
        raise ValueError(
            "Email must contain an at-sign"
        )

    local, domain = normalized.rsplit(
        "@",
        1,
    )

    if not local or not domain:
        raise ValueError(
            "Email local and domain parts are required"
        )

    return (
        f"{local}@{domain}"
    )

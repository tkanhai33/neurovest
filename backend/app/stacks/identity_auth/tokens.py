from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
import uuid
from typing import Any, Mapping

from backend.app.stacks.identity_auth.contracts import (
    ACCESS_TOKEN_TYPE,
    DEFAULT_JWT_POLICY,
    REFRESH_TOKEN_TYPE,
    JWTPolicy,
    TokenClaims,
    TokenPair,
)

from backend.app.stacks.identity_auth.errors import (
    ExpiredTokenError,
    InvalidTokenError,
    RevokedTokenError,
    TokenNotYetValidError,
)

from backend.app.stacks.identity_auth.revocation import (
    InMemoryTokenRevocationStore,
)

from backend.app.stacks.identity_auth.secret_boundary import (
    load_jwt_secret,
)


REQUIRED_CLAIMS = {
    "iss",
    "aud",
    "sub",
    "exp",
    "nbf",
    "iat",
    "jti",
    "typ",
}


def _b64url_encode(
    payload: bytes,
) -> str:
    return base64.urlsafe_b64encode(
        payload
    ).rstrip(
        b"="
    ).decode(
        "ascii"
    )


def _b64url_decode(
    value: str,
) -> bytes:
    padding = "=" * (
        -len(value) % 4
    )

    try:
        return base64.urlsafe_b64decode(
            (
                value
                + padding
            ).encode(
                "ascii"
            )
        )

    except (
        ValueError,
        UnicodeError,
    ) as exc:
        raise InvalidTokenError(
            "Token contains invalid base64url data"
        ) from exc


def _json_bytes(
    value: Mapping[str, Any],
) -> bytes:
    return json.dumps(
        dict(
            value
        ),
        separators=(
            ",",
            ":",
        ),
        sort_keys=True,
        ensure_ascii=True,
    ).encode(
        "utf-8"
    )


def _sign(
    signing_input: bytes,
    secret: bytes,
) -> bytes:
    return hmac.new(
        secret,
        signing_input,
        hashlib.sha256,
    ).digest()


def _encode(
    claims: Mapping[str, Any],
    *,
    secret: bytes,
) -> str:
    header = {
        "alg": "HS256",
        "typ": "JWT",
    }

    encoded_header = _b64url_encode(
        _json_bytes(
            header
        )
    )

    encoded_payload = _b64url_encode(
        _json_bytes(
            claims
        )
    )

    signing_input = (
        f"{encoded_header}.{encoded_payload}"
    ).encode(
        "ascii"
    )

    encoded_signature = _b64url_encode(
        _sign(
            signing_input,
            secret,
        )
    )

    return (
        f"{encoded_header}."
        f"{encoded_payload}."
        f"{encoded_signature}"
    )


def issue_token(
    subject: str,
    token_type: str,
    *,
    extra_claims: Mapping[str, Any] | None = None,
    policy: JWTPolicy = DEFAULT_JWT_POLICY,
    now: int | None = None,
) -> str:
    if not subject:
        raise ValueError(
            "Token subject cannot be empty"
        )

    if token_type not in {
        ACCESS_TOKEN_TYPE,
        REFRESH_TOKEN_TYPE,
    }:
        raise ValueError(
            "Unsupported token type"
        )

    issued_at = (
        int(
            time.time()
        )
        if now is None
        else int(
            now
        )
    )

    lifetime = (
        policy.access_token_seconds
        if token_type == ACCESS_TOKEN_TYPE
        else policy.refresh_token_seconds
    )

    claims = {
        "iss": policy.issuer,
        "aud": policy.audience,
        "sub": subject,
        "iat": issued_at,
        "nbf": issued_at,
        "exp": issued_at + lifetime,
        "jti": uuid.uuid4().hex,
        "typ": token_type,
    }

    for key, value in dict(
        extra_claims
        or {}
    ).items():
        if key in REQUIRED_CLAIMS:
            raise ValueError(
                f"Reserved JWT claim cannot be overridden: {key}"
            )

        claims[key] = value

    return _encode(
        claims,
        secret=load_jwt_secret(),
    )


def issue_access_token(
    subject: str,
    *,
    extra_claims: Mapping[str, Any] | None = None,
    policy: JWTPolicy = DEFAULT_JWT_POLICY,
    now: int | None = None,
) -> str:
    return issue_token(
        subject,
        ACCESS_TOKEN_TYPE,
        extra_claims=extra_claims,
        policy=policy,
        now=now,
    )


def issue_refresh_token(
    subject: str,
    *,
    extra_claims: Mapping[str, Any] | None = None,
    policy: JWTPolicy = DEFAULT_JWT_POLICY,
    now: int | None = None,
) -> str:
    return issue_token(
        subject,
        REFRESH_TOKEN_TYPE,
        extra_claims=extra_claims,
        policy=policy,
        now=now,
    )


def issue_token_pair(
    subject: str,
    *,
    extra_claims: Mapping[str, Any] | None = None,
    policy: JWTPolicy = DEFAULT_JWT_POLICY,
    now: int | None = None,
) -> TokenPair:
    return TokenPair(
        access_token=issue_access_token(
            subject,
            extra_claims=extra_claims,
            policy=policy,
            now=now,
        ),
        refresh_token=issue_refresh_token(
            subject,
            extra_claims=extra_claims,
            policy=policy,
            now=now,
        ),
    )


def validate_token(
    token: str,
    expected_type: str,
    *,
    policy: JWTPolicy = DEFAULT_JWT_POLICY,
    revocation_store: (
        InMemoryTokenRevocationStore
        | None
    ) = None,
    now: int | None = None,
) -> TokenClaims:
    if expected_type not in {
        ACCESS_TOKEN_TYPE,
        REFRESH_TOKEN_TYPE,
    }:
        raise ValueError(
            "Unsupported expected token type"
        )

    if not isinstance(
        token,
        str,
    ) or not token:
        raise InvalidTokenError(
            "Token is missing"
        )

    parts = token.split(
        "."
    )

    if len(parts) != 3:
        raise InvalidTokenError(
            "Token must contain exactly three segments"
        )

    encoded_header, encoded_payload, encoded_signature = (
        parts
    )

    try:
        header = json.loads(
            _b64url_decode(
                encoded_header
            )
        )

        payload = json.loads(
            _b64url_decode(
                encoded_payload
            )
        )

    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
        TypeError,
    ) as exc:
        raise InvalidTokenError(
            "Token JSON is malformed"
        ) from exc

    if not isinstance(
        header,
        dict,
    ) or not isinstance(
        payload,
        dict,
    ):
        raise InvalidTokenError(
            "Token header and payload must be objects"
        )

    if header != {
        "alg": "HS256",
        "typ": "JWT",
    }:
        raise InvalidTokenError(
            "Token header is not approved"
        )

    signature = _b64url_decode(
        encoded_signature
    )

    signing_input = (
        f"{encoded_header}.{encoded_payload}"
    ).encode(
        "ascii"
    )

    expected_signature = _sign(
        signing_input,
        load_jwt_secret(),
    )

    if not hmac.compare_digest(
        signature,
        expected_signature,
    ):
        raise InvalidTokenError(
            "Token signature is invalid"
        )

    missing = REQUIRED_CLAIMS - set(
        payload
    )

    if missing:
        raise InvalidTokenError(
            "Token is missing required claims: "
            + ", ".join(
                sorted(
                    missing
                )
            )
        )

    if payload["iss"] != policy.issuer:
        raise InvalidTokenError(
            "Token issuer is invalid"
        )

    if payload["aud"] != policy.audience:
        raise InvalidTokenError(
            "Token audience is invalid"
        )

    if payload["typ"] != expected_type:
        raise InvalidTokenError(
            "Token type is invalid"
        )

    if not isinstance(
        payload["sub"],
        str,
    ) or not payload["sub"]:
        raise InvalidTokenError(
            "Token subject is invalid"
        )

    if not isinstance(
        payload["jti"],
        str,
    ) or not payload["jti"]:
        raise InvalidTokenError(
            "Token identifier is invalid"
        )

    integer_claims = {}

    for name in (
        "iat",
        "nbf",
        "exp",
    ):
        value = payload[
            name
        ]

        if (
            isinstance(
                value,
                bool,
            )
            or not isinstance(
                value,
                int,
            )
        ):
            raise InvalidTokenError(
                f"Token claim {name} must be an integer"
            )

        integer_claims[
            name
        ] = value

    current = (
        int(
            time.time()
        )
        if now is None
        else int(
            now
        )
    )

    if integer_claims[
        "nbf"
    ] > (
        current
        + policy.clock_skew_seconds
    ):
        raise TokenNotYetValidError(
            "Token is not yet valid"
        )

    if integer_claims[
        "exp"
    ] <= (
        current
        - policy.clock_skew_seconds
    ):
        raise ExpiredTokenError(
            "Token has expired"
        )

    if integer_claims[
        "iat"
    ] > (
        current
        + policy.clock_skew_seconds
    ):
        raise InvalidTokenError(
            "Token issuance time is in the future"
        )

    if integer_claims[
        "exp"
    ] <= integer_claims[
        "iat"
    ]:
        raise InvalidTokenError(
            "Token expiration does not follow issuance"
        )

    if (
        revocation_store is not None
        and revocation_store.is_revoked(
            payload[
                "jti"
            ]
        )
    ):
        raise RevokedTokenError(
            "Token has been revoked"
        )

    extra = {
        key: value
        for key, value in payload.items()
        if key not in REQUIRED_CLAIMS
    }

    return TokenClaims(
        subject=payload[
            "sub"
        ],
        token_type=payload[
            "typ"
        ],
        token_id=payload[
            "jti"
        ],
        issuer=payload[
            "iss"
        ],
        audience=payload[
            "aud"
        ],
        issued_at=integer_claims[
            "iat"
        ],
        not_before=integer_claims[
            "nbf"
        ],
        expires_at=integer_claims[
            "exp"
        ],
        extra=extra,
    )


def validate_access_token(
    token: str,
    *,
    policy: JWTPolicy = DEFAULT_JWT_POLICY,
    revocation_store: (
        InMemoryTokenRevocationStore
        | None
    ) = None,
    now: int | None = None,
) -> TokenClaims:
    return validate_token(
        token,
        ACCESS_TOKEN_TYPE,
        policy=policy,
        revocation_store=revocation_store,
        now=now,
    )


def validate_refresh_token(
    token: str,
    *,
    policy: JWTPolicy = DEFAULT_JWT_POLICY,
    revocation_store: (
        InMemoryTokenRevocationStore
        | None
    ) = None,
    now: int | None = None,
) -> TokenClaims:
    return validate_token(
        token,
        REFRESH_TOKEN_TYPE,
        policy=policy,
        revocation_store=revocation_store,
        now=now,
    )


def rotate_refresh_token(
    refresh_token: str,
    *,
    revocation_store: (
        InMemoryTokenRevocationStore
    ),
    policy: JWTPolicy = DEFAULT_JWT_POLICY,
    now: int | None = None,
) -> TokenPair:
    claims = validate_refresh_token(
        refresh_token,
        policy=policy,
        revocation_store=revocation_store,
        now=now,
    )

    revocation_store.revoke(
        claims.token_id
    )

    return issue_token_pair(
        claims.subject,
        extra_claims=claims.extra,
        policy=policy,
        now=now,
    )

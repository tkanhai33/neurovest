from __future__ import annotations

import json

import pytest

from backend.app.stacks.identity_auth.contracts import (
    ACCESS_TOKEN_TYPE,
    JWTPolicy,
    REFRESH_TOKEN_TYPE,
)

from backend.app.stacks.identity_auth.errors import (
    ExpiredTokenError,
    InvalidTokenError,
    MissingSecretError,
    TokenNotYetValidError,
)

from backend.app.stacks.identity_auth.tokens import (
    _b64url_decode,
    _b64url_encode,
    issue_access_token,
    issue_refresh_token,
    issue_token_pair,
    validate_access_token,
    validate_refresh_token,
)


TEST_SECRET = (
    "test-only-secret-material-"
    "0123456789abcdef"
)


@pytest.fixture(autouse=True)
def jwt_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "NEUROVEST_JWT_SECRET",
        TEST_SECRET,
    )


def _replace_payload(
    token: str,
    payload: dict,
) -> str:
    header, _, signature = token.split(
        "."
    )

    encoded_payload = _b64url_encode(
        json.dumps(
            payload,
            separators=(
                ",",
                ":",
            ),
            sort_keys=True,
        ).encode(
            "utf-8"
        )
    )

    return (
        f"{header}."
        f"{encoded_payload}."
        f"{signature}"
    )


def test_missing_secret_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(
        "NEUROVEST_JWT_SECRET",
        raising=False,
    )

    with pytest.raises(
        MissingSecretError
    ):
        issue_access_token(
            "user-1",
            now=1000,
        )


def test_access_token_round_trip() -> None:
    token = issue_access_token(
        "user-1",
        extra_claims={
            "role": "viewer",
        },
        now=1000,
    )

    claims = validate_access_token(
        token,
        now=1001,
    )

    assert claims.subject == "user-1"
    assert claims.token_type == ACCESS_TOKEN_TYPE
    assert claims.extra[
        "role"
    ] == "viewer"


def test_refresh_token_is_not_accepted_as_access() -> None:
    token = issue_refresh_token(
        "user-1",
        now=1000,
    )

    with pytest.raises(
        InvalidTokenError
    ):
        validate_access_token(
            token,
            now=1001,
        )


def test_access_token_is_not_accepted_as_refresh() -> None:
    token = issue_access_token(
        "user-1",
        now=1000,
    )

    with pytest.raises(
        InvalidTokenError
    ):
        validate_refresh_token(
            token,
            now=1001,
        )


def test_token_pair_uses_separate_tokens() -> None:
    pair = issue_token_pair(
        "user-1",
        now=1000,
    )

    assert pair.access_token != pair.refresh_token

    assert validate_access_token(
        pair.access_token,
        now=1001,
    ).token_type == ACCESS_TOKEN_TYPE

    assert validate_refresh_token(
        pair.refresh_token,
        now=1001,
    ).token_type == REFRESH_TOKEN_TYPE


def test_expired_token_is_rejected() -> None:
    policy = JWTPolicy(
        access_token_seconds=10,
        refresh_token_seconds=20,
    )

    token = issue_access_token(
        "user-1",
        policy=policy,
        now=1000,
    )

    with pytest.raises(
        ExpiredTokenError
    ):
        validate_access_token(
            token,
            policy=policy,
            now=1010,
        )


def test_not_before_claim_is_enforced() -> None:
    token = issue_access_token(
        "user-1",
        now=1000,
    )

    with pytest.raises(
        TokenNotYetValidError
    ):
        validate_access_token(
            token,
            now=999,
        )


def test_tampered_payload_is_rejected() -> None:
    token = issue_access_token(
        "user-1",
        now=1000,
    )

    _, encoded_payload, _ = token.split(
        "."
    )

    payload = json.loads(
        _b64url_decode(
            encoded_payload
        )
    )

    payload[
        "sub"
    ] = "attacker"

    tampered = _replace_payload(
        token,
        payload,
    )

    with pytest.raises(
        InvalidTokenError
    ):
        validate_access_token(
            tampered,
            now=1001,
        )


def test_wrong_issuer_is_rejected() -> None:
    issued_policy = JWTPolicy(
        issuer="wrong-issuer",
    )

    token = issue_access_token(
        "user-1",
        policy=issued_policy,
        now=1000,
    )

    with pytest.raises(
        InvalidTokenError
    ):
        validate_access_token(
            token,
            now=1001,
        )


def test_wrong_audience_is_rejected() -> None:
    issued_policy = JWTPolicy(
        audience="wrong-audience",
    )

    token = issue_access_token(
        "user-1",
        policy=issued_policy,
        now=1000,
    )

    with pytest.raises(
        InvalidTokenError
    ):
        validate_access_token(
            token,
            now=1001,
        )


def test_malformed_token_is_rejected() -> None:
    with pytest.raises(
        InvalidTokenError
    ):
        validate_access_token(
            "not-a-jwt",
            now=1001,
        )


def test_reserved_claims_cannot_be_overridden() -> None:
    with pytest.raises(
        ValueError
    ):
        issue_access_token(
            "user-1",
            extra_claims={
                "typ": "refresh",
            },
            now=1000,
        )

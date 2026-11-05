from __future__ import annotations

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from backend.app.stacks.identity_auth.api_dependencies import (
    _AUTH_LIMITER,
    enforce_auth_rate_limit,
    reset_auth_rate_limiter,
)
from backend.app.stacks.identity_auth.api_router import router


@pytest.fixture(
    autouse=True,
)
def _isolate_auth_rate_limiter_state():
    """Provide clean process-local limiter state for every test."""

    reset_auth_rate_limiter()

    try:
        yield

    finally:
        reset_auth_rate_limiter()


def build_request(
    host: str,
) -> Request:
    return Request(
        {
            "type": "http",
            "http_version": "1.1",
            "method": "POST",
            "scheme": "http",
            "path": "/auth/login",
            "raw_path": b"/auth/login",
            "query_string": b"",
            "headers": [],
            "client": (
                host,
                50000,
            ),
            "server": (
                "testserver",
                80,
            ),
        }
    )


@pytest.fixture(autouse=True)
def clear_auth_limiter() -> None:
    reset_auth_rate_limiter()

    yield

    reset_auth_rate_limiter()


@pytest.mark.asyncio
async def test_auth_requests_are_rate_limited_by_client_ip() -> None:
    request = build_request(
        "198.51.100.10"
    )

    for _ in range(
        _AUTH_LIMITER._limit
    ):
        await enforce_auth_rate_limit(
            request
        )

    with pytest.raises(
        HTTPException
    ) as captured:
        await enforce_auth_rate_limit(
            request
        )

    assert captured.value.status_code == 429
    assert (
        captured.value.detail
        == "Too many authentication requests"
    )


@pytest.mark.asyncio
async def test_auth_rate_limit_is_isolated_by_client_ip() -> None:
    first_client = build_request(
        "198.51.100.20"
    )

    second_client = build_request(
        "198.51.100.21"
    )

    for _ in range(
        _AUTH_LIMITER._limit
    ):
        await enforce_auth_rate_limit(
            first_client
        )

    await enforce_auth_rate_limit(
        second_client
    )


def test_login_and_registration_routes_use_auth_rate_limit() -> None:
    protected_paths = {
        "/auth/login",
        "/auth/register",
    }

    located = set()

    for route in router.routes:
        if getattr(
            route,
            "path",
            None,
        ) not in protected_paths:
            continue

        dependency_calls = {
            dependency.call
            for dependency in (
                route.dependant.dependencies
            )
        }

        assert (
            enforce_auth_rate_limit
            in dependency_calls
        )

        located.add(
            route.path
        )

    assert located == protected_paths


@pytest.mark.asyncio
async def test_public_proxy_aggregate_limit() -> None:
    from backend.app.stacks.identity_auth import api_dependencies as auth

    request = build_request("127.0.0.1")
    previous = getattr(auth, "_PUBLIC_AUTH_AGGREGATE_LIMITER", None)

    try:
        auth._PUBLIC_AUTH_AGGREGATE_LIMITER = None

        for _ in range(300):
            await auth.enforce_auth_rate_limit(request)

        with pytest.raises(HTTPException) as captured:
            await auth.enforce_auth_rate_limit(request)

        assert captured.value.status_code == 429
    finally:
        auth._PUBLIC_AUTH_AGGREGATE_LIMITER = previous

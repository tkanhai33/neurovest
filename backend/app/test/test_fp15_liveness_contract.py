from __future__ import annotations

import asyncio

from fastapi.routing import APIRoute

from backend.app.main import (
    app,
    service_liveness,
)


def test_dedicated_liveness_route_is_registered() -> None:
    matches = [
        route
        for route in app.routes
        if isinstance(
            route,
            APIRoute,
        )
        and route.path == "/health/live"
    ]

    assert len(matches) == 1

    assert matches[0].methods == {
        "GET",
    }


def test_liveness_contract_is_dependency_free() -> None:
    route = next(
        route
        for route in app.routes
        if isinstance(
            route,
            APIRoute,
        )
        and route.path == "/health/live"
    )

    assert (
        route.dependant.dependencies
        == []
    )


def test_liveness_contract_returns_stable_payload() -> None:
    result = asyncio.run(
        service_liveness()
    )

    assert result == {
        "status": "alive",
        "service": "neurovest-backend",
        "live": True,
    }


def test_liveness_contract_does_not_claim_readiness() -> None:
    result = asyncio.run(
        service_liveness()
    )

    assert "database" not in result
    assert "broker" not in result
    assert "ready" not in result
    assert result["status"] == "alive"

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.app.stacks.strategy.user_activation import api
from backend.app.stacks.strategy.user_activation.model import (
    UserStrategyUniverseMember,
)
from backend.app.stacks.strategy.user_activation.service import (
    _clean_owner_universe_symbols,
)


def test_owner_universe_model_has_owner_scoped_unique_identity():
    assert UserStrategyUniverseMember.__tablename__ == (
        "user_strategy_universe_members"
    )

    constraint_names = {
        constraint.name
        for constraint in UserStrategyUniverseMember.__table__.constraints
    }

    assert "uq_user_strategy_universe_owner_name_symbol" in constraint_names


def test_owner_universe_normalizes_deduplicates_and_sorts_at_boundary():
    assert _clean_owner_universe_symbols(
        [" aapl ", "MSFT", "aapl"]
    ) == ["AAPL", "MSFT"]


@pytest.mark.parametrize(
    "symbols",
    (
        [],
        ["AAPL"],
        ["AAPL", ""],
        "AAPL",
    ),
)
def test_owner_universe_rejects_invalid_requests(symbols):
    with pytest.raises(ValueError):
        _clean_owner_universe_symbols(symbols)


def test_owner_universe_api_is_authenticated_and_bounded():
    route_methods: dict[str, set[str]] = {}

    for route in api.router.routes:
        route_methods.setdefault(
            route.path,
            set(),
        ).update(route.methods or set())

    assert "/api/v1/strategy-library/universe" in route_methods
    assert {"GET", "PUT"} <= route_methods[
        "/api/v1/strategy-library/universe"
    ]

    payload = api.StrategyUniverseReplaceRequest(
        symbols=["AAPL", "MSFT"]
    )

    assert payload.symbols == ["AAPL", "MSFT"]

    with pytest.raises(ValidationError):
        api.StrategyUniverseReplaceRequest(
            symbols=["AAPL"]
        )

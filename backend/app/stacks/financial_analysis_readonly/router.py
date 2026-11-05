"""NeuroVest read-only financial analysis staging router."""

from __future__ import annotations

from pathlib import Path

from backend.app.stacks.market_data import multi_symbol_bars
from backend.app.stacks.strategy.user_activation import api as activation_api

from .financial_api import create_candidate_router


def build_router():
    owner_function = getattr(
        activation_api,
        "list_owner_universe_symbols",
        None,
    )

    provider_function = getattr(
        multi_symbol_bars,
        "get_daily_bars_for_symbols",
        None,
    )

    if not callable(owner_function):
        raise RuntimeError("owner_resolver_unavailable")

    if not callable(provider_function):
        raise RuntimeError("market_provider_unavailable")

    async def resolve_owner(*, owner_subject):
        if not isinstance(owner_subject, str) or not owner_subject:
            raise RuntimeError("invalid_authenticated_owner")

        return await owner_function(
            owner_subject=owner_subject
        )

    def load_bars(symbols, *, limit):
        return provider_function(
            symbols,
            limit=limit,
        )

    return create_candidate_router(
        owner_universe_loader=resolve_owner,
        provider_loader=load_bars,
        b13_directory=Path(__file__).resolve().parent,
    )

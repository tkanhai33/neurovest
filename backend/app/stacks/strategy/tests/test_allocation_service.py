from __future__ import annotations

import asyncio

import pytest

from backend.app.stacks.strategy import allocation_service


SYMBOLS = (
    "SPY", "QQQ", "IWM", "DIA",
    "XLK", "XLF", "XLE", "XLV",
    "XLY", "XLP", "XLI", "XLU",
    "XLB", "XLRE", "TLT", "GLD",
)


def _bars() -> list[dict[str, float]]:
    return [
        {"close": 100.0 + index}
        for index in range(253)
    ]


def _universe_bars() -> dict[str, list[dict[str, float]]]:
    return {
        symbol: _bars()
        for symbol in SYMBOLS
    }


def test_owner_proposals_are_complete_and_non_executable(monkeypatch):
    async def fake_symbols(*, owner_subject: str, universe_name: str):
        assert owner_subject == "owner-a"
        assert universe_name == "default"
        return list(SYMBOLS)

    monkeypatch.setattr(
        allocation_service,
        "list_owner_universe_symbols",
        fake_symbols,
    )

    async def enabled_names(*, owner_subject: str):
        assert owner_subject == "owner-a"
        return [
            "Equal Weight Portfolio",
            "60/40 Rebalanced Portfolio",
            "Permanent Portfolio",
        ]

    monkeypatch.setattr(
        allocation_service,
        "list_enabled_strategy_names",
        enabled_names,
    )

    monkeypatch.setattr(
        allocation_service,
        "get_daily_bars_for_symbols",
        lambda symbols, *, limit: _universe_bars(),
    )

    output = asyncio.run(
        allocation_service.get_owner_allocation_proposals(
            owner_subject="owner-a",
        )
    )

    assert output["proposal_count"] == 3
    assert [
        proposal["strategy_name"]
        for proposal in output["proposals"]
    ] == [
        "Equal Weight Portfolio",
        "60/40 Rebalanced Portfolio",
        "Permanent Portfolio",
    ]
    assert output["owner_allocation_strategy_applied"] is True
    assert output["execution_enabled"] is False
    assert output["broker_order_generation_enabled"] is False


def test_missing_owner_universe_fails_closed(monkeypatch):
    async def no_symbols(*, owner_subject: str, universe_name: str):
        return []

    monkeypatch.setattr(
        allocation_service,
        "list_owner_universe_symbols",
        no_symbols,
    )

    with pytest.raises(
        allocation_service.OwnerAllocationProposalsUnavailableError,
        match="at least two symbols",
    ):
        asyncio.run(
            allocation_service.get_owner_allocation_proposals(
                owner_subject="owner-a",
            )
        )



def test_no_enabled_allocation_strategy_skips_provider_read(monkeypatch):
    async def symbols(*, owner_subject: str, universe_name: str):
        return list(SYMBOLS)

    async def enabled_names(*, owner_subject: str):
        return ["SMA Crossover"]

    def provider_must_not_run(*args, **kwargs):
        raise AssertionError("provider must not run")

    monkeypatch.setattr(
        allocation_service,
        "list_owner_universe_symbols",
        symbols,
    )
    monkeypatch.setattr(
        allocation_service,
        "list_enabled_strategy_names",
        enabled_names,
    )
    monkeypatch.setattr(
        allocation_service,
        "get_daily_bars_for_symbols",
        provider_must_not_run,
    )

    output = asyncio.run(
        allocation_service.get_owner_allocation_proposals(
            owner_subject="owner-a",
        )
    )

    assert output["proposal_count"] == 0
    assert output["owner_allocation_strategy_applied"] is False
    assert output["provider_data_read"] is False
    assert output["execution_enabled"] is False

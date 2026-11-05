from __future__ import annotations

import asyncio

from backend.app.stacks.strategy import allocation_paper_service


def test_owner_paper_evaluations_are_snapshot_only(monkeypatch):
    async def fake_proposals(*, owner_subject: str):
        assert owner_subject == "owner-a"
        return {
            "proposal_count": 1,
            "universe_name": "default",
            "universe_symbols": ["SPY", "TLT"],
            "proposals": [{"strategy_name": "Equal Weight Portfolio"}],
            "enabled_allocation_strategy_names": [
                "Equal Weight Portfolio",
            ],
        }

    monkeypatch.setattr(
        allocation_paper_service,
        "get_owner_allocation_proposals",
        fake_proposals,
    )
    monkeypatch.setattr(
        allocation_paper_service,
        "get_daily_bars_for_symbols",
        lambda symbols, *, limit: {"SPY": [], "TLT": []},
    )
    monkeypatch.setattr(
        allocation_paper_service,
        "evaluate_fixed_weight_proposal_snapshot",
        lambda **kwargs: {
            "status": "ok",
            "strategy_backtest": False,
            "execution_enabled": False,
        },
    )

    output = asyncio.run(
        allocation_paper_service.get_owner_allocation_paper_evaluations(
            owner_subject="owner-a",
        )
    )

    assert output["evaluation_count"] == 1
    assert output["strategy_backtest"] is False
    assert output["execution_enabled"] is False


def test_no_enabled_proposals_skips_provider_read(monkeypatch):
    async def fake_proposals(*, owner_subject: str):
        return {
            "proposal_count": 0,
            "reason": "no_enabled_allocation_proposal_strategies",
        }

    def provider_must_not_run(*args, **kwargs):
        raise AssertionError("provider must not run")

    monkeypatch.setattr(
        allocation_paper_service,
        "get_owner_allocation_proposals",
        fake_proposals,
    )
    monkeypatch.setattr(
        allocation_paper_service,
        "get_daily_bars_for_symbols",
        provider_must_not_run,
    )

    output = asyncio.run(
        allocation_paper_service.get_owner_allocation_paper_evaluations(
            owner_subject="owner-a",
        )
    )

    assert output["evaluation_count"] == 0
    assert output["provider_data_read"] is False

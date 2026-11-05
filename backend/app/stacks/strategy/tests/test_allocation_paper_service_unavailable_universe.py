from __future__ import annotations

import asyncio

from backend.app.stacks.strategy import (
    allocation_paper_service,
)


def test_owner_universe_with_fewer_than_two_symbols_is_empty_state(
    monkeypatch,
) -> None:
    async def unavailable_owner_proposals(
        *,
        owner_subject: str,
    ) -> dict[str, object]:
        raise (
            allocation_paper_service.
            _allocation_service.
            OwnerAllocationProposalsUnavailableError(
                "owner universe requires at least two symbols"
            )
        )

    monkeypatch.setattr(
        allocation_paper_service,
        "get_owner_allocation_proposals",
        unavailable_owner_proposals,
    )

    result = asyncio.run(
        allocation_paper_service.
        get_owner_allocation_paper_evaluations(
            owner_subject="qualification-user",
        )
    )

    assert result["status"] == "ok"
    assert result["evaluation_count"] == 0
    assert result["evaluations"] == []
    assert (
        result["owner_allocation_strategy_applied"]
        is False
    )
    assert result["provider_data_read"] is False
    assert result["execution_enabled"] is False
    assert (
        result["reason"]
        == "owner universe requires at least two symbols"
    )

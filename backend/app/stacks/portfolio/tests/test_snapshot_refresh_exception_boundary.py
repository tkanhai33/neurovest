from __future__ import annotations

from pathlib import Path

import pytest

from backend.app.spine.L5_api.owned_readonly_portfolio_service import (
    AuthenticatedPortfolioUnavailable,
)
from backend.app.stacks.portfolio import (
    portfolio_snapshot_lifecycle as lifecycle,
)
from backend.app.stacks.portfolio.portfolio_snapshot_lifecycle import (
    PortfolioSnapshotLifecycleError,
)


def test_missing_normalized_snapshot_is_translated_at_lifecycle_boundary(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    user_id = "objective-5j-exception-boundary-user"

    def missing_snapshot() -> Path:
        raise AuthenticatedPortfolioUnavailable(
            "No qualified normalized portfolio snapshot exists."
        )

    monkeypatch.setattr(
        lifecycle,
        "find_latest_normalized_portfolio",
        missing_snapshot,
    )

    with pytest.raises(
        PortfolioSnapshotLifecycleError,
        match=(
            "No qualified normalized portfolio "
            "snapshot exists"
        ),
    ):
        lifecycle.refresh_portfolio_snapshot(
            neurovest_user_id=user_id,
            runtime_root=tmp_path,
        )

    state = lifecycle.get_portfolio_lifecycle(
        neurovest_user_id=user_id,
        runtime_root=tmp_path,
    )

    assert state["snapshot_state"] == "missing"
    assert state["active_snapshot_present"] is False
    assert state["last_refresh_status"] == "failed"

    assert (
        state["last_failure_type"]
        == "AuthenticatedPortfolioUnavailable"
    )

    assert (
        state["last_failure_message"]
        == "No qualified normalized portfolio snapshot exists."
    )

    assert state["failed_refresh_count"] == 1
    assert state["refresh_count"] == 0
    assert state["network_request_count"] == 0
    assert state["database_write_count"] == 0


def test_unrelated_refresh_exception_remains_unmodified(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    def unexpected_failure() -> Path:
        raise RuntimeError(
            "unexpected qualification failure"
        )

    monkeypatch.setattr(
        lifecycle,
        "find_latest_normalized_portfolio",
        unexpected_failure,
    )

    with pytest.raises(
        RuntimeError,
        match="unexpected qualification failure",
    ):
        lifecycle.refresh_portfolio_snapshot(
            neurovest_user_id=(
                "objective-5j-unrelated-error-user"
            ),
            runtime_root=tmp_path,
        )

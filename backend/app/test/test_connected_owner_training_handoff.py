
import asyncio
from types import SimpleNamespace

import pytest

from backend.app.stacks.db_runtime import (
    connected_symbol_context_bridge as bridge,
)
from backend.app.stacks.strategy_candidate_sandbox.L4_runtime_orchestration import (
    bounded_training_runtime as runtime,
)


def run(coroutine):
    return asyncio.run(coroutine)


def test_authenticated_owner_launch(monkeypatch):
    received = {}

    async def select(**kwargs):
        received["identity"] = kwargs
        return ("BTE.TO", "TD.TO", "WCP.TO")

    def discover():
        return [
            {"symbol": symbol, "path": "unused"}
            for symbol in ("BTE.TO", "TD.TO", "WCP.TO")
        ]

    def start(**kwargs):
        received["launch"] = kwargs
        return {
            "run_id": "mock-run",
            "scope": kwargs["scope"],
            "owner_user_id": kwargs["owner_user_id"],
            "selected_symbols": list(kwargs["selected_symbols"]),
        }

    monkeypatch.setattr(
        bridge, "select_authenticated_training_symbols", select
    )
    monkeypatch.setattr(runtime, "discover_canadian_datasets", discover)
    monkeypatch.setattr(runtime, "start_bounded_training_session", start)

    result = run(bridge.launch_connected_owner_training(
        owner_user_id="owner-a",
        owner_session_id="session-a",
        role="developer",
    ))

    assert result["scope"] == "user"
    assert result["owner_user_id"] == "owner-a"
    assert received["identity"]["owner_user_id"] == "owner-a"
    assert received["identity"]["owner_session_id"] == "session-a"
    assert received["launch"]["selected_symbols"] == (
        "BTE.TO", "TD.TO", "WCP.TO"
    )
    assert received["launch"]["scope"] == "user"


@pytest.mark.parametrize("role", ["admin", "support"])
def test_privileged_non_developer_role_denied(monkeypatch, role):
    async def forbidden(**kwargs):
        raise AssertionError("Selection should not run")

    monkeypatch.setattr(
        bridge, "select_authenticated_training_symbols", forbidden
    )

    with pytest.raises(PermissionError):
        run(bridge.launch_connected_owner_training(
            owner_user_id="owner-a",
            owner_session_id="session-a",
            role=role,
        ))


def test_missing_dataset_never_launches(monkeypatch):
    async def select(**kwargs):
        return ("TD.TO", "WCP.TO")

    def forbidden(**kwargs):
        raise AssertionError("Training must not start")

    monkeypatch.setattr(
        bridge, "select_authenticated_training_symbols", select
    )
    monkeypatch.setattr(
        runtime, "discover_canadian_datasets",
        lambda: [{"symbol": "TD.TO"}],
    )
    monkeypatch.setattr(
        runtime, "start_bounded_training_session", forbidden
    )

    with pytest.raises(ValueError):
        run(bridge.launch_connected_owner_training(
            owner_user_id="owner-a",
            owner_session_id="session-a",
            role="user",
        ))


def test_missing_authenticated_session_denied(monkeypatch):
    async def select(**kwargs):
        from backend.app.stacks.db_runtime.owner_ai_scope import (
            OwnerAIScope,
        )
        OwnerAIScope(
            owner_user_id=kwargs["owner_user_id"],
            owner_session_id=kwargs["owner_session_id"],
            role=kwargs["role"],
        )
        return ("TD.TO",)

    monkeypatch.setattr(
        bridge, "select_authenticated_training_symbols", select
    )

    with pytest.raises(PermissionError):
        run(bridge.launch_connected_owner_training(
            owner_user_id="owner-a",
            owner_session_id="",
            role="user",
        ))

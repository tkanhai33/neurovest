
import pytest

from backend.app.stacks.db_runtime import (
    connected_symbol_context_bridge as bridge,
)
from backend.app.stacks.strategy_candidate_sandbox.L4_runtime_orchestration import (
    bounded_training_runtime as runtime,
)


RUN = "training_20261010_200000_abc123def0"


def check(monkeypatch, result, owner="owner-a", run_id=RUN):
    monkeypatch.setattr(
        runtime,
        "get_training_session",
        lambda requested: result,
    )
    return bridge.get_authenticated_owner_training_result(
        owner_user_id=owner,
        run_id=run_id,
    )


def test_owner_can_read_own_result(monkeypatch):
    result = {
        "run_id": RUN,
        "scope": "user",
        "owner_user_id": "owner-a",
        "selected_symbols": ["TD.TO"],
    }
    assert check(monkeypatch, result) == result


def test_other_owner_cannot_read_result(monkeypatch):
    result = {
        "run_id": RUN,
        "scope": "user",
        "owner_user_id": "owner-b",
    }
    assert check(monkeypatch, result) is None


def test_system_training_not_exposed(monkeypatch):
    result = {
        "run_id": RUN,
        "scope": "system",
        "owner_user_id": None,
    }
    assert check(monkeypatch, result) is None


def test_missing_owner_field_denied(monkeypatch):
    assert check(monkeypatch, {"scope": "user"}) is None


def test_nonexistent_run(monkeypatch):
    assert check(monkeypatch, None) is None


def test_no_authenticated_identity(monkeypatch):
    with pytest.raises(PermissionError):
        check(monkeypatch, {}, owner="")


@pytest.mark.parametrize(
    "run_id",
    ["../private", "../../etc/passwd", "", "run/id"],
)
def test_unsafe_run_ids_denied(monkeypatch, run_id):
    with pytest.raises(ValueError):
        check(monkeypatch, {}, run_id=run_id)

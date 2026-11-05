from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from backend.app.stacks.execution.execution_control import (
    ExecutionBlockedError,
    ExecutionControl,
    InvalidOperatingModeTransition,
    OperatingMode,
)
from backend.app.stacks.execution import (
    paper_broker,
)


def make_control(
    tmp_path: Path,
) -> ExecutionControl:
    return ExecutionControl(
        state_path=(
            tmp_path
            / "execution-control.json"
        )
    )


def test_new_control_starts_safe(
    tmp_path: Path,
) -> None:
    control = make_control(
        tmp_path
    )

    snapshot = control.snapshot()

    assert (
        snapshot.mode
        == OperatingMode.SAFE.value
    )

    assert (
        snapshot.paper_execution_enabled
        is False
    )

    assert (
        snapshot.live_execution_enabled
        is False
    )


def test_safe_mode_blocks_paper_execution(
    tmp_path: Path,
) -> None:
    control = make_control(
        tmp_path
    )

    with pytest.raises(
        ExecutionBlockedError
    ):
        control.assert_paper_execution_allowed()


def test_simulation_allows_only_paper_execution(
    tmp_path: Path,
) -> None:
    control = make_control(
        tmp_path
    )

    control.transition(
        OperatingMode.SIMULATION,
        actor="test-admin",
        reason="Enable controlled paper simulation",
    )

    control.assert_paper_execution_allowed()

    with pytest.raises(
        ExecutionBlockedError
    ):
        control.assert_live_execution_allowed()


def test_locked_mode_blocks_execution(
    tmp_path: Path,
) -> None:
    control = make_control(
        tmp_path
    )

    control.transition(
        OperatingMode.LOCKED,
        actor="test-admin",
        reason="Administrative lock",
    )

    with pytest.raises(
        ExecutionBlockedError
    ):
        control.assert_paper_execution_allowed()


def test_emergency_stop_blocks_execution(
    tmp_path: Path,
) -> None:
    control = make_control(
        tmp_path
    )

    snapshot = (
        control.emergency_stop(
            actor="test-admin",
            reason="Emergency qualification",
        )
    )

    assert (
        snapshot.mode
        == OperatingMode.EMERGENCY_STOP.value
    )

    assert (
        snapshot.emergency_stop_active
        is True
    )

    with pytest.raises(
        ExecutionBlockedError
    ):
        control.assert_paper_execution_allowed()


def test_emergency_stop_recovery_requires_locked(
    tmp_path: Path,
) -> None:
    control = make_control(
        tmp_path
    )

    control.emergency_stop(
        actor="test-admin",
        reason="Emergency qualification",
    )

    with pytest.raises(
        InvalidOperatingModeTransition
    ):
        control.transition(
            OperatingMode.SIMULATION,
            actor="test-admin",
            reason="Forbidden direct recovery",
        )

    control.transition(
        OperatingMode.LOCKED,
        actor="test-admin",
        reason="Controlled recovery lock",
    )

    control.transition(
        OperatingMode.SAFE,
        actor="test-admin",
        reason="Return to safe operation",
    )


def test_mode_survives_restart(
    tmp_path: Path,
) -> None:
    state_path = (
        tmp_path
        / "execution-control.json"
    )

    first = ExecutionControl(
        state_path=state_path
    )

    first.transition(
        OperatingMode.SIMULATION,
        actor="test-admin",
        reason="Persist simulation mode",
    )

    second = ExecutionControl(
        state_path=state_path
    )

    snapshot = second.snapshot()

    assert (
        snapshot.mode
        == OperatingMode.SIMULATION.value
    )

    assert snapshot.revision == 1


def test_invalid_persisted_state_locks_fail_closed(
    tmp_path: Path,
) -> None:
    state_path = (
        tmp_path
        / "execution-control.json"
    )

    state_path.write_text(
        "{not valid json",
        encoding="utf-8",
    )

    control = ExecutionControl(
        state_path=state_path
    )

    assert (
        control.snapshot().mode
        == OperatingMode.LOCKED.value
    )


def test_paper_broker_invokes_central_gate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = []

    def deny() -> None:
        called.append(
            True
        )

        raise ExecutionBlockedError(
            "blocked by test"
        )

    monkeypatch.setattr(
        paper_broker.execution_control,
        "assert_paper_execution_allowed",
        deny,
    )

    with pytest.raises(
        ExecutionBlockedError
    ):
        asyncio.run(
            paper_broker.process_portfolio_output(
                [
                    {
                        "symbol": "AAPL",
                        "signal": "buy",
                    }
                ],
                {
                    "symbol": "AAPL",
                    "signal": "buy",
                },
                user_id="test-owner",
                trace_id="test-trace",
            )
        )

    assert called == [
        True,
    ]

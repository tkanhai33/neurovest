from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from backend.app.stacks.execution.execution_control import (
    ExecutionBlockedError,
    ExecutionControl,
    OperatingMode,
)
from backend.app.stacks.execution.emergency_commit_barrier import (
    CommitBarrierBlocked,
    financial_commit_barrier,
)
from backend.app.stacks.execution.emergency_stop_coordinator import (
    finalize_emergency_stop,
    publish_stop_intent,
)


def make_control(tmp_path: Path):
    state = tmp_path / "operating_mode.json"
    control = ExecutionControl(state_path=state)

    control.transition(
        OperatingMode.SIMULATION,
        actor="offline-r39b",
        reason="Isolated integrated regression",
    )
    return control, state


def marker_for(state: Path):
    return state.with_name(state.name + ".stop.pending")


def test_stop_blocks_subsequent_financial_work(tmp_path):
    async def scenario():
        control, state = make_control(tmp_path)

        async with financial_commit_barrier(state):
            control.assert_paper_execution_allowed()

        stopped = await finalize_emergency_stop(
            control,
            state,
            actor="offline-r39b",
            reason="Integrated stop qualification",
        )

        assert stopped.mode == "EMERGENCY_STOP"
        assert marker_for(state).exists()

        with pytest.raises(CommitBarrierBlocked):
            async with financial_commit_barrier(state):
                pytest.fail("Stopped work was admitted")

        with pytest.raises(ExecutionBlockedError):
            control.assert_paper_execution_allowed()

    asyncio.run(scenario())


def test_stop_waits_for_critical_section(tmp_path):
    async def scenario():
        control, state = make_control(tmp_path)

        entered = asyncio.Event()
        release = asyncio.Event()
        completed = asyncio.Event()

        async def worker():
            async with financial_commit_barrier(state):
                control.assert_paper_execution_allowed()
                entered.set()
                await asyncio.wait_for(release.wait(), 5)
            completed.set()

        task = asyncio.create_task(worker())
        await asyncio.wait_for(entered.wait(), 5)

        stopper = asyncio.create_task(
            finalize_emergency_stop(
                control,
                state,
                actor="offline-r39b",
                reason="Concurrent stop qualification",
            )
        )

        try:
            async def wait_for_marker():
                while not marker_for(state).exists():
                    await asyncio.sleep(0.01)

            await asyncio.wait_for(wait_for_marker(), 5)

            assert not stopper.done()

            with pytest.raises(CommitBarrierBlocked):
                async with financial_commit_barrier(state):
                    pytest.fail(
                        "New work entered after stop intent"
                    )
        finally:
            release.set()

        await asyncio.wait_for(task, 5)

        stopped = await asyncio.wait_for(stopper, 5)

        assert completed.is_set()
        assert stopped.mode == "EMERGENCY_STOP"

    asyncio.run(scenario())


def test_stop_timeout_retains_blockade(tmp_path):
    async def scenario():
        control, state = make_control(tmp_path)

        async with financial_commit_barrier(state):
            with pytest.raises(CommitBarrierBlocked):
                await finalize_emergency_stop(
                    control,
                    state,
                    actor="offline-r39b",
                    reason="Timeout qualification",
                    timeout_seconds=0.05,
                )

            assert marker_for(state).exists()

            with pytest.raises(ExecutionBlockedError):
                control.assert_paper_execution_allowed()

        assert marker_for(state).exists()

        stopped = await finalize_emergency_stop(
            control,
            state,
            actor="offline-r39b",
            reason="Resume stop finalization",
        )

        assert stopped.mode == "EMERGENCY_STOP"

    asyncio.run(scenario())


def test_pending_stop_blocks_ordinary_transitions(tmp_path):
    control, state = make_control(tmp_path)

    publish_stop_intent(state)

    with pytest.raises(ExecutionBlockedError):
        control.transition(
            OperatingMode.SAFE,
            actor="offline-r39b",
            reason="Blocked ordinary transition",
        )

    with pytest.raises(ExecutionBlockedError):
        control.assert_paper_execution_allowed()

    stopped = control.emergency_stop(
        actor="offline-r39b",
        reason="Stop must remain permitted",
    )

    assert stopped.mode == "EMERGENCY_STOP"

    with pytest.raises(ExecutionBlockedError):
        control.transition(
            OperatingMode.SIMULATION,
            actor="offline-r39b",
            reason="Unauthorized reset",
        )


def test_stop_survives_controller_restart(tmp_path):
    control, state = make_control(tmp_path)

    publish_stop_intent(state)

    control.emergency_stop(
        actor="offline-r39b",
        reason="Persistence test",
    )

    fresh = ExecutionControl(state_path=state)

    assert fresh.snapshot().mode == "EMERGENCY_STOP"
    assert marker_for(state).exists()

    payload = json.loads(state.read_text())

    assert payload["paper_execution_enabled"] is False
    assert payload["live_execution_enabled"] is False

    with pytest.raises(ExecutionBlockedError):
        fresh.assert_paper_execution_allowed()

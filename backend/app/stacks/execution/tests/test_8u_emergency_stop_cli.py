from __future__ import annotations

import json
import os
import subprocess
import sys

from backend.app.stacks.execution.execution_control import (
    ExecutionControl,
    OperatingMode,
)


MODULE = (
    "backend.app.stacks.execution.emergency_stop_cli"
)


def invoke(state, *, confirm=True):
    args = [
        sys.executable,
        "-B",
        "-m",
        MODULE,
        "--state-path",
        str(state),
        "--actor",
        "offline-r47",
        "--reason",
        "Disposable operator-command test",
    ]

    if confirm:
        args.append("--confirm-emergency-stop")

    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=15,
        env={
            **os.environ,
            "PYTHONDONTWRITEBYTECODE": "1",
        },
    )


def create_fixture(tmp_path):
    state = tmp_path / "operating_mode.json"

    control = ExecutionControl(state_path=state)

    control.transition(
        OperatingMode.SIMULATION,
        actor="offline-r47",
        reason="Test setup only",
    )

    return state


def test_operator_stops_real_disposable_controller(tmp_path):
    state = create_fixture(tmp_path)

    result = invoke(state)

    assert result.returncode == 0, result.stderr

    report = json.loads(result.stdout)

    assert report["result"] == "EMERGENCY_STOP_CONFIRMED"
    assert report["paper_execution_enabled"] is False
    assert report["live_execution_enabled"] is False

    fresh = ExecutionControl(state_path=state)

    assert fresh.snapshot().mode == "EMERGENCY_STOP"

    marker = state.with_name(
        state.name + ".stop.pending"
    )

    assert marker.exists()


def test_operator_refuses_missing_confirmation(tmp_path):
    state = create_fixture(tmp_path)

    result = invoke(state, confirm=False)

    assert result.returncode == 2

    assert ExecutionControl(
        state_path=state
    ).snapshot().mode == "SIMULATION"

    assert not state.with_name(
        state.name + ".stop.pending"
    ).exists()


def test_operator_repeat_stop_is_idempotent(tmp_path):
    state = create_fixture(tmp_path)

    first = invoke(state)
    assert first.returncode == 0, first.stderr

    before = ExecutionControl(
        state_path=state
    ).snapshot().revision

    second = invoke(state)
    assert second.returncode == 0, second.stderr

    after = ExecutionControl(
        state_path=state
    ).snapshot().revision

    assert before == after


def test_operator_rejects_group_writable_directory(tmp_path):
    state = create_fixture(tmp_path)

    original = tmp_path.stat().st_mode & 0o777

    try:
        tmp_path.chmod(0o770)

        result = invoke(state)

        assert result.returncode == 1

        assert not state.with_name(
            state.name + ".stop.pending"
        ).exists()

    finally:
        tmp_path.chmod(original)


def test_operator_rejects_relative_path():
    args = [
        sys.executable,
        "-B",
        "-m",
        MODULE,
        "--state-path",
        "relative/operating_mode.json",
        "--actor",
        "offline-r47",
        "--reason",
        "Relative path rejection",
        "--confirm-emergency-stop",
    ]

    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=15,
    )

    assert result.returncode == 1
    assert "UNCONFIRMED" in result.stderr

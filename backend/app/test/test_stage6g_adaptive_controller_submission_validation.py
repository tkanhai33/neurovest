from __future__ import annotations

import importlib
import time

import pytest


MODULE_NAME = (
    "backend.app.stacks.strategy_candidate_sandbox."
    "adaptive_training_controller"
)


def controller_module():
    return importlib.import_module(
        MODULE_NAME
    )


def registry_snapshot(module):
    with module._LOCK:
        return dict(module._CONTROLLERS)


def test_rejects_excessive_rounds_before_queueing():
    module = controller_module()

    before = registry_snapshot(module)

    with pytest.raises(
        ValueError,
        match=(
            "maximum_rounds must be "
            "between 1 and 10"
        ),
    ):
        module.start_adaptive_training_controller(
            confidence_threshold=1.0,
            maximum_rounds=100,
            duration_seconds_per_round=1,
            scope="user",
            owner_user_id="stage6g-user",
            owner_session_id="stage6g-session",
            requested_by_role="user",
        )

    after = registry_snapshot(module)

    assert after == before


def test_rejects_zero_rounds_before_queueing():
    module = controller_module()

    before = registry_snapshot(module)

    with pytest.raises(
        ValueError,
        match=(
            "maximum_rounds must be "
            "between 1 and 10"
        ),
    ):
        module.start_adaptive_training_controller(
            confidence_threshold=1.0,
            maximum_rounds=0,
            duration_seconds_per_round=1,
            scope="user",
            owner_user_id="stage6g-user",
            owner_session_id="stage6g-session",
            requested_by_role="user",
        )

    assert registry_snapshot(module) == before


def test_rejects_invalid_threshold_before_queueing():
    module = controller_module()

    before = registry_snapshot(module)

    with pytest.raises(
        ValueError,
        match=(
            "confidence_threshold must be "
            "between 0 and 1"
        ),
    ):
        module.start_adaptive_training_controller(
            confidence_threshold=1.5,
            maximum_rounds=2,
            duration_seconds_per_round=1,
            scope="user",
            owner_user_id="stage6g-user",
            owner_session_id="stage6g-session",
            requested_by_role="user",
        )

    assert registry_snapshot(module) == before


def test_rejects_invalid_duration_before_queueing():
    module = controller_module()

    before = registry_snapshot(module)

    with pytest.raises(
        ValueError,
        match=(
            "duration_seconds_per_round must "
            "be between 1 and 300"
        ),
    ):
        module.start_adaptive_training_controller(
            confidence_threshold=1.0,
            maximum_rounds=2,
            duration_seconds_per_round=0,
            scope="user",
            owner_user_id="stage6g-user",
            owner_session_id="stage6g-session",
            requested_by_role="user",
        )

    assert registry_snapshot(module) == before


def test_rejects_invalid_timeout_before_queueing():
    module = controller_module()

    before = registry_snapshot(module)

    with pytest.raises(
        ValueError,
        match=(
            "timeout_seconds_per_round must "
            "be greater than 0 and at most 600"
        ),
    ):
        module.start_adaptive_training_controller(
            confidence_threshold=1.0,
            maximum_rounds=2,
            duration_seconds_per_round=1,
            timeout_seconds_per_round=0,
            scope="user",
            owner_user_id="stage6g-user",
            owner_session_id="stage6g-session",
            requested_by_role="user",
        )

    assert registry_snapshot(module) == before


def test_valid_submission_uses_normalized_values(
    monkeypatch,
):
    module = controller_module()

    captured = {}

    class ControlledThread:
        def __init__(
            self,
            *,
            target,
            kwargs,
            name,
            daemon,
        ):
            captured["target"] = target
            captured["kwargs"] = kwargs
            captured["name"] = name
            captured["daemon"] = daemon
            captured["started"] = False

        def start(self):
            captured["started"] = True

    monkeypatch.setattr(
        module,
        "Thread",
        ControlledThread,
    )

    result = (
        module.start_adaptive_training_controller(
            confidence_threshold=0.75,
            maximum_rounds=2,
            duration_seconds_per_round=1,
            scope="user",
            owner_user_id="stage6g-valid-user",
            owner_session_id="stage6g-valid-session",
            requested_by_role="user",
        )
    )

    assert result["status"] == "queued"
    assert result["confidence_threshold"] == 0.75
    assert result["maximum_rounds"] == 2
    assert result["duration_seconds_per_round"] == 1

    assert captured["started"] is True
    assert captured["daemon"] is True
    assert (
        captured["kwargs"]["maximum_rounds"]
        == 2
    )
    assert (
        captured["kwargs"][
            "duration_seconds_per_round"
        ]
        == 1
    )

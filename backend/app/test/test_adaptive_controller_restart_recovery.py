from __future__ import annotations

from pathlib import Path
import importlib
import json


MODULE_NAME = (
    "backend.app.stacks.strategy_candidate_sandbox."
    "adaptive_training_controller"
)


def _controller_module(
    monkeypatch,
    tmp_path: Path,
):
    module = importlib.import_module(
        MODULE_NAME
    )

    root = (
        tmp_path
        / "adaptive_training_controller"
    )

    index = root / "controllers.jsonl"

    monkeypatch.setattr(
        module,
        "_CONTROLLER_ROOT",
        root,
    )

    monkeypatch.setattr(
        module,
        "_CONTROLLER_INDEX",
        index,
    )

    with module._LOCK:
        module._CONTROLLERS.clear()

    return module, index


def _append(
    index: Path,
    payload: dict,
) -> None:
    index.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with index.open(
        "a",
        encoding="utf-8",
    ) as handle:
        handle.write(
            json.dumps(
                payload,
                sort_keys=True,
            )
            + "\n"
        )


def test_completed_controller_restores_from_jsonl(
    monkeypatch,
    tmp_path,
):
    module, index = _controller_module(
        monkeypatch,
        tmp_path,
    )

    controller_id = (
        "adaptive_controller_completed_recovery"
    )

    _append(
        index,
        {
            "controller_id": controller_id,
            "controller_version": 1,
            "scope": "user",
            "owner_user_id": "user-a",
            "owner_session_id": "session-a",
            "requested_by": "user-a",
            "requested_by_role": "user",
            "status": "completed",
            "rounds_completed": 1,
            "stop_reason":
                "maximum_rounds_reached",
            "rounds": [],
        },
    )

    assert (
        module._load_persisted_controllers()
        == 1
    )

    restored = (
        module.get_adaptive_controller(
            controller_id
        )
    )

    assert restored is not None
    assert restored["status"] == "completed"
    assert restored["owner_user_id"] == "user-a"
    assert (
        restored["owner_session_id"]
        == "session-a"
    )


def test_latest_jsonl_snapshot_wins(
    monkeypatch,
    tmp_path,
):
    module, index = _controller_module(
        monkeypatch,
        tmp_path,
    )

    controller_id = (
        "adaptive_controller_latest_snapshot"
    )

    _append(
        index,
        {
            "controller_id": controller_id,
            "scope": "system",
            "status": "running",
            "rounds_completed": 0,
            "rounds": [],
        },
    )

    _append(
        index,
        {
            "controller_id": controller_id,
            "scope": "system",
            "status": "completed",
            "rounds_completed": 2,
            "stop_reason":
                "maximum_rounds_reached",
            "rounds": [],
        },
    )

    assert (
        module._load_persisted_controllers()
        == 1
    )

    restored = (
        module.get_adaptive_controller(
            controller_id
        )
    )

    assert restored is not None
    assert restored["status"] == "completed"
    assert restored["rounds_completed"] == 2


def test_interrupted_controller_becomes_failed(
    monkeypatch,
    tmp_path,
):
    module, index = _controller_module(
        monkeypatch,
        tmp_path,
    )

    controller_id = (
        "adaptive_controller_interrupted"
    )

    _append(
        index,
        {
            "controller_id": controller_id,
            "scope": "user",
            "owner_user_id": "user-b",
            "owner_session_id": "session-b",
            "status": "running",
            "created_at":
                "2026-08-03T00:00:00+00:00",
            "started_at":
                "2026-08-03T00:00:01+00:00",
            "completed_at": None,
            "rounds": [],
        },
    )

    assert (
        module._load_persisted_controllers()
        == 1
    )

    restored = (
        module.get_adaptive_controller(
            controller_id
        )
    )

    assert restored is not None
    assert restored["status"] == "failed"
    assert (
        restored["stop_reason"]
        == "interrupted_by_runtime_restart"
    )


def test_invalid_jsonl_lines_are_ignored(
    monkeypatch,
    tmp_path,
):
    module, index = _controller_module(
        monkeypatch,
        tmp_path,
    )

    index.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    index.write_text(
        "\n".join(
            [
                "{invalid-json",
                json.dumps(
                    {
                        "controller_id":
                            "not_an_adaptive_controller",
                        "status": "completed",
                    }
                ),
                json.dumps(
                    {
                        "controller_id":
                            "adaptive_controller_ownerless",
                        "scope": "user",
                        "owner_user_id": "",
                        "status": "completed",
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    assert (
        module._load_persisted_controllers()
        == 0
    )

    assert module._CONTROLLERS == {}


def test_wrapped_controller_record_is_supported(
    monkeypatch,
    tmp_path,
):
    module, index = _controller_module(
        monkeypatch,
        tmp_path,
    )

    controller_id = (
        "adaptive_controller_wrapped_record"
    )

    _append(
        index,
        {
            "controller": {
                "controller_id": controller_id,
                "scope": "system",
                "status": "completed",
                "rounds": [],
            }
        },
    )

    assert (
        module._load_persisted_controllers()
        == 1
    )

    assert (
        module.get_adaptive_controller(
            controller_id
        )
        is not None
    )


def test_loaded_record_preserves_owner_fields(
    monkeypatch,
    tmp_path,
):
    module, index = _controller_module(
        monkeypatch,
        tmp_path,
    )

    controller_id = (
        "adaptive_controller_owner_fields"
    )

    _append(
        index,
        {
            "controller_id": controller_id,
            "scope": "user",
            "owner_user_id": "owner-user",
            "owner_session_id": "owner-session",
            "requested_by": "owner-user",
            "requested_by_role": "user",
            "status": "completed",
            "rounds": [],
        },
    )

    assert (
        module._load_persisted_controllers()
        == 1
    )

    restored = (
        module.get_adaptive_controller(
            controller_id
        )
    )

    assert restored is not None
    assert (
        restored["owner_user_id"]
        == "owner-user"
    )
    assert (
        restored["owner_session_id"]
        == "owner-session"
    )
    assert (
        restored["requested_by_role"]
        == "user"
    )


def test_recovery_does_not_enable_execution(
    monkeypatch,
    tmp_path,
):
    module, index = _controller_module(
        monkeypatch,
        tmp_path,
    )

    status = (
        module.adaptive_controller_status()
    )

    assert (
        status["automatic_strategy_promotion"]
        is False
    )
    assert (
        status["paper_order_creation"]
        is False
    )
    assert status["portfolio_mutation"] is False
    assert status["database_writes"] is False
    assert status["model_mutation"] is False
    assert status["broker_execution"] is False
    assert status["live_execution"] is False

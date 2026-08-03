from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import time

import pytest

from backend.app.stacks.strategy_candidate_sandbox import (
    adaptive_training_controller as controller,
)


def _record(
    *,
    controller_id: str,
    user_id: str,
    session_id: str,
) -> dict:
    return {
        "controller_id":
            controller_id,

        "controller_version":
            1,

        "status":
            "queued",

        "created_at":
            "2026-08-03T00:00:00+00:00",

        "started_at":
            None,

        "completed_at":
            None,

        "confidence_threshold":
            0.75,

        "maximum_rounds":
            2,

        "duration_seconds_per_round":
            1,

        "requested_by":
            user_id,

        "requested_by_role":
            "user",

        "scope":
            "user",

        "owner_user_id":
            user_id,

        "owner_session_id":
            session_id,

        "rounds_completed":
            0,

        "stop_reason":
            None,

        "best_round_number":
            None,

        "best_average_confidence":
            None,

        "best_candidate_id":
            None,

        "best_training_window_id":
            None,

        "rounds":
            [],

        "safety": {
            "historical_training_only":
                True,

            "automatic_strategy_promotion":
                False,

            "paper_order_creation":
                False,

            "portfolio_mutation":
                False,

            "database_writes":
                False,

            "model_mutation":
                False,

            "broker_execution":
                False,

            "live_execution":
                False,
        },
    }


@pytest.fixture(autouse=True)
def isolated_controllers():
    with controller._LOCK:
        original = deepcopy(
            controller._CONTROLLERS
        )

        controller._CONTROLLERS.clear()

    yield

    with controller._LOCK:
        controller._CONTROLLERS.clear()
        controller._CONTROLLERS.update(
            original
        )


def test_owner_can_read_own_controller() -> None:
    record = _record(
        controller_id="adaptive_controller_owner",
        user_id="user-a",
        session_id="session-a",
    )

    with controller._LOCK:
        controller._CONTROLLERS[
            record["controller_id"]
        ] = record

    result = (
        controller
        .get_adaptive_controller_for_owner(
            controller_id=(
                record["controller_id"]
            ),
            owner_user_id="user-a",
            owner_session_id="session-a",
        )
    )

    assert result is not None
    assert result["controller_id"] == (
        record["controller_id"]
    )


def test_cross_user_controller_read_is_hidden() -> None:
    record = _record(
        controller_id="adaptive_controller_private",
        user_id="user-a",
        session_id="session-a",
    )

    with controller._LOCK:
        controller._CONTROLLERS[
            record["controller_id"]
        ] = record

    assert (
        controller
        .get_adaptive_controller_for_owner(
            controller_id=(
                record["controller_id"]
            ),
            owner_user_id="user-b",
            owner_session_id="session-b",
        )
        is None
    )


def test_same_user_different_session_is_hidden() -> None:
    record = _record(
        controller_id="adaptive_controller_session",
        user_id="user-a",
        session_id="session-a",
    )

    with controller._LOCK:
        controller._CONTROLLERS[
            record["controller_id"]
        ] = record

    assert (
        controller
        .get_adaptive_controller_for_owner(
            controller_id=(
                record["controller_id"]
            ),
            owner_user_id="user-a",
            owner_session_id="session-b",
        )
        is None
    )


def test_owner_list_contains_only_exact_owner() -> None:
    records = [
        _record(
            controller_id="adaptive_controller_a",
            user_id="user-a",
            session_id="session-a",
        ),
        _record(
            controller_id="adaptive_controller_b",
            user_id="user-b",
            session_id="session-b",
        ),
        _record(
            controller_id="adaptive_controller_c",
            user_id="user-a",
            session_id="session-c",
        ),
    ]

    with controller._LOCK:
        for record in records:
            controller._CONTROLLERS[
                record["controller_id"]
            ] = record

    result = (
        controller
        .list_adaptive_controllers_for_owner(
            owner_user_id="user-a",
            owner_session_id="session-a",
            limit=20,
        )
    )

    assert [
        item["controller_id"]
        for item in result
    ] == [
        "adaptive_controller_a",
    ]


def test_user_scope_requires_both_owner_values() -> None:
    with pytest.raises(
        ValueError,
        match="owner user ID",
    ):
        controller.start_adaptive_training_controller(
            confidence_threshold=0.75,
            maximum_rounds=2,
            scope="user",
            owner_user_id=None,
            owner_session_id="session-a",
        )

    with pytest.raises(
        ValueError,
        match="owner session ID",
    ):
        controller.start_adaptive_training_controller(
            confidence_threshold=0.75,
            maximum_rounds=2,
            scope="user",
            owner_user_id="user-a",
            owner_session_id=None,
        )


def test_system_scope_rejects_customer_ownership() -> None:
    with pytest.raises(
        ValueError,
        match="customer owner",
    ):
        controller.start_adaptive_training_controller(
            confidence_threshold=0.75,
            maximum_rounds=2,
            scope="system",
            owner_user_id="user-a",
            owner_session_id=None,
        )


def test_async_start_derives_owned_queued_record(
    monkeypatch,
) -> None:
    def fake_run(**kwargs):
        controller_id = kwargs[
            "controller_id"
        ]

        with controller._LOCK:
            existing = (
                controller._CONTROLLERS[
                    controller_id
                ]
            )

            existing["status"] = "completed"
            existing["started_at"] = (
                "2026-08-03T00:00:01+00:00"
            )
            existing["completed_at"] = (
                "2026-08-03T00:00:02+00:00"
            )
            existing["stop_reason"] = (
                "maximum_rounds_reached"
            )

        return deepcopy(
            existing
        )

    monkeypatch.setattr(
        controller,
        "run_adaptive_training_controller",
        fake_run,
    )

    queued = (
        controller
        .start_adaptive_training_controller(
            confidence_threshold=0.75,
            maximum_rounds=2,
            duration_seconds_per_round=1,
            requested_by="user-a",
            scope="user",
            owner_user_id="user-a",
            owner_session_id="session-a",
            requested_by_role="user",
        )
    )

    assert queued["scope"] == "user"
    assert queued["owner_user_id"] == "user-a"
    assert (
        queued["owner_session_id"]
        == "session-a"
    )

    deadline = time.monotonic() + 5

    final = None

    while time.monotonic() < deadline:
        final = (
            controller
            .get_adaptive_controller_for_owner(
                controller_id=(
                    queued["controller_id"]
                ),
                owner_user_id="user-a",
                owner_session_id="session-a",
            )
        )

        if (
            final is not None
            and final.get("status")
            == "completed"
        ):
            break

        time.sleep(0.01)

    assert final is not None
    assert final["status"] == "completed"


def test_api_routes_use_server_principal_ownership() -> None:
    source = Path(
        "backend/app/main.py"
    ).read_text(
        encoding="utf-8",
    )

    required = (
        '"/api/v1/training/adaptive"',
        '"/api/v1/training/adaptive/{controller_id}"',
        "require_authenticated_principal",
        "_training_principal_subject",
        "_training_principal_session",
        "get_adaptive_controller_for_owner",
        "list_adaptive_controllers_for_owner",
        "start_adaptive_training_controller",
    )

    for marker in required:
        assert marker in source

    route_section = source[
        source.index(
            "async def "
            "start_authenticated_user_"
            "adaptive_controller"
        ):
        source.index(
            "@app.get(\n"
            '    "/api/v1/admin/training/status"'
        )
    ]

    assert 'scope="user"' in route_section
    assert "owner_user_id=(" in route_section
    assert "owner_session_id=(" in route_section
    assert "client_owner_user_id" not in route_section
    assert "client_owner_session_id" not in route_section


def test_safety_boundaries_remain_disabled() -> None:
    status = (
        controller
        .adaptive_controller_status()
    )

    assert (
        status[
            "automatic_strategy_promotion"
        ]
        is False
    )

    assert (
        status[
            "paper_order_creation"
        ]
        is False
    )

    assert (
        status[
            "portfolio_mutation"
        ]
        is False
    )

    assert (
        status[
            "database_writes"
        ]
        is False
    )

    assert (
        status[
            "model_mutation"
        ]
        is False
    )

    assert (
        status[
            "broker_execution"
        ]
        is False
    )

    assert (
        status[
            "live_execution"
        ]
        is False
    )

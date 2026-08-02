from pathlib import Path
from unittest.mock import patch
import time

from backend.app.stacks.chat_public.chat_intent_regex import (
    detect_chat_intent,
)

from backend.app.stacks.chat_public.chat_runtime import (
    handle_chat_message,
)

from backend.app.stacks.strategy_candidate_sandbox.L4_runtime_orchestration.bounded_training_runtime import (
    discover_canadian_datasets,
    get_training_session,
    start_bounded_training_session,
    training_runtime_status,
)


MAIN = Path(
    "backend/app/main.py"
)

SERVICE = Path(
    "backend/app/stacks/"
    "strategy_candidate_sandbox/"
    "L4_runtime_orchestration/"
    "bounded_training_runtime.py"
)


def test_exact_training_prompt_is_deterministic() -> None:
    intent = detect_chat_intent(
        "Run a training session for 2 minutes "
        "on all Canadian symbols."
    )

    assert (
        intent.intent
        == "run_training_session"
    )

    assert intent.family == "TRAINING"

    assert (
        intent.subtype
        == "bounded_canadian_training"
    )

    assert intent.confidence == 1.0


def test_seconds_training_prompt_is_deterministic() -> None:
    intent = detect_chat_intent(
        "Start a training session for "
        "30 seconds on Canadian symbols."
    )

    assert (
        intent.intent
        == "run_training_session"
    )

    assert intent.family == "TRAINING"


def test_canadian_historical_repository_is_found() -> None:
    datasets = (
        discover_canadian_datasets()
    )

    symbols = {
        item["symbol"]
        for item in datasets
    }

    assert len(datasets) >= 55
    assert "RY.TO" in symbols
    assert "TD.TO" in symbols
    assert "VFV.TO" in symbols
    assert "XIU.TO" in symbols


def test_two_minute_chat_duration_is_forwarded() -> None:
    fake_record = {
        "run_id":
            "training_test_0001",
        "duration_seconds":
            120,
        "status":
            "queued",
    }

    with patch(
        "backend.app.stacks.chat_public."
        "chat_runtime."
        "start_bounded_training_session",
        return_value=fake_record,
    ) as start:
        result = handle_chat_message(
            "Run a training session for "
            "2 minutes on all Canadian symbols."
        )

    start.assert_called_once_with(
        duration_seconds=120,
        universe="canada",
        requested_by=(
            "authenticated_chat"
        ),
        source="chat",
    )

    assert result["status"] == "ok"

    assert (
        result["intent"]
        == "run_training_session"
    )

    assert (
        result["provider"]
        == (
            "neurovest_bounded_"
            "training_runtime"
        )
    )

    assert (
        result["tool_truth_state"]
        == "grounded"
    )


def test_thirty_second_chat_duration_is_forwarded() -> None:
    fake_record = {
        "run_id":
            "training_test_0030",
        "duration_seconds":
            30,
        "status":
            "queued",
    }

    with patch(
        "backend.app.stacks.chat_public."
        "chat_runtime."
        "start_bounded_training_session",
        return_value=fake_record,
    ) as start:
        handle_chat_message(
            "Start a training session for "
            "30 seconds on Canadian symbols."
        )

    start.assert_called_once_with(
        duration_seconds=30,
        universe="canada",
        requested_by=(
            "authenticated_chat"
        ),
        source="chat",
    )


def test_one_second_session_completes() -> None:
    record = (
        start_bounded_training_session(
            duration_seconds=1,
            universe="canada",
            requested_by="pytest",
            source="test",
        )
    )

    run_id = record["run_id"]
    deadline = time.monotonic() + 10
    result = None

    while time.monotonic() < deadline:
        result = get_training_session(
            run_id
        )

        if (
            result
            and result.get("status")
            in {
                "completed",
                "failed",
            }
        ):
            break

        time.sleep(0.05)

    assert result is not None
    assert result["status"] == "completed"
    assert result["progress_percent"] == 100.0
    assert result["eligible_symbol_count"] >= 55
    assert result["rows_evaluated"] > 0
    assert result["cycles"] > 0

    assert result["executed_trades"] == 0
    assert result["paper_orders_created"] == 0
    assert result["portfolio_mutations"] == 0
    assert result["database_rows_written"] == 0
    assert result["strategy_promotions"] == 0
    assert result["broker_requests"] == 0
    assert result["live_orders"] == 0


def test_runtime_status_is_fail_closed() -> None:
    status = training_runtime_status()

    assert status["runtime_enabled"] is True
    assert status["canadian_dataset_count"] >= 55

    safety = status["safety"]

    assert (
        safety[
            "historical_csv_read_only"
        ]
        is True
    )

    assert safety["sandbox_only"] is True

    assert (
        safety[
            "paper_orders_enabled"
        ]
        is False
    )

    assert (
        safety[
            "portfolio_mutation_enabled"
        ]
        is False
    )

    assert (
        safety[
            "database_writes_enabled"
        ]
        is False
    )

    assert (
        safety[
            "strategy_mutation_enabled"
        ]
        is False
    )

    assert (
        safety[
            "promotion_enabled"
        ]
        is False
    )

    assert (
        safety[
            "broker_execution_enabled"
        ]
        is False
    )

    assert (
        safety[
            "live_execution_enabled"
        ]
        is False
    )


def test_training_role_routes_are_exposed() -> None:
    source = MAIN.read_text(
        encoding="utf-8",
    )

    user_routes = (
        '"/api/v1/training/runs"',
        '"/api/v1/training/runs/{run_id}"',
    )

    admin_observability_routes = (
        '"/api/v1/admin/training/status"',
        '"/api/v1/admin/training/health"',
        '"/api/v1/admin/training/failures"',
    )

    developer_routes = (
        '"/api/v1/developer/training/runs"',
        '"/api/v1/developer/training/runs/{run_id}"',
    )

    for route in (
        user_routes
        + admin_observability_routes
        + developer_routes
    ):
        assert route in source

    assert (
        '@app.post(\n'
        '    "/api/v1/admin/training/runs"'
        not in source
    )

    assert (
        '@app.get(\n'
        '    "/api/v1/admin/training/runs"'
        not in source
    )

    assert (
        '"/api/v1/admin/training/runs/{run_id}"'
        not in source
    )

    assert (
        "require_administrative_principal"
        in source
    )

    assert (
        "_require_developer_training_role"
        in source
    )

def test_service_contains_no_execution_calls() -> None:
    source = SERVICE.read_text(
        encoding="utf-8",
    )

    forbidden = (
        "execute_trade(",
        "place_order(",
        "submit_order(",
        "rebalance_portfolio(",
        "session.add(",
        "session.execute(",
        "session.commit(",
        "OperatingMode.LIVE",
        "live_execution_enabled=True",
        "broker_execution_enabled=True",
        "promotion_enabled=True",
    )

    for value in forbidden:
        assert value not in source

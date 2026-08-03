"""
Bounded adaptive multi-round training controller.

This controller may:
- launch bounded historical training rounds;
- compare persisted confidence against the prior baseline;
- create a new immutable candidate contract for the next round;
- create a new immutable historical-window contract for the next round;
- stop at a confidence threshold or maximum-round boundary.

This controller may not:
- promote strategies;
- mutate models;
- create paper or live orders;
- call brokers;
- modify customer portfolios.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from threading import RLock, Thread
from typing import Any
from uuid import uuid4
from datetime import UTC, datetime
import json
import math
import time

from backend.app.stacks.strategy_candidate_sandbox.training_candidate_contract import (
    build_training_candidate_contract,
    validate_training_candidate_contract,
)

from backend.app.stacks.strategy_candidate_sandbox.training_window_contract import (
    validate_training_window_contract,
)

from backend.app.stacks.strategy_candidate_sandbox.persistent_learning_ledger import (
    get_learning_contribution,
)

from backend.app.stacks.strategy_candidate_sandbox.L4_runtime_orchestration.bounded_training_runtime import (
    get_training_session,
    start_bounded_training_session,
)


_REPO_ROOT = Path(__file__).resolve().parents[4]

_CONTROLLER_ROOT = (
    _REPO_ROOT
    / "runtime"
    / "strategy_candidate_sandbox"
    / "adaptive_training_controller"
)

_CONTROLLER_INDEX = (
    _CONTROLLER_ROOT
    / "controllers.jsonl"
)

_LOCK = RLock()

_CONTROLLERS: dict[
    str,
    dict[str, Any],
] = {}

_TERMINAL_RUN_STATES = {
    "completed",
    "failed",
    "cancelled",
    "canceled",
}

_MINIMUM_ROUNDS = 1
_MAXIMUM_ROUNDS = 10

_MINIMUM_THRESHOLD = 0.0
_MAXIMUM_THRESHOLD = 1.0

_MINIMUM_SIGNAL_STRENGTH = 0.0001
_MAXIMUM_SIGNAL_STRENGTH = 0.50


def _utc_now() -> str:
    return datetime.now(
        UTC
    ).isoformat()


def _finite_float(
    value: Any,
    *,
    default: float = 0.0,
) -> float:
    try:
        number = float(value)
    except (
        TypeError,
        ValueError,
    ):
        return default

    if not math.isfinite(number):
        return default

    return number


def _bounded_int(
    value: Any,
    *,
    minimum: int,
    maximum: int,
    name: str,
) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
    ):
        raise ValueError(
            f"{name} must be an integer"
        )

    if not minimum <= value <= maximum:
        raise ValueError(
            f"{name} must be between "
            f"{minimum} and {maximum}"
        )

    return value


def _write_controller_record(
    record: dict[str, Any],
) -> None:
    _CONTROLLER_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    controller_id = str(
        record["controller_id"]
    )

    controller_path = (
        _CONTROLLER_ROOT
        / f"{controller_id}.json"
    )

    controller_path.write_text(
        json.dumps(
            record,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )

    with _CONTROLLER_INDEX.open(
        "a",
        encoding="utf-8",
    ) as handle:
        handle.write(
            json.dumps(
                record,
                sort_keys=True,
                ensure_ascii=False,
                default=str,
            )
            + "\n"
        )


def _update_controller(
    controller_id: str,
    **updates: Any,
) -> dict[str, Any]:
    with _LOCK:
        record = _CONTROLLERS.get(
            controller_id
        )

        if record is None:
            raise KeyError(
                "adaptive controller not found"
            )

        record.update(
            updates
        )

        snapshot = deepcopy(
            record
        )

    _write_controller_record(
        snapshot
    )

    return snapshot


def _wait_for_training_run(
    run_id: str,
    *,
    timeout_seconds: float,
) -> dict[str, Any]:
    deadline = (
        time.monotonic()
        + timeout_seconds
    )

    while time.monotonic() < deadline:
        record = get_training_session(
            run_id
        )

        if (
            isinstance(record, dict)
            and str(
                record.get("status")
                or ""
            ).lower()
            in _TERMINAL_RUN_STATES
        ):
            return record

        time.sleep(0.05)

    raise TimeoutError(
        "bounded training round timed out"
    )


def _round_metrics(
    record: dict[str, Any],
) -> dict[str, Any]:
    return {
        "average_confidence":
            _finite_float(
                record.get(
                    "average_confidence"
                )
            ),

        "average_confidence_delta":
            _finite_float(
                record.get(
                    "average_confidence_delta"
                )
            ),

        "confidence_baseline_available":
            bool(
                record.get(
                    "confidence_baseline_available"
                )
            ),

        "baseline_contribution_id":
            record.get(
                "baseline_contribution_id"
            ),

        "symbols_compared":
            int(
                record.get(
                    "symbols_compared"
                )
                or 0
            ),

        "symbols_improved":
            int(
                record.get(
                    "symbols_improved"
                )
                or 0
            ),

        "symbols_declined":
            int(
                record.get(
                    "symbols_declined"
                )
                or 0
            ),

        "symbols_unchanged":
            int(
                record.get(
                    "symbols_unchanged"
                )
                or 0
            ),

        "all_compared_symbols_improved":
            bool(
                record.get(
                    "all_compared_symbols_improved"
                )
            ),

        "rows_evaluated":
            int(
                record.get(
                    "rows_evaluated"
                )
                or 0
            ),

        "valid_learning_artifacts":
            int(
                record.get(
                    "valid_learning_artifacts"
                )
                or 0
            ),

        "symbols_with_valid_confidence":
            int(
                record.get(
                    "symbols_with_valid_confidence"
                )
                or 0
            ),
    }


def _next_candidate(
    *,
    current_candidate: dict[str, Any],
    metrics: dict[str, Any],
    next_round_number: int,
) -> dict[str, Any]:
    if not validate_training_candidate_contract(
        current_candidate
    ):
        raise ValueError(
            "current candidate contract is invalid"
        )

    short_rows = int(
        current_candidate[
            "short_lookback_rows"
        ]
    )

    long_rows = int(
        current_candidate[
            "long_lookback_rows"
        ]
    )

    minimum_strength = float(
        current_candidate[
            "minimum_signal_strength"
        ]
    )

    confidence_delta = _finite_float(
        metrics.get(
            "average_confidence_delta"
        )
    )

    declined = int(
        metrics.get(
            "symbols_declined"
        )
        or 0
    )

    improved = int(
        metrics.get(
            "symbols_improved"
        )
        or 0
    )

    if confidence_delta > 0 and improved >= declined:
        minimum_strength *= 0.90

        if next_round_number % 2 == 0:
            short_rows = max(
                2,
                short_rows - 1,
            )
        else:
            long_rows = min(
                500,
                long_rows + 2,
            )

    else:
        minimum_strength *= 1.10

        if next_round_number % 2 == 0:
            short_rows = min(
                100,
                short_rows + 1,
            )
        else:
            long_rows = max(
                short_rows + 1,
                long_rows - 2,
            )

    minimum_strength = min(
        _MAXIMUM_SIGNAL_STRENGTH,
        max(
            _MINIMUM_SIGNAL_STRENGTH,
            minimum_strength,
        ),
    )

    if short_rows >= long_rows:
        long_rows = short_rows + 1

    return (
        build_training_candidate_contract(
            decision_rule=str(
                current_candidate[
                    "decision_rule"
                ]
            ),
            short_lookback_rows=(
                short_rows
            ),
            long_lookback_rows=(
                long_rows
            ),
            minimum_signal_strength=(
                minimum_strength
            ),
            created_from="qualification",
        )
        .to_dict()
    )


def _next_window_values(
    *,
    current_window: dict[str, Any],
    next_round_number: int,
) -> dict[str, Any]:
    if not validate_training_window_contract(
        current_window
    ):
        raise ValueError(
            "current window contract is invalid"
        )

    lookback_rows = current_window.get(
        "lookback_rows"
    )

    current_offset = int(
        current_window[
            "row_offset"
        ]
    )

    if lookback_rows is None:
        offset_step = 250
    else:
        offset_step = max(
            2,
            int(lookback_rows),
        )

    return {
        "window_start":
            current_window.get(
                "window_start"
            ),

        "window_end":
            current_window.get(
                "window_end"
            ),

        "lookback_rows":
            lookback_rows,

        "row_offset":
            current_offset
            + offset_step,

        "round_number":
            next_round_number,

        "maximum_rounds":
            int(
                current_window[
                    "maximum_rounds"
                ]
            ),
    }


def start_adaptive_training_controller(
    *,
    confidence_threshold: float,
    maximum_rounds: int,
    duration_seconds_per_round: int = 1,
    initial_candidate: dict[str, Any] | None = None,
    window_start: str | None = None,
    window_end: str | None = None,
    lookback_rows: int | None = 120,
    row_offset: int = 0,
    requested_by: str = "adaptive_training_controller",
    timeout_seconds_per_round: float = 120.0,
    scope: str = "system",
    owner_user_id: str | None = None,
    owner_session_id: str | None = None,
    requested_by_role: str | None = None,
) -> dict[str, Any]:
    resolved_scope = str(
        scope
        or "system"
    ).strip().lower()

    resolved_owner_user_id = (
        str(owner_user_id).strip()
        if owner_user_id is not None
        else None
    ) or None

    resolved_owner_session_id = (
        str(owner_session_id).strip()
        if owner_session_id is not None
        else None
    ) or None

    if resolved_scope not in {
        "user",
        "system",
    }:
        raise ValueError(
            "Adaptive controller scope must be USER or SYSTEM."
        )

    if resolved_scope == "user":
        if not resolved_owner_user_id:
            raise ValueError(
                "USER adaptive training requires an owner user ID."
            )

        if not resolved_owner_session_id:
            raise ValueError(
                "USER adaptive training requires an owner session ID."
            )

    if resolved_scope == "system":
        if resolved_owner_user_id is not None:
            raise ValueError(
                "SYSTEM adaptive training cannot have a customer owner."
            )

        if resolved_owner_session_id is not None:
            raise ValueError(
                "SYSTEM adaptive training cannot have a customer session."
            )

    controller_id = (
        "adaptive_controller_"
        + uuid4().hex[:24]
    )

    queued = {
        "controller_id":
            controller_id,

        "controller_version":
            1,

        "status":
            "queued",

        "created_at":
            _utc_now(),

        "started_at":
            None,

        "completed_at":
            None,

        "confidence_threshold":
            float(confidence_threshold),

        "maximum_rounds":
            int(maximum_rounds),

        "duration_seconds_per_round":
            int(duration_seconds_per_round),

        "requested_by":
            requested_by,

        "requested_by_role":
            (
                str(requested_by_role).strip().lower()
                if requested_by_role is not None
                else None
            ),

        "scope":
            resolved_scope,

        "owner_user_id":
            resolved_owner_user_id,

        "owner_session_id":
            resolved_owner_session_id,

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

    with _LOCK:
        _CONTROLLERS[
            controller_id
        ] = queued

    _write_controller_record(
        deepcopy(queued)
    )

    thread = Thread(
        target=run_adaptive_training_controller,
        kwargs={
            "confidence_threshold":
                confidence_threshold,

            "maximum_rounds":
                maximum_rounds,

            "duration_seconds_per_round":
                duration_seconds_per_round,

            "initial_candidate":
                initial_candidate,

            "window_start":
                window_start,

            "window_end":
                window_end,

            "lookback_rows":
                lookback_rows,

            "row_offset":
                row_offset,

            "requested_by":
                requested_by,

            "timeout_seconds_per_round":
                timeout_seconds_per_round,

            "scope":
                resolved_scope,

            "owner_user_id":
                resolved_owner_user_id,

            "owner_session_id":
                resolved_owner_session_id,

            "requested_by_role":
                requested_by_role,

            "controller_id":
                controller_id,
        },
        name=controller_id,
        daemon=True,
    )

    thread.start()

    return deepcopy(
        queued
    )


def get_adaptive_controller_for_owner(
    *,
    controller_id: str,
    owner_user_id: str,
    owner_session_id: str,
) -> dict[str, Any] | None:
    record = get_adaptive_controller(
        controller_id
    )

    if record is None:
        return None

    if record.get("scope") != "user":
        return None

    if (
        record.get("owner_user_id")
        != str(owner_user_id)
    ):
        return None

    if (
        record.get("owner_session_id")
        != str(owner_session_id)
    ):
        return None

    return record


def list_adaptive_controllers_for_owner(
    *,
    owner_user_id: str,
    owner_session_id: str,
    limit: int = 20,
) -> list[dict[str, Any]]:
    resolved_limit = max(
        1,
        min(
            int(limit),
            100,
        ),
    )

    with _LOCK:
        records = [
            deepcopy(record)
            for record
            in _CONTROLLERS.values()
            if (
                record.get("scope")
                == "user"
                and record.get(
                    "owner_user_id"
                )
                == str(owner_user_id)
                and record.get(
                    "owner_session_id"
                )
                == str(owner_session_id)
            )
        ]

    records.sort(
        key=lambda item: str(
            item.get("created_at")
            or ""
        ),
        reverse=True,
    )

    return records[
        :resolved_limit
    ]


def get_adaptive_controller(
    controller_id: str,
) -> dict[str, Any] | None:
    with _LOCK:
        record = _CONTROLLERS.get(
            str(controller_id)
        )

        return (
            deepcopy(record)
            if record is not None
            else None
        )


def adaptive_controller_status() -> dict[str, Any]:
    with _LOCK:
        total = len(
            _CONTROLLERS
        )

        running = sum(
            1
            for item in _CONTROLLERS.values()
            if item.get("status")
            == "running"
        )

    return {
        "controller_enabled":
            True,

        "controller_version":
            1,

        "controllers_in_memory":
            total,

        "controllers_running":
            running,

        "maximum_rounds_allowed":
            _MAXIMUM_ROUNDS,

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
    }


def run_adaptive_training_controller(
    *,
    confidence_threshold: float,
    maximum_rounds: int,
    duration_seconds_per_round: int = 1,
    initial_candidate: dict[str, Any] | None = None,
    window_start: str | None = None,
    window_end: str | None = None,
    lookback_rows: int | None = 120,
    row_offset: int = 0,
    requested_by: str = (
        "adaptive_training_controller"
    ),
    timeout_seconds_per_round: float = 120.0,
    scope: str = "system",
    owner_user_id: str | None = None,
    owner_session_id: str | None = None,
    requested_by_role: str | None = None,
    controller_id: str | None = None,
) -> dict[str, Any]:
    threshold = _finite_float(
        confidence_threshold,
        default=-1.0,
    )

    if not (
        _MINIMUM_THRESHOLD
        <= threshold
        <= _MAXIMUM_THRESHOLD
    ):
        raise ValueError(
            "confidence_threshold must be "
            "between 0 and 1"
        )

    resolved_maximum_rounds = (
        _bounded_int(
            maximum_rounds,
            minimum=_MINIMUM_ROUNDS,
            maximum=_MAXIMUM_ROUNDS,
            name="maximum_rounds",
        )
    )

    resolved_duration = _bounded_int(
        duration_seconds_per_round,
        minimum=1,
        maximum=300,
        name="duration_seconds_per_round",
    )

    if (
        timeout_seconds_per_round
        <= 0
        or timeout_seconds_per_round
        > 600
    ):
        raise ValueError(
            "timeout_seconds_per_round must "
            "be greater than 0 and at most 600"
        )

    resolved_scope = str(
        scope
        or "system"
    ).strip().lower()

    if resolved_scope not in {
        "user",
        "system",
    }:
        raise ValueError(
            "Adaptive controller scope must be USER or SYSTEM."
        )

    resolved_owner_user_id = (
        str(owner_user_id).strip()
        if owner_user_id is not None
        else None
    ) or None

    resolved_owner_session_id = (
        str(owner_session_id).strip()
        if owner_session_id is not None
        else None
    ) or None

    resolved_requested_by_role = (
        str(requested_by_role).strip().lower()
        if requested_by_role is not None
        else None
    ) or None

    if resolved_scope == "user":
        if not resolved_owner_user_id:
            raise ValueError(
                "USER adaptive training requires an owner user ID."
            )

        if not resolved_owner_session_id:
            raise ValueError(
                "USER adaptive training requires an owner session ID."
            )

    if resolved_scope == "system":
        if resolved_owner_user_id is not None:
            raise ValueError(
                "SYSTEM adaptive training cannot have a customer owner."
            )

        if resolved_owner_session_id is not None:
            raise ValueError(
                "SYSTEM adaptive training cannot have a customer session."
            )

    if initial_candidate is None:
        candidate = (
            build_training_candidate_contract(
                created_from="qualification",
            )
            .to_dict()
        )
    else:
        candidate = dict(
            initial_candidate
        )

    if not validate_training_candidate_contract(
        candidate
    ):
        raise ValueError(
            "initial candidate contract is invalid"
        )

    resolved_controller_id = (
        str(controller_id).strip()
        if controller_id is not None
        else ""
    )

    if not resolved_controller_id:
        resolved_controller_id = (
            "adaptive_controller_"
            + uuid4().hex[:24]
        )

    controller_id = resolved_controller_id

    controller = {
        "controller_id":
            controller_id,

        "controller_version":
            1,

        "status":
            "running",

        "created_at":
            _utc_now(),

        "started_at":
            _utc_now(),

        "completed_at":
            None,

        "confidence_threshold":
            threshold,

        "maximum_rounds":
            resolved_maximum_rounds,

        "duration_seconds_per_round":
            resolved_duration,

        "requested_by":
            requested_by,

        "requested_by_role":
            resolved_requested_by_role,

        "scope":
            resolved_scope,

        "owner_user_id":
            resolved_owner_user_id,

        "owner_session_id":
            resolved_owner_session_id,

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

    with _LOCK:
        _CONTROLLERS[
            controller_id
        ] = controller

    _write_controller_record(
        deepcopy(controller)
    )

    current_window_values = {
        "window_start":
            window_start,

        "window_end":
            window_end,

        "lookback_rows":
            lookback_rows,

        "row_offset":
            row_offset,

        "round_number":
            1,

        "maximum_rounds":
            resolved_maximum_rounds,
    }

    best_confidence = -1.0
    best_round_number = None
    best_candidate_id = None
    best_window_id = None

    try:
        for round_number in range(
            1,
            resolved_maximum_rounds + 1,
        ):
            started = (
                start_bounded_training_session(
                    duration_seconds=(
                        resolved_duration
                    ),
                    universe="canada",
                    requested_by=requested_by,
                    source=(
                        "adaptive_controller"
                    ),
                    scope=resolved_scope,
                    owner_user_id=(
                        resolved_owner_user_id
                    ),
                    owner_session_id=(
                        resolved_owner_session_id
                    ),
                    requested_by_role=(
                        resolved_requested_by_role
                        or (
                            "user"
                            if resolved_scope == "user"
                            else "developer"
                        )
                    ),
                    training_candidate=(
                        candidate
                    ),
                    window_start=(
                        current_window_values[
                            "window_start"
                        ]
                    ),
                    window_end=(
                        current_window_values[
                            "window_end"
                        ]
                    ),
                    lookback_rows=(
                        current_window_values[
                            "lookback_rows"
                        ]
                    ),
                    row_offset=(
                        current_window_values[
                            "row_offset"
                        ]
                    ),
                    round_number=(
                        round_number
                    ),
                    maximum_rounds=(
                        resolved_maximum_rounds
                    ),
                )
            )

            run_id = str(
                started[
                    "run_id"
                ]
            )

            completed = (
                _wait_for_training_run(
                    run_id,
                    timeout_seconds=(
                        timeout_seconds_per_round
                    ),
                )
            )

            run_status = str(
                completed.get("status")
                or ""
            ).lower()

            contribution = completed.get(
                "sanitized_learning_contribution"
            )

            contribution_id = (
                contribution.get(
                    "contribution_id"
                )
                if isinstance(
                    contribution,
                    dict,
                )
                else None
            )

            persisted_contribution = (
                get_learning_contribution(
                    str(contribution_id)
                )
                if contribution_id
                else None
            )

            metrics = _round_metrics(
                completed
            )

            round_record = {
                "round_number":
                    round_number,

                "run_id":
                    run_id,

                "status":
                    run_status,

                "candidate_id":
                    completed.get(
                        "candidate_id"
                    ),

                "training_candidate":
                    deepcopy(
                        completed.get(
                            "training_candidate"
                        )
                    ),

                "training_window_id":
                    completed.get(
                        "training_window_id"
                    ),

                "training_window":
                    deepcopy(
                        completed.get(
                            "training_window"
                        )
                    ),

                "learning_contribution_id":
                    contribution_id,

                "ledger_persisted":
                    isinstance(
                        persisted_contribution,
                        dict,
                    ),

                "confidence_pipeline_status":
                    completed.get(
                        "confidence_pipeline_status"
                    ),

                "learning_ledger_status":
                    completed.get(
                        "learning_ledger_status"
                    ),

                **metrics,

                "execution_counters": {
                    key:
                        int(
                            completed.get(key)
                            or 0
                        )
                    for key in (
                        "paper_orders_created",
                        "portfolio_mutations",
                        "database_rows_written",
                        "strategy_promotions",
                        "broker_requests",
                        "live_orders",
                        "model_updates",
                    )
                },
            }

            with _LOCK:
                controller = (
                    _CONTROLLERS[
                        controller_id
                    ]
                )

                controller[
                    "rounds"
                ].append(
                    round_record
                )

                controller[
                    "rounds_completed"
                ] = round_number

            average_confidence = (
                _finite_float(
                    metrics[
                        "average_confidence"
                    ]
                )
            )

            if average_confidence > best_confidence:
                best_confidence = (
                    average_confidence
                )

                best_round_number = (
                    round_number
                )

                best_candidate_id = (
                    completed.get(
                        "candidate_id"
                    )
                )

                best_window_id = (
                    completed.get(
                        "training_window_id"
                    )
                )

            _update_controller(
                controller_id,
                best_round_number=(
                    best_round_number
                ),
                best_average_confidence=(
                    best_confidence
                ),
                best_candidate_id=(
                    best_candidate_id
                ),
                best_training_window_id=(
                    best_window_id
                ),
            )

            if run_status != "completed":
                return _update_controller(
                    controller_id,
                    status="failed",
                    completed_at=_utc_now(),
                    stop_reason=(
                        "training_round_failed"
                    ),
                )

            if not isinstance(
                persisted_contribution,
                dict,
            ):
                return _update_controller(
                    controller_id,
                    status="failed",
                    completed_at=_utc_now(),
                    stop_reason=(
                        "learning_contribution_"
                        "not_persisted"
                    ),
                )

            if average_confidence >= threshold:
                return _update_controller(
                    controller_id,
                    status="completed",
                    completed_at=_utc_now(),
                    stop_reason=(
                        "confidence_threshold_met"
                    ),
                )

            if (
                round_number
                >= resolved_maximum_rounds
            ):
                return _update_controller(
                    controller_id,
                    status="completed",
                    completed_at=_utc_now(),
                    stop_reason=(
                        "maximum_rounds_reached"
                    ),
                )

            candidate = _next_candidate(
                current_candidate=candidate,
                metrics=metrics,
                next_round_number=(
                    round_number + 1
                ),
            )

            current_window = (
                completed.get(
                    "training_window"
                )
            )

            if not isinstance(
                current_window,
                dict,
            ):
                return _update_controller(
                    controller_id,
                    status="failed",
                    completed_at=_utc_now(),
                    stop_reason=(
                        "training_window_missing"
                    ),
                )

            current_window_values = (
                _next_window_values(
                    current_window=(
                        current_window
                    ),
                    next_round_number=(
                        round_number + 1
                    ),
                )
            )

    except Exception as error:
        return _update_controller(
            controller_id,
            status="failed",
            completed_at=_utc_now(),
            stop_reason=(
                type(error).__name__
            ),
            error=str(error),
        )

    return _update_controller(
        controller_id,
        status="failed",
        completed_at=_utc_now(),
        stop_reason=(
            "controller_exited_without_"
            "terminal_classification"
        ),
    )


__all__ = [
    "adaptive_controller_status",
    "get_adaptive_controller",
    "run_adaptive_training_controller",
]

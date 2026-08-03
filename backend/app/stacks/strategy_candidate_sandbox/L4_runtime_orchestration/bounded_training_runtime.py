"""
Bounded read-only historical training runtime.

This runtime evaluates repository-owned historical CSV rows only.

It does not:

- place paper or live orders
- mutate portfolios
- call brokers
- promote strategies
- mutate strategy definitions
- write identity, portfolio, order, or ledger database rows
- enable live execution
- enable broker execution

The only writes are bounded runtime evidence files under
runtime/training_sessions.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock, Thread
from time import monotonic, sleep
from typing import Any
from uuid import uuid4
import csv
import json
import math

from backend.app.stacks.strategy_candidate_sandbox.persistent_learning_ledger import (
    persist_sanitized_learning_contribution,
)

from backend.app.stacks.strategy_candidate_sandbox.bounded_training_confidence_pipeline import (
    build_bounded_training_confidence_summary,
)

from backend.app.stacks.strategy_candidate_sandbox.training_confidence_baseline import (
    build_confidence_baseline_comparison,
)





_REPO_ROOT = Path(__file__).resolve().parents[5]

_DATA_ROOT = (
    _REPO_ROOT
    / "backend"
    / "app"
    / "stacks"
    / "learning_research"
    / "research_data"
)

_RUNTIME_ROOT = (
    _REPO_ROOT
    / "runtime"
    / "training_sessions"
)

_CANADIAN_GROUPS = (
    "equities_canada",
    "canadian_etfs",
)

_MINIMUM_DURATION_SECONDS = 1
_MAXIMUM_DURATION_SECONDS = 600
_DEFAULT_DURATION_SECONDS = 120

_LOCK = Lock()
_RUNS: dict[str, dict[str, Any]] = {}


def _utc_now() -> str:
    return datetime.now(
        UTC
    ).isoformat()


def _safe_float(
    value: Any,
) -> float | None:
    try:
        number = float(value)
    except (
        TypeError,
        ValueError,
    ):
        return None

    if not math.isfinite(number):
        return None

    return number


def _resolve_duration(
    duration_seconds: Any,
) -> int:
    try:
        duration = int(
            duration_seconds
        )
    except (
        TypeError,
        ValueError,
    ):
        duration = (
            _DEFAULT_DURATION_SECONDS
        )

    return max(
        _MINIMUM_DURATION_SECONDS,
        min(
            duration,
            _MAXIMUM_DURATION_SECONDS,
        ),
    )


def _symbol_from_csv(
    path: Path,
) -> str:
    relative = path.relative_to(
        _DATA_ROOT
    )

    group = relative.parts[0]

    metadata_dir = (
        _DATA_ROOT
        / group
        / "metadata"
    )

    manifest = (
        metadata_dir
        / (
            path.stem
            + "_manifest.json"
        )
    )

    if manifest.is_file():
        try:
            payload = json.loads(
                manifest.read_text(
                    encoding="utf-8",
                )
            )

            symbol = str(
                payload.get(
                    "symbol",
                    "",
                )
            ).strip().upper()

            if symbol:
                return symbol

        except Exception:
            pass

    name = path.stem

    if name.endswith("_TO"):
        return (
            name[:-3]
            .replace("_", "-")
            + ".TO"
        )

    return name.replace(
        "_",
        "-",
    ).upper()


def discover_canadian_datasets() -> list[
    dict[str, str]
]:
    datasets: list[
        dict[str, str]
    ] = []

    for group in _CANADIAN_GROUPS:
        raw_dir = (
            _DATA_ROOT
            / group
            / "raw"
        )

        if not raw_dir.is_dir():
            continue

        for path in sorted(
            raw_dir.glob("*.csv")
        ):
            datasets.append(
                {
                    "symbol":
                        _symbol_from_csv(
                            path
                        ),
                    "asset_group":
                        group,
                    "path":
                        str(path),
                }
            )

    return datasets


def _read_close_rows(
    path: Path,
) -> list[
    tuple[str | None, float]
]:
    rows: list[
        tuple[str | None, float]
    ] = []

    with path.open(
        "r",
        encoding="utf-8-sig",
        errors="replace",
        newline="",
    ) as handle:
        reader = csv.DictReader(
            handle
        )

        if not reader.fieldnames:
            return rows

        normalized = {
            str(name).strip().lower():
                name
            for name in reader.fieldnames
            if name is not None
        }

        close_key = (
            normalized.get("close")
            or normalized.get(
                "adj close"
            )
            or normalized.get(
                "adj_close"
            )
        )

        date_key = (
            normalized.get("date")
            or normalized.get(
                "datetime"
            )
            or normalized.get(
                "timestamp"
            )
        )

        if close_key is None:
            return rows

        for row in reader:
            close = _safe_float(
                row.get(close_key)
            )

            if close is None:
                continue

            timestamp = (
                str(
                    row.get(
                        date_key,
                        "",
                    )
                ).strip()
                if date_key
                else None
            )

            rows.append(
                (
                    timestamp or None,
                    close,
                )
            )

    return rows


def _decision(
    *,
    previous_close: float,
    current_close: float,
) -> str:
    if previous_close == 0:
        return "HOLD"

    change = (
        current_close
        - previous_close
    ) / abs(previous_close)

    if change >= 0.0025:
        return "BUY_SIGNAL"

    if change <= -0.0025:
        return "SELL_SIGNAL"

    return "HOLD"


def _write_evidence(
    snapshot: dict[str, Any],
) -> None:
    _RUNTIME_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    run_id = str(
        snapshot["run_id"]
    )

    run_dir = (
        _RUNTIME_ROOT
        / run_id
    )

    run_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = (
        run_dir
        / "summary.json.tmp"
    )

    destination = (
        run_dir
        / "summary.json"
    )

    temporary.write_text(
        json.dumps(
            snapshot,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )

    temporary.replace(
        destination
    )


def _update_run(
    run_id: str,
    **values: Any,
) -> dict[str, Any]:
    with _LOCK:
        record = _RUNS[
            run_id
        ]

        record.update(
            values
        )

        snapshot = deepcopy(
            record
        )

    _write_evidence(
        snapshot
    )

    return snapshot


def _run_training(
    run_id: str,
) -> None:
    with _LOCK:
        record = deepcopy(
            _RUNS[run_id]
        )

    duration_seconds = int(
        record[
            "duration_seconds"
        ]
    )

    datasets = (
        discover_canadian_datasets()
    )

    if not datasets:
        _update_run(
            run_id,
            status="failed",
            completed_at=_utc_now(),
            error=(
                "No Canadian historical CSV "
                "datasets were found."
            ),
        )

        return

    prepared: list[
        dict[str, Any]
    ] = []

    invalid_datasets: list[str] = []

    for dataset in datasets:
        path = Path(
            dataset["path"]
        )

        try:
            rows = _read_close_rows(
                path
            )
        except Exception:
            rows = []

        if len(rows) < 2:
            invalid_datasets.append(
                dataset["symbol"]
            )
            continue

        prepared.append(
            {
                **dataset,
                "rows": rows,
                "cursor": 1,
            }
        )

    if not prepared:
        _update_run(
            run_id,
            status="failed",
            completed_at=_utc_now(),
            error=(
                "Canadian datasets were found, "
                "but none contained at least "
                "two valid close values."
            ),
            invalid_symbols=(
                invalid_datasets
            ),
        )

        return

    started_monotonic = (
        monotonic()
    )

    deadline = (
        started_monotonic
        + duration_seconds
    )

    decision_counts = {
        "BUY_SIGNAL": 0,
        "SELL_SIGNAL": 0,
        "HOLD": 0,
    }

    per_symbol = {
        item["symbol"]: {
            "cycles": 0,
            "BUY_SIGNAL": 0,
            "SELL_SIGNAL": 0,
            "HOLD": 0,
            "last_timestamp": None,
            "last_close": None,
        }
        for item in prepared
    }

    cycles = 0
    rows_evaluated = 0
    heartbeat_at = (
        started_monotonic
    )

    _update_run(
        run_id,
        status="running",
        started_at=_utc_now(),
        discovered_symbol_count=(
            len(datasets)
        ),
        eligible_symbol_count=(
            len(prepared)
        ),
        invalid_symbols=(
            invalid_datasets
        ),
        symbols=[
            item["symbol"]
            for item in prepared
        ],
    )

    while monotonic() < deadline:
        for item in prepared:
            if monotonic() >= deadline:
                break

            rows = item["rows"]
            cursor = int(
                item["cursor"]
            )

            if cursor >= len(rows):
                cursor = 1

            previous_timestamp, previous = (
                rows[cursor - 1]
            )

            current_timestamp, current = (
                rows[cursor]
            )

            signal = _decision(
                previous_close=previous,
                current_close=current,
            )

            decision_counts[
                signal
            ] += 1

            symbol_result = (
                per_symbol[
                    item["symbol"]
                ]
            )

            symbol_result[
                "cycles"
            ] += 1

            symbol_result[
                signal
            ] += 1

            symbol_result[
                "last_timestamp"
            ] = current_timestamp

            symbol_result[
                "last_close"
            ] = current

            item["cursor"] = (
                cursor + 1
            )

            rows_evaluated += 1

        cycles += 1

        now = monotonic()

        if (
            now - heartbeat_at
            >= 1.0
        ):
            elapsed = max(
                0.0,
                now
                - started_monotonic,
            )

            _update_run(
                run_id,
                elapsed_seconds=round(
                    elapsed,
                    3,
                ),
                progress_percent=round(
                    min(
                        100.0,
                        (
                            elapsed
                            / duration_seconds
                        )
                        * 100.0,
                    ),
                    2,
                ),
                cycles=cycles,
                rows_evaluated=(
                    rows_evaluated
                ),
                decision_counts=(
                    deepcopy(
                        decision_counts
                    )
                ),
            )

            heartbeat_at = now

        sleep(0.01)

    completed_monotonic = (
        monotonic()
    )

    actual_duration = max(
        0.0,
        completed_monotonic
        - started_monotonic,
    )

    _update_run(
        run_id,
        status="finalizing",
        completed_at=_utc_now(),
        elapsed_seconds=round(
            actual_duration,
            3,
        ),
        progress_percent=100.0,
        cycles=cycles,
        rows_evaluated=(
            rows_evaluated
        ),
        decision_counts=(
            decision_counts
        ),
        per_symbol=(
            per_symbol
        ),
        executed_trades=0,
        paper_orders_created=0,
        portfolio_mutations=0,
        database_rows_written=0,
        strategy_promotions=0,
        learning_artifacts_written=0,
        learning_updates=0,
        model_updates=0,
        broker_requests=0,
        live_orders=0,
    )

    completed_record = get_training_session(
        run_id
    )

    if completed_record is not None:
        contribution_record = dict(
            completed_record
        )

        contribution_record[
            "status"
        ] = "completed"

        contribution = (
            _sanitized_learning_contribution(
                contribution_record
            )
        )

        confidence_summary = {}
        confidence_pipeline_status = "pending"
        confidence_pipeline_error = None

        try:
            confidence_summary = (
                build_bounded_training_confidence_summary(
                    run_id=run_id,
                    datasets=prepared,
                )
            )

            contribution.update(
                confidence_summary
            )

            confidence_baseline = (
                build_confidence_baseline_comparison(
                    current_contribution=(
                        contribution
                    ),
                )
            )

            contribution.update(
                confidence_baseline
            )

            confidence_pipeline_status = (
                "completed"
            )

        except Exception as error:
            confidence_pipeline_status = (
                "failed"
            )

            confidence_pipeline_error = (
                type(error).__name__
            )

        try:
            persistence = (
                persist_sanitized_learning_contribution(
                    contribution
                )
            )

            _update_run(
                run_id,
                    status="completed",
                sanitized_learning_contribution=(
                    contribution
                ),
                learning_ledger_status=(
                    persistence.get(
                        "status"
                    )
                ),
                learning_contribution_id=(
                    persistence.get(
                        "contribution_id"
                    )
                ),
                learning_ledger_entry_id=(
                    persistence.get(
                        "ledger_entry_id"
                    )
                ),
                learning_artifacts_written=int(
                    persistence.get(
                        "artifacts_written",
                        0,
                    )
                ),
                learning_updates=int(
                    persistence.get(
                        "learning_updates",
                        0,
                    )
                ),
                model_updates=0,
                confidence_pipeline_status=(
                    confidence_pipeline_status
                ),
                confidence_pipeline_error=(
                    confidence_pipeline_error
                ),
                valid_learning_artifacts=int(
                    confidence_summary.get(
                        "valid_learning_artifacts",
                        0,
                    )
                ),
                learning_observations=int(
                    confidence_summary.get(
                        "learning_observations",
                        0,
                    )
                ),
                average_reward=float(
                    confidence_summary.get(
                        "average_reward",
                        0.0,
                    )
                ),
                average_confidence=float(
                    confidence_summary.get(
                        "average_confidence",
                        0.0,
                    )
                ),
                minimum_symbol_confidence=float(
                    confidence_summary.get(
                        "minimum_symbol_confidence",
                        0.0,
                    )
                ),
                maximum_symbol_confidence=float(
                    confidence_summary.get(
                        "maximum_symbol_confidence",
                        0.0,
                    )
                ),
                symbols_with_valid_confidence=int(
                    confidence_summary.get(
                        "symbols_with_valid_confidence",
                        0,
                    )
                ),
                confidence_baseline_available=(
                    confidence_baseline.get(
                        "confidence_baseline_available"
                    )
                ),
                baseline_contribution_id=(
                    confidence_baseline.get(
                        "baseline_contribution_id"
                    )
                ),
                baseline_average_confidence=(
                    confidence_baseline.get(
                        "baseline_average_confidence"
                    )
                ),
                current_average_confidence=(
                    confidence_baseline.get(
                        "current_average_confidence"
                    )
                ),
                average_confidence_delta=(
                    confidence_baseline.get(
                        "average_confidence_delta"
                    )
                ),
                symbols_compared=int(
                    confidence_baseline.get(
                        "symbols_compared",
                        0,
                    )
                ),
                symbols_improved=int(
                    confidence_baseline.get(
                        "symbols_improved",
                        0,
                    )
                ),
                symbols_unchanged=int(
                    confidence_baseline.get(
                        "symbols_unchanged",
                        0,
                    )
                ),
                symbols_declined=int(
                    confidence_baseline.get(
                        "symbols_declined",
                        0,
                    )
                ),
                all_compared_symbols_improved=(
                    confidence_baseline.get(
                        "all_compared_symbols_improved",
                        False,
                    )
                ),
                confidence_improved=(
                    confidence_baseline.get(
                        "confidence_improved",
                        False,
                    )
                ),
            )

        except Exception as error:
            _update_run(
                run_id,
                sanitized_learning_contribution=(
                    contribution
                ),
                learning_ledger_status=(
                    "failed"
                ),
                learning_ledger_error=(
                    type(error).__name__
                ),
                learning_artifacts_written=0,
                learning_updates=0,
                model_updates=0,
            )



def _normalize_training_scope(
    value: Any,
) -> str:
    scope = str(
        value or ""
    ).strip().lower()

    if scope not in {
        "user",
        "system",
    }:
        raise ValueError(
            "Training scope must be USER or SYSTEM."
        )

    return scope


def _normalized_owner_value(
    value: Any,
) -> str | None:
    normalized = str(
        value or ""
    ).strip()

    return normalized or None


def _public_health_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    """
    Return operational health without exposing customer identity.
    """

    return {
        "run_id":
            record.get("run_id"),

        "scope":
            record.get("scope"),

        "status":
            record.get("status"),

        "created_at":
            record.get("created_at"),

        "started_at":
            record.get("started_at"),

        "completed_at":
            record.get("completed_at"),

        "duration_seconds":
            record.get(
                "duration_seconds"
            ),

        "elapsed_seconds":
            record.get(
                "elapsed_seconds"
            ),

        "progress_percent":
            record.get(
                "progress_percent"
            ),

        "eligible_symbol_count":
            record.get(
                "eligible_symbol_count"
            ),

        "rows_evaluated":
            record.get(
                "rows_evaluated"
            ),

        "cycles":
            record.get("cycles"),

        "error":
            record.get("error"),

        "safety":
            deepcopy(
                record.get(
                    "safety",
                    {},
                )
            ),
    }


def _sanitized_learning_contribution(
    record: dict[str, Any],
) -> dict[str, Any]:
    """
    Produce transferable aggregate learning output.

    This intentionally excludes:
    - user and session identifiers
    - email and display name
    - chat content
    - portfolio, position, order, and account data
    - authentication information
    """

    decision_counts = record.get(
        "decision_counts",
        {},
    )

    if not isinstance(
        decision_counts,
        dict,
    ):
        decision_counts = {}

    return {
        "contribution_id":
            "contribution_"
            + uuid4().hex,

        "source_scope":
            record.get("scope"),

        "universe":
            record.get("universe"),

        "completed":
            record.get("status")
            == "completed",

        "duration_seconds":
            record.get(
                "duration_seconds"
            ),

        "elapsed_seconds":
            record.get(
                "elapsed_seconds"
            ),

        "symbols_evaluated":
            record.get(
                "eligible_symbol_count"
            ),

        "rows_evaluated":
            record.get(
                "rows_evaluated"
            ),

        "cycles":
            record.get("cycles"),

        "signal_totals": {
            "BUY_SIGNAL":
                int(
                    decision_counts.get(
                        "BUY_SIGNAL",
                        0,
                    )
                ),

            "SELL_SIGNAL":
                int(
                    decision_counts.get(
                        "SELL_SIGNAL",
                        0,
                    )
                ),

            "HOLD":
                int(
                    decision_counts.get(
                        "HOLD",
                        0,
                    )
                ),
        },

        "safety": {
            "customer_identity_included":
                False,

            "session_identity_included":
                False,

            "portfolio_data_included":
                False,

            "order_data_included":
                False,

            "chat_content_included":
                False,

            "authentication_data_included":
                False,

            "broker_execution":
                False,

            "live_execution":
                False,
        },
    }


def get_training_session_for_owner(
    *,
    run_id: str,
    owner_user_id: str,
    owner_session_id: str,
) -> dict[str, Any] | None:
    record = get_training_session(
        run_id
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


def list_training_sessions_for_owner(
    *,
    owner_user_id: str,
    owner_session_id: str,
    limit: int = 20,
) -> list[dict[str, Any]]:
    return [
        record
        for record
        in list_training_sessions(
            limit=100,
        )
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
    ][:max(1, min(int(limit), 100))]


def list_training_health(
    *,
    limit: int = 100,
) -> list[dict[str, Any]]:
    return [
        _public_health_record(
            record
        )
        for record
        in list_training_sessions(
            limit=limit,
        )
    ]


def list_training_failures(
    *,
    limit: int = 100,
) -> list[dict[str, Any]]:
    return [
        _public_health_record(
            record
        )
        for record
        in list_training_sessions(
            limit=limit,
        )
        if record.get("status")
        == "failed"
    ]

def start_bounded_training_session(
    *,
    duration_seconds: int = (
        _DEFAULT_DURATION_SECONDS
    ),
    universe: str = "canada",
    requested_by: str | None = None,
    source: str = "api",
    scope: str = "system",
    owner_user_id: str | None = None,
    owner_session_id: str | None = None,
    requested_by_role: str | None = None,
) -> dict[str, Any]:
    normalized_universe = str(
        universe
    ).strip().lower()

    if normalized_universe not in {
        "canada",
        "canadian",
        "all_canadian",
    }:
        raise ValueError(
            "Only the bounded Canadian "
            "historical universe is supported."
        )

    duration = _resolve_duration(
        duration_seconds
    )

    resolved_scope = (
        _normalize_training_scope(
            scope
        )
    )

    resolved_owner_user_id = (
        _normalized_owner_value(
            owner_user_id
        )
    )

    resolved_owner_session_id = (
        _normalized_owner_value(
            owner_session_id
        )
    )

    resolved_role = str(
        requested_by_role or ""
    ).strip().lower() or None

    if resolved_scope == "user":
        if not resolved_owner_user_id:
            raise ValueError(
                "USER training requires an owner user ID."
            )

        if not resolved_owner_session_id:
            raise ValueError(
                "USER training requires an owner session ID."
            )

    if resolved_scope == "system":
        if resolved_owner_user_id is not None:
            raise ValueError(
                "SYSTEM training cannot have a customer owner."
            )

        if resolved_owner_session_id is not None:
            raise ValueError(
                "SYSTEM training cannot have a customer session."
            )

    run_id = (
        "training_"
        + datetime.now(
            UTC
        ).strftime(
            "%Y%m%d_%H%M%S"
        )
        + "_"
        + uuid4().hex[:10]
    )

    record = {
        "run_id": run_id,
        "status": "queued",
        "created_at": _utc_now(),
        "started_at": None,
        "completed_at": None,
        "duration_seconds": duration,
        "elapsed_seconds": 0.0,
        "progress_percent": 0.0,
        "universe": "canada",

        "scope":
            resolved_scope,

        "owner_user_id":
            resolved_owner_user_id,

        "owner_session_id":
            resolved_owner_session_id,

        "requested_by":
            requested_by,

        "requested_by_role":
            resolved_role,

        "source": source,
        "discovered_symbol_count": 0,
        "eligible_symbol_count": 0,
        "symbols": [],
        "invalid_symbols": [],
        "cycles": 0,
        "rows_evaluated": 0,
        "decision_counts": {
            "BUY_SIGNAL": 0,
            "SELL_SIGNAL": 0,
            "HOLD": 0,
        },
        "per_symbol": {},
        "error": None,
        "safety": {
            "historical_csv_read_only":
                True,
            "sandbox_only":
                True,
            "executed_trades":
                False,
            "paper_order_creation":
                False,
            "portfolio_mutation":
                False,
            "database_writes":
                False,
            "strategy_mutation":
                False,
            "strategy_promotion":
                False,
            "broker_execution":
                False,
            "live_execution":
                False,
        },
    }

    with _LOCK:
        _RUNS[
            run_id
        ] = record

    _write_evidence(
        deepcopy(
            record
        )
    )

    thread = Thread(
        target=_run_training,
        args=(run_id,),
        name=run_id,
        daemon=True,
    )

    thread.start()

    return deepcopy(
        record
    )


def get_training_session(
    run_id: str,
) -> dict[str, Any] | None:
    with _LOCK:
        record = _RUNS.get(
            str(run_id)
        )

        if record is not None:
            return deepcopy(
                record
            )

    path = (
        _RUNTIME_ROOT
        / str(run_id)
        / "summary.json"
    )

    if not path.is_file():
        return None

    try:
        payload = json.loads(
            path.read_text(
                encoding="utf-8",
            )
        )
    except Exception:
        return None

    return (
        payload
        if isinstance(
            payload,
            dict,
        )
        else None
    )


def list_training_sessions(
    *,
    limit: int = 20,
) -> list[dict[str, Any]]:
    resolved_limit = max(
        1,
        min(
            int(limit),
            100,
        ),
    )

    records: dict[
        str,
        dict[str, Any],
    ] = {}

    if _RUNTIME_ROOT.is_dir():
        paths = sorted(
            _RUNTIME_ROOT.glob(
                "training_*/summary.json"
            ),
            key=lambda path:
                path.stat().st_mtime,
            reverse=True,
        )

        for path in paths[
            :resolved_limit
        ]:
            try:
                payload = json.loads(
                    path.read_text(
                        encoding="utf-8",
                    )
                )
            except Exception:
                continue

            if not isinstance(
                payload,
                dict,
            ):
                continue

            run_id = str(
                payload.get(
                    "run_id",
                    "",
                )
            )

            if run_id:
                records[
                    run_id
                ] = payload

    with _LOCK:
        memory_records = [
            deepcopy(record)
            for record in _RUNS.values()
        ]

    for record in memory_records:
        run_id = str(
            record.get(
                "run_id",
                "",
            )
        )

        if run_id:
            records[
                run_id
            ] = record

    return sorted(
        records.values(),
        key=lambda item:
            str(
                item.get(
                    "created_at",
                    "",
                )
            ),
        reverse=True,
    )[:resolved_limit]


def training_runtime_status() -> dict[str, Any]:
    datasets = (
        discover_canadian_datasets()
    )

    with _LOCK:
        active = sum(
            1
            for record
            in _RUNS.values()
            if record.get(
                "status"
            )
            in {
                "queued",
                "running",
            }
        )

    return {
        "runtime_enabled": True,
        "mode": (
            "BOUNDED_READ_ONLY_"
            "HISTORICAL_REPLAY"
        ),
        "default_duration_seconds":
            _DEFAULT_DURATION_SECONDS,
        "minimum_duration_seconds":
            _MINIMUM_DURATION_SECONDS,
        "maximum_duration_seconds":
            _MAXIMUM_DURATION_SECONDS,
        "canadian_dataset_count":
            len(datasets),
        "active_run_count":
            active,
        "runtime_evidence_root":
            str(_RUNTIME_ROOT),
        "safety": {
            "historical_csv_read_only":
                True,
            "sandbox_only":
                True,
            "paper_orders_enabled":
                False,
            "portfolio_mutation_enabled":
                False,
            "database_writes_enabled":
                False,
            "strategy_mutation_enabled":
                False,
            "promotion_enabled":
                False,
            "broker_execution_enabled":
                False,
            "live_execution_enabled":
                False,
        },
    }


__all__ = [
    "discover_canadian_datasets",
    "get_training_session",
    "get_training_session_for_owner",
    "list_training_failures",
    "list_training_health",
    "list_training_sessions",
    "list_training_sessions_for_owner",
    "start_bounded_training_session",
    "training_runtime_status",
]

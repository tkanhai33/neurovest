"""
Append-only sanitized learning ledger.

This module persists aggregate bounded-training contributions without
customer, session, portfolio, order, authentication, or broker data.

It does not promote strategies, mutate production models, write to the
application database, or enable any trading path.
"""

from __future__ import annotations

from backend.app.stacks.strategy_candidate_sandbox.training_candidate_contract import (
    validate_training_candidate_contract,
)
from backend.app.stacks.strategy_candidate_sandbox.training_window_contract import (
    validate_training_window_contract,
)

from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Any
from uuid import uuid4
import json


_REPO_ROOT = Path(__file__).resolve().parents[4]

_LEDGER_ROOT = (
    _REPO_ROOT
    / "runtime"
    / "strategy_candidate_sandbox"
    / "learning_ledger"
)

_LEDGER_INDEX = (
    _LEDGER_ROOT
    / "contributions.jsonl"
)

_LOCK = Lock()

_LEDGER_VERSION = 1

_ALLOWED_TOP_LEVEL_KEYS = {
    "all_compared_symbols_improved",
    "average_confidence",
    "average_confidence_delta",
    "average_reward",
    "baseline_average_confidence",
    "baseline_contribution_id",
    "candidate_id",
    "completed",
    "confidence_baseline_available",
    "confidence_baseline_version",
    "confidence_improved",
    "confidence_safety",
    "contribution_id",
    "current_average_confidence",
    "cycles",
    "duration_seconds",
    "elapsed_seconds",
    "invalid_confidence_datasets",
    "learning_observations",
    "learning_pipeline",
    "learning_pipeline_version",
    "lookback_rows",
    "maximum_rounds",
    "maximum_symbol_confidence",
    "maximum_symbol_confidence_delta",
    "minimum_symbol_confidence",
    "minimum_symbol_confidence_delta",
    "round_number",
    "row_offset",
    "rows_evaluated",
    "safety",
    "signal_totals",
    "source_scope",
    "symbol_confidence",
    "symbol_confidence_delta",
    "symbols_compared",
    "symbols_declined",
    "symbols_evaluated",
    "symbols_improved",
    "symbols_unchanged",
    "symbols_with_valid_confidence",
    "training_candidate",
    "training_window",
    "training_window_id",
    "universe",
    "valid_learning_artifacts",
    "window_end",
    "window_start",
}

_REQUIRED_TOP_LEVEL_KEYS = {
    "contribution_id",
    "source_scope",
    "universe",
    "completed",
    "symbols_evaluated",
    "rows_evaluated",
    "cycles",
    "signal_totals",
    "safety",
}

_FORBIDDEN_KEYS = {
    "owner_user_id",
    "owner_session_id",
    "user_id",
    "session_id",
    "email",
    "display_name",
    "name",
    "password",
    "prompt",
    "raw_prompt",
    "chat",
    "chat_content",
    "message",
    "portfolio",
    "positions",
    "holdings",
    "orders",
    "account",
    "account_id",
    "authentication",
    "access_token",
    "refresh_token",
    "credential",
    "credentials",
    "broker",
    "broker_token",
    "requested_by",
    "requested_by_role",
}

_SIGNAL_KEYS = {
    "BUY_SIGNAL",
    "SELL_SIGNAL",
    "HOLD",
}

_REQUIRED_SAFETY_VALUES = {
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
}


def _utc_now() -> str:
    return datetime.now(
        UTC
    ).isoformat()


def _contains_forbidden_key(
    value: Any,
) -> str | None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(
                key
            ).strip().lower()

            if normalized in _FORBIDDEN_KEYS:
                return normalized

            nested = _contains_forbidden_key(
                child
            )

            if nested:
                return nested

    elif isinstance(value, list):
        for child in value:
            nested = _contains_forbidden_key(
                child
            )

            if nested:
                return nested

    return None


def validate_sanitized_contribution(
    contribution: dict[str, Any],
) -> bool:
    if not isinstance(
        contribution,
        dict,
    ):
        return False

    keys = set(
        contribution
    )

    if not _REQUIRED_TOP_LEVEL_KEYS.issubset(
        keys
    ):
        return False

    if not keys.issubset(
        _ALLOWED_TOP_LEVEL_KEYS
    ):
        return False

    if _contains_forbidden_key(
        contribution
    ):
        return False

    if contribution.get(
        "completed"
    ) is not True:
        return False

    scope = str(
        contribution.get(
            "source_scope"
        )
        or ""
    ).strip().lower()

    if scope not in {
        "user",
        "system",
    }:
        return False

    universe = str(
        contribution.get(
            "universe"
        )
        or ""
    ).strip().lower()

    if universe != "canada":
        return False

    for key in (
        "symbols_evaluated",
        "rows_evaluated",
        "cycles",
    ):
        value = contribution.get(
            key
        )

        if not isinstance(
            value,
            int,
        ):
            return False

        if value < 0:
            return False

    totals = contribution.get(
        "signal_totals"
    )

    if not isinstance(
        totals,
        dict,
    ):
        return False

    if set(totals) != _SIGNAL_KEYS:
        return False

    for value in totals.values():
        if not isinstance(
            value,
            int,
        ):
            return False

        if value < 0:
            return False

    symbol_confidence = contribution.get(
        "symbol_confidence"
    )

    if symbol_confidence is not None:
        if not isinstance(
            symbol_confidence,
            list,
        ):
            return False

        observed_symbols: set[str] = set()

        for item in symbol_confidence:
            if not isinstance(
                item,
                dict,
            ):
                return False

            if set(item) != {
                "symbol",
                "observations",
                "average_reward",
                "average_confidence",
            }:
                return False

            symbol = str(
                item.get(
                    "symbol"
                )
                or ""
            ).strip().upper()

            if not symbol:
                return False

            if symbol in observed_symbols:
                return False

            observed_symbols.add(
                symbol
            )

            observations = item.get(
                "observations"
            )

            if not isinstance(
                observations,
                int,
            ):
                return False

            if observations < 0:
                return False

            reward = item.get(
                "average_reward"
            )

            confidence = item.get(
                "average_confidence"
            )

            if not isinstance(
                reward,
                (
                    int,
                    float,
                ),
            ):
                return False

            if not isinstance(
                confidence,
                (
                    int,
                    float,
                ),
            ):
                return False

            if not (
                0.0
                <= float(confidence)
                <= 1.0
            ):
                return False

    for key in (
        "average_confidence",
        "minimum_symbol_confidence",
        "maximum_symbol_confidence",
    ):
        value = contribution.get(
            key
        )

        if value is None:
            continue

        if not isinstance(
            value,
            (
                int,
                float,
            ),
        ):
            return False

        if not (
            0.0
            <= float(value)
            <= 1.0
        ):
            return False

    for key in (
        "valid_learning_artifacts",
        "learning_observations",
        "symbols_with_valid_confidence",
        "invalid_confidence_datasets",
    ):
        value = contribution.get(
            key
        )

        if value is None:
            continue

        if not isinstance(
            value,
            int,
        ):
            return False

        if value < 0:
            return False

    baseline_available = contribution.get(
        "confidence_baseline_available"
    )

    if baseline_available is not None:
        if not isinstance(
            baseline_available,
            bool,
        ):
            return False

    for key in (
        "symbols_compared",
        "symbols_improved",
        "symbols_unchanged",
        "symbols_declined",
    ):
        value = contribution.get(
            key
        )

        if value is None:
            continue

        if not isinstance(
            value,
            int,
        ):
            return False

        if value < 0:
            return False

    for key in (
        "baseline_average_confidence",
        "current_average_confidence",
    ):
        value = contribution.get(
            key
        )

        if value is None:
            continue

        if not isinstance(
            value,
            (
                int,
                float,
            ),
        ):
            return False

        if not (
            0.0
            <= float(value)
            <= 1.0
        ):
            return False

    for key in (
        "average_confidence_delta",
        "minimum_symbol_confidence_delta",
        "maximum_symbol_confidence_delta",
    ):
        value = contribution.get(
            key
        )

        if value is None:
            continue

        if not isinstance(
            value,
            (
                int,
                float,
            ),
        ):
            return False

        if not (
            -1.0
            <= float(value)
            <= 1.0
        ):
            return False

    symbol_delta = contribution.get(
        "symbol_confidence_delta"
    )

    if symbol_delta is not None:
        if not isinstance(
            symbol_delta,
            list,
        ):
            return False

        observed_symbols: set[str] = set()

        for item in symbol_delta:
            if not isinstance(
                item,
                dict,
            ):
                return False

            if set(item) != {
                "symbol",
                "baseline_confidence",
                "current_confidence",
                "confidence_delta",
                "state",
            }:
                return False

            symbol = str(
                item.get(
                    "symbol"
                )
                or ""
            ).strip().upper()

            if (
                not symbol
                or symbol in observed_symbols
            ):
                return False

            observed_symbols.add(
                symbol
            )

            before = item.get(
                "baseline_confidence"
            )

            after = item.get(
                "current_confidence"
            )

            delta = item.get(
                "confidence_delta"
            )

            if not all(
                isinstance(
                    value,
                    (
                        int,
                        float,
                    ),
                )
                for value in (
                    before,
                    after,
                    delta,
                )
            ):
                return False

            if not (
                0.0
                <= float(before)
                <= 1.0
            ):
                return False

            if not (
                0.0
                <= float(after)
                <= 1.0
            ):
                return False

            if not (
                -1.0
                <= float(delta)
                <= 1.0
            ):
                return False

            if item.get(
                "state"
            ) not in {
                "improved",
                "unchanged",
                "declined",
            }:
                return False

    provenance_keys = {
        "candidate_id",
        "training_candidate",
        "training_window_id",
        "training_window",
        "window_start",
        "window_end",
        "lookback_rows",
        "row_offset",
        "round_number",
        "maximum_rounds",
    }

    present_provenance_keys = (
        set(contribution)
        & provenance_keys
    )

    if present_provenance_keys:
        if (
            present_provenance_keys
            != provenance_keys
        ):
            return False

        training_candidate = (
            contribution.get(
                "training_candidate"
            )
        )

        training_window = (
            contribution.get(
                "training_window"
            )
        )

        if not validate_training_candidate_contract(
            training_candidate
        ):
            return False

        if not validate_training_window_contract(
            training_window
        ):
            return False

        if contribution.get(
            "candidate_id"
        ) != training_candidate.get(
            "candidate_id"
        ):
            return False

        if contribution.get(
            "training_window_id"
        ) != training_window.get(
            "training_window_id"
        ):
            return False

        for key in (
            "window_start",
            "window_end",
            "lookback_rows",
            "row_offset",
            "round_number",
            "maximum_rounds",
        ):
            if contribution.get(
                key
            ) != training_window.get(
                key
            ):
                return False

    safety = contribution.get(
        "safety"
    )

    if not isinstance(
        safety,
        dict,
    ):
        return False

    for key, required in (
        _REQUIRED_SAFETY_VALUES.items()
    ):
        if safety.get(key) is not required:
            return False

    return True


def persist_sanitized_learning_contribution(
    contribution: dict[str, Any],
) -> dict[str, Any]:
    candidate = deepcopy(
        contribution
    )

    if not validate_sanitized_contribution(
        candidate
    ):
        raise ValueError(
            "Sanitized learning contribution failed validation."
        )

    contribution_id = str(
        candidate[
            "contribution_id"
        ]
    ).strip()

    if not contribution_id:
        raise ValueError(
            "Learning contribution ID is required."
        )

    envelope = {
        "ledger_version":
            _LEDGER_VERSION,

        "ledger_entry_id":
            "learning_entry_"
            + uuid4().hex,

        "persisted_at":
            _utc_now(),

        "contribution":
            candidate,

        "safety": {
            "append_only":
                True,

            "customer_identity_persisted":
                False,

            "session_identity_persisted":
                False,

            "portfolio_data_persisted":
                False,

            "order_data_persisted":
                False,

            "chat_content_persisted":
                False,

            "authentication_data_persisted":
                False,

            "database_write":
                False,

            "strategy_promotion":
                False,

            "broker_execution":
                False,

            "live_execution":
                False,
        },
    }

    if _contains_forbidden_key(
        envelope
    ):
        raise ValueError(
            "Learning-ledger envelope contains a forbidden key."
        )

    _LEDGER_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination = (
        _LEDGER_ROOT
        / f"{contribution_id}.json"
    )

    if destination.exists():
        existing = json.loads(
            destination.read_text(
                encoding="utf-8",
            )
        )

        return {
            "status":
                "already_persisted",

            "ledger_entry_id":
                existing.get(
                    "ledger_entry_id"
                ),

            "contribution_id":
                contribution_id,

            "ledger_path":
                str(destination),

            "index_path":
                str(_LEDGER_INDEX),

            "artifacts_written":
                0,

            "learning_updates":
                0,
        }

    rendered = (
        json.dumps(
            envelope,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
            default=str,
        )
        + "\n"
    )

    jsonl_line = (
        json.dumps(
            envelope,
            ensure_ascii=False,
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
            default=str,
        )
        + "\n"
    )

    temporary = destination.with_suffix(
        ".json.tmp"
    )

    with _LOCK:
        if destination.exists():
            existing = json.loads(
                destination.read_text(
                    encoding="utf-8",
                )
            )

            return {
                "status":
                    "already_persisted",

                "ledger_entry_id":
                    existing.get(
                        "ledger_entry_id"
                    ),

                "contribution_id":
                    contribution_id,

                "ledger_path":
                    str(destination),

                "index_path":
                    str(_LEDGER_INDEX),

                "artifacts_written":
                    0,

                "learning_updates":
                    0,
            }

        temporary.write_text(
            rendered,
            encoding="utf-8",
        )

        temporary.replace(
            destination
        )

        with _LEDGER_INDEX.open(
            "a",
            encoding="utf-8",
        ) as handle:
            handle.write(
                jsonl_line
            )

            handle.flush()

    return {
        "status":
            "persisted",

        "ledger_entry_id":
            envelope[
                "ledger_entry_id"
            ],

        "contribution_id":
            contribution_id,

        "ledger_path":
            str(destination),

        "index_path":
            str(_LEDGER_INDEX),

        "artifacts_written":
            1,

        "learning_updates":
            1,
    }


def get_learning_contribution(
    contribution_id: str,
) -> dict[str, Any] | None:
    normalized = str(
        contribution_id
        or ""
    ).strip()

    if not normalized:
        return None

    path = (
        _LEDGER_ROOT
        / f"{normalized}.json"
    )

    if not path.is_file():
        return None

    payload = json.loads(
        path.read_text(
            encoding="utf-8",
        )
    )

    if not isinstance(
        payload,
        dict,
    ):
        return None

    return payload


def list_learning_contributions(
    *,
    limit: int = 100,
) -> list[dict[str, Any]]:
    resolved_limit = max(
        1,
        min(
            int(limit),
            1000,
        ),
    )

    if not _LEDGER_INDEX.is_file():
        return []

    records: list[
        dict[str, Any]
    ] = []

    with _LEDGER_INDEX.open(
        "r",
        encoding="utf-8",
    ) as handle:
        for line in handle:
            stripped = line.strip()

            if not stripped:
                continue

            try:
                payload = json.loads(
                    stripped
                )
            except json.JSONDecodeError:
                continue

            if isinstance(
                payload,
                dict,
            ):
                records.append(
                    payload
                )

    return records[
        -resolved_limit:
    ]


def learning_ledger_status() -> dict[str, Any]:
    contribution_count = 0

    if _LEDGER_ROOT.is_dir():
        contribution_count = len(
            list(
                _LEDGER_ROOT.glob(
                    "contribution_*.json"
                )
            )
        )

    return {
        "ledger_enabled":
            True,

        "ledger_version":
            _LEDGER_VERSION,

        "ledger_root":
            str(_LEDGER_ROOT),

        "index_path":
            str(_LEDGER_INDEX),

        "persisted_contribution_count":
            contribution_count,

        "append_only":
            True,

        "database_writes_enabled":
            False,

        "strategy_promotion_enabled":
            False,

        "broker_execution_enabled":
            False,

        "live_execution_enabled":
            False,

        "customer_identity_allowed":
            False,

        "session_identity_allowed":
            False,

        "portfolio_data_allowed":
            False,

        "order_data_allowed":
            False,

        "chat_content_allowed":
            False,

        "authentication_data_allowed":
            False,
    }


__all__ = [
    "get_learning_contribution",
    "learning_ledger_status",
    "list_learning_contributions",
    "persist_sanitized_learning_contribution",
    "validate_sanitized_contribution",
]

"""
Sanitized bounded-training confidence pipeline.

Reuses the existing NeuroVest learning path:

    OHLCV row
        -> build_learning_artifact
        -> feature extraction
        -> reward scoring
        -> strategy knowledge object
        -> symbol intelligence profile
        -> sanitized confidence summary

No strategy promotion, database mutation, portfolio mutation, order
creation, broker request, or live execution is permitted here.
"""

from __future__ import annotations

from backend.app.stacks.strategy_candidate_sandbox.training_candidate_contract import (
    build_training_candidate_contract,
    validate_training_candidate_contract,
)
from backend.app.stacks.strategy_candidate_sandbox.training_window_contract import (
    apply_training_window,
    build_close_prefix_sums,
    build_training_window_contract,
    candidate_decision_from_prefix,
    validate_training_window_contract,
)

from pathlib import Path
from typing import Any
import csv
import math

from backend.app.stacks.strategy_candidate_sandbox.L3_service_facade.learning_artifact_pipeline import (
    build_learning_artifact,
)

from backend.app.stacks.strategy_candidate_sandbox.learning_artifact_contract import (
    validate_learning_artifact_contract,
)

from backend.app.stacks.strategy_candidate_sandbox.strategy_knowledge_object import (
    build_strategy_knowledge_object_from_learning_artifact,
    validate_strategy_knowledge_object,
)

from backend.app.stacks.strategy_candidate_sandbox.symbol_intelligence_profile import (
    build_symbol_intelligence_profile,
)


_PIPELINE_VERSION = 1

_REQUIRED_COLUMNS = {
    "open",
    "high",
    "low",
    "close",
    "volume",
}

_FORBIDDEN_KEYS = {
    "owner_user_id",
    "owner_session_id",
    "user_id",
    "session_id",
    "email",
    "display_name",
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


def _finite_float(
    value: Any,
) -> float | None:
    try:
        resolved = float(value)
    except (
        TypeError,
        ValueError,
    ):
        return None

    if not math.isfinite(resolved):
        return None

    return resolved



def _read_full_ohlcv_rows(
    path: Path,
    *,
    training_window: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        reader = csv.DictReader(
            handle
        )

        for raw in reader:
            normalized = {
                str(key).strip().lower():
                    value
                for key, value in raw.items()
                if key is not None
            }

            if not _REQUIRED_COLUMNS.issubset(
                normalized
            ):
                continue

            values = {
                key:
                    _finite_float(
                        normalized.get(key)
                    )
                for key in _REQUIRED_COLUMNS
            }

            if any(
                value is None
                for value in values.values()
            ):
                continue

            date_value = (
                normalized.get("date")
                or normalized.get("datetime")
                or normalized.get("timestamp")
                or ""
            )

            rows.append(
                {
                    "date":
                        str(date_value),

                    "open":
                        float(values["open"]),

                    "high":
                        float(values["high"]),

                    "low":
                        float(values["low"]),

                    "close":
                        float(values["close"]),

                    "volume":
                        float(values["volume"]),
                }
            )

    return apply_training_window(
        rows,
        timestamps=[
            str(
                row.get("date")
                or ""
            )
            for row in rows
        ],
        window=training_window,
    )



def _decision_for_row(
    *,
    closes: list[float],
    prefix_sums: list[float],
    index: int,
    training_candidate: dict[str, Any],
) -> str:
    return candidate_decision_from_prefix(
        closes=closes,
        prefix_sums=prefix_sums,
        index=index,
        candidate=training_candidate,
    )


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


def build_bounded_training_confidence_summary(
    *,
    run_id: str,
    datasets: list[dict[str, Any]],
    training_candidate: dict[str, Any] | None = None,
    training_window: dict[str, Any] | None = None,
) -> dict[str, Any]:
    resolved_candidate = (
        build_training_candidate_contract(
            created_from="manual",
        ).to_dict()
        if training_candidate is None
        else dict(training_candidate)
    )

    resolved_window = (
        build_training_window_contract().to_dict()
        if training_window is None
        else dict(training_window)
    )

    if not validate_training_candidate_contract(
        resolved_candidate
    ):
        raise ValueError(
            "invalid confidence training candidate"
        )

    if not validate_training_window_contract(
        resolved_window
    ):
        raise ValueError(
            "invalid confidence training window"
        )
    symbol_summaries: list[
        dict[str, Any]
    ] = []

    total_artifacts = 0
    total_observations = 0
    invalid_datasets = 0

    weighted_reward = 0.0
    weighted_confidence = 0.0

    for dataset in datasets:
        symbol = str(
            dataset.get("symbol")
            or ""
        ).strip().upper()

        path_value = dataset.get("path")

        if not symbol or not path_value:
            invalid_datasets += 1
            continue

        path = Path(path_value)

        if not path.is_file():
            invalid_datasets += 1
            continue

        rows = _read_full_ohlcv_rows(
            path,
            training_window=(
                resolved_window
            ),
        )

        closes = [
            float(
                row["close"]
            )
            for row in rows
        ]

        prefix_sums = (
            build_close_prefix_sums(
                closes
            )
        )

        if len(rows) < 2:
            invalid_datasets += 1
            continue

        knowledge_objects: list[
            dict[str, Any]
        ] = []

        for index in range(
            len(rows) - 1
        ):
            row = rows[index]
            next_row = rows[index + 1]

            previous_close = (
                float(
                    rows[index - 1]["close"]
                )
                if index > 0
                else None
            )

            current_close = float(
                row["close"]
            )

            next_close = float(
                next_row["close"]
            )

            decision = _decision_for_row(
                closes=closes,
                prefix_sums=prefix_sums,
                index=index,
                training_candidate=(
                    resolved_candidate
                ),
            )

            artifact = build_learning_artifact(
                run_id=run_id,
                symbol=symbol,
                row=row,
                previous_close=previous_close,
                next_close=next_close,
                decision=decision,
                cycle=index + 1,
            )

            if not validate_learning_artifact_contract(
                artifact
            ):
                continue

            knowledge = (
                build_strategy_knowledge_object_from_learning_artifact(
                    artifact,
                    strategy_name=(
                        "Bounded Historical "
                        "Direction Replay"
                    ),
                    strategy_family=(
                        "BOUNDED_HISTORICAL_REPLAY"
                    ),
                )
            )

            if not validate_strategy_knowledge_object(
                knowledge
            ):
                continue

            knowledge_objects.append(
                knowledge
            )

        if not knowledge_objects:
            invalid_datasets += 1
            continue

        profile = (
            build_symbol_intelligence_profile(
                symbol=symbol,
                knowledge_objects=knowledge_objects,
            )
        )

        observations = int(
            profile.get(
                "observations",
                0,
            )
            or 0
        )

        average_reward = float(
            profile.get(
                "average_reward",
                0.0,
            )
            or 0.0
        )

        average_confidence = float(
            profile.get(
                "average_confidence",
                0.0,
            )
            or 0.0
        )

        average_confidence = max(
            0.0,
            min(
                average_confidence,
                1.0,
            ),
        )

        symbol_summaries.append(
            {
                "symbol":
                    symbol,

                "observations":
                    observations,

                "average_reward":
                    round(
                        average_reward,
                        8,
                    ),

                "average_confidence":
                    round(
                        average_confidence,
                        8,
                    ),
            }
        )

        total_artifacts += len(
            knowledge_objects
        )

        total_observations += (
            observations
        )

        weighted_reward += (
            average_reward
            * observations
        )

        weighted_confidence += (
            average_confidence
            * observations
        )

    symbol_summaries.sort(
        key=lambda item:
            item["symbol"]
    )

    confidence_values = [
        float(
            item["average_confidence"]
        )
        for item in symbol_summaries
        if int(
            item.get(
                "observations",
                0,
            )
        ) > 0
    ]

    average_reward = (
        weighted_reward
        / total_observations
        if total_observations
        else 0.0
    )

    average_confidence = (
        weighted_confidence
        / total_observations
        if total_observations
        else 0.0
    )

    summary = {
        "learning_pipeline_version":
            _PIPELINE_VERSION,

        "learning_pipeline":
            (
                "feature_reward_artifact_"
                "knowledge_profile"
            ),

        "candidate_id":
            resolved_candidate[
                "candidate_id"
            ],

        "training_candidate":
            dict(
                resolved_candidate
            ),

        "training_window_id":
            resolved_window[
                "training_window_id"
            ],

        "training_window":
            dict(
                resolved_window
            ),

        "window_start":
            resolved_window[
                "window_start"
            ],

        "window_end":
            resolved_window[
                "window_end"
            ],

        "lookback_rows":
            resolved_window[
                "lookback_rows"
            ],

        "row_offset":
            resolved_window[
                "row_offset"
            ],

        "round_number":
            resolved_window[
                "round_number"
            ],

        "maximum_rounds":
            resolved_window[
                "maximum_rounds"
            ],

        "valid_learning_artifacts":
            total_artifacts,

        "learning_observations":
            total_observations,

        "average_reward":
            round(
                average_reward,
                8,
            ),

        "average_confidence":
            round(
                average_confidence,
                8,
            ),

        "minimum_symbol_confidence":
            round(
                min(confidence_values)
                if confidence_values
                else 0.0,
                8,
            ),

        "maximum_symbol_confidence":
            round(
                max(confidence_values)
                if confidence_values
                else 0.0,
                8,
            ),

        "symbols_with_valid_confidence":
            len(confidence_values),

        "invalid_confidence_datasets":
            invalid_datasets,

        "symbol_confidence":
            symbol_summaries,

        "confidence_safety": {
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

            "database_writes":
                False,

            "strategy_mutation":
                False,

            "strategy_promotion":
                False,

            "paper_orders":
                False,

            "broker_execution":
                False,

            "live_execution":
                False,
        },
    }

    forbidden = _contains_forbidden_key(
        summary
    )

    if forbidden:
        raise ValueError(
            "Confidence summary contains "
            f"forbidden key: {forbidden}"
        )

    return summary


__all__ = [
    "build_bounded_training_confidence_summary",
]

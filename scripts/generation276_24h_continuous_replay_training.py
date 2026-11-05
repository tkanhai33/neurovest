#!/usr/bin/env python3

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import argparse
import hashlib
import json
import math
import os
import sys
import time

import joblib
import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
)


DEFAULT_PACKAGE = Path(
    "runtime/training/"
    "generation275_checkpointed_long_training_20260806_191828/"
    "checkpoints/checkpoint_002_iter_165/candidate_package.joblib"
)

DEFAULT_DATASET = Path(
    "runtime/training/"
    "generation274_challenger_confirmation_freeze_20260806_085814/"
    "evidence/inputs/training_dataset.csv"
)


def finite_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(key): finite_json(child)
            for key, child in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            finite_json(child)
            for child in value
        ]

    if isinstance(value, np.generic):
        value = value.item()

    if (
        isinstance(value, float)
        and not math.isfinite(value)
    ):
        return None

    return value


def write_json(
    path: Path,
    value: Any,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            finite_json(value),
            indent=2,
            sort_keys=True,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )


def sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def find_estimator(
    package: Any,
) -> tuple[str, Any]:
    if (
        hasattr(package, "fit")
        and hasattr(package, "predict")
    ):
        return "package_root", package

    if not isinstance(package, dict):
        raise RuntimeError(
            "Candidate package is neither "
            "a dictionary nor estimator."
        )

    preferred = (
        "model",
        "estimator",
        "pipeline",
        "classifier",
        "regressor",
        "learner",
        "winner_model",
        "candidate_model",
        "fitted_model",
    )

    for key in preferred:
        value = package.get(key)

        if (
            hasattr(value, "fit")
            and hasattr(value, "predict")
        ):
            return key, value

    for key, value in package.items():
        if (
            hasattr(value, "fit")
            and hasattr(value, "predict")
        ):
            return str(key), value

    raise RuntimeError(
        "No trainable estimator found "
        "inside candidate package."
    )


def package_with_estimator(
    original: Any,
    estimator_key: str,
    estimator: Any,
) -> Any:
    if estimator_key == "package_root":
        return estimator

    package = deepcopy(original)

    package[
        estimator_key
    ] = estimator

    if isinstance(package, dict):
        package[
            "generation276_continuous_training"
        ] = {
            "updated_at":
                datetime.now(
                    UTC
                ).isoformat(),

            "training_mode":
                "24h_continuous_frozen_replay",

            "registration":
                False,

            "promotion":
                False,

            "runtime_activation":
                False,
        }

    return package


def metrics(
    actual: pd.Series,
    predicted: np.ndarray,
) -> dict[str, float]:
    return {
        "accuracy":
            float(
                accuracy_score(
                    actual,
                    predicted,
                )
            ),

        "balanced_accuracy":
            float(
                balanced_accuracy_score(
                    actual,
                    predicted,
                )
            ),

        "f1_macro":
            float(
                f1_score(
                    actual,
                    predicted,
                    average="macro",
                    zero_division=0,
                )
            ),
    }


def prediction_change(
    first: np.ndarray,
    second: np.ndarray,
) -> float:
    if len(first) != len(second):
        raise RuntimeError(
            "Prediction arrays have "
            "different lengths."
        )

    if len(first) == 0:
        return 0.0

    return float(
        np.mean(
            first != second
        )
    )


def estimator_iteration_state(
    estimator: Any,
) -> dict[str, Any]:
    record: dict[str, Any] = {}

    for attribute in (
        "max_iter",
        "n_iter_",
        "n_estimators",
        "n_estimators_",
        "warm_start",
    ):
        if hasattr(
            estimator,
            attribute,
        ):
            try:
                value = getattr(
                    estimator,
                    attribute,
                )

                if isinstance(
                    value,
                    np.generic,
                ):
                    value = value.item()

                record[
                    attribute
                ] = value

            except Exception:
                pass

    return record


def configure_next_iteration(
    estimator: Any,
    increment: int,
) -> tuple[str, int, int]:
    if hasattr(
        estimator,
        "warm_start",
    ):
        try:
            estimator.set_params(
                warm_start=True
            )
        except Exception:
            try:
                estimator.warm_start = True
            except Exception:
                pass

    if hasattr(
        estimator,
        "max_iter",
    ):
        current = int(
            getattr(
                estimator,
                "max_iter",
            )
        )

        target = (
            current
            + increment
        )

        try:
            estimator.set_params(
                max_iter=target
            )
        except Exception:
            estimator.max_iter = target

        return (
            "max_iter",
            current,
            target,
        )

    if hasattr(
        estimator,
        "n_estimators",
    ):
        current = int(
            getattr(
                estimator,
                "n_estimators",
            )
        )

        target = (
            current
            + increment
        )

        try:
            estimator.set_params(
                n_estimators=target
            )
        except Exception:
            estimator.n_estimators = target

        return (
            "n_estimators",
            current,
            target,
        )

    raise RuntimeError(
        "Estimator exposes neither "
        "max_iter nor n_estimators."
    )


parser = argparse.ArgumentParser(
    description=(
        "Generation 276 real 24-hour "
        "continuous replay training."
    )
)

parser.add_argument(
    "--output-root",
    required=True,
)

parser.add_argument(
    "--duration-hours",
    type=float,
    default=24.0,
)

parser.add_argument(
    "--cycle-minutes",
    type=float,
    default=5.0,
)

parser.add_argument(
    "--iterations-per-cycle",
    type=int,
    default=5,
)

parser.add_argument(
    "--phase-two-end-fraction",
    type=float,
    default=0.80,
)

parser.add_argument(
    "--balanced-accuracy-tolerance",
    type=float,
    default=0.003,
)

parser.add_argument(
    "--f1-tolerance",
    type=float,
    default=0.003,
)

parser.add_argument(
    "--package",
    default=str(
        DEFAULT_PACKAGE
    ),
)

parser.add_argument(
    "--dataset",
    default=str(
        DEFAULT_DATASET
    ),
)

args = parser.parse_args()

if args.duration_hours < 24.0:
    raise SystemExit(
        "Generation 276 requires "
        "at least 24 hours."
    )

if args.iterations_per_cycle <= 0:
    raise SystemExit(
        "iterations-per-cycle "
        "must be positive."
    )

output_root = Path(
    args.output_root
)

package_path = Path(
    args.package
)

dataset_path = Path(
    args.dataset
)

checkpoint_root = (
    output_root
    / "checkpoints"
)

heartbeat_root = (
    output_root
    / "heartbeats"
)

resume_root = (
    output_root
    / "resume"
)

for path in (
    output_root,
    checkpoint_root,
    heartbeat_root,
    resume_root,
):
    path.mkdir(
        parents=True,
        exist_ok=True,
    )

result_path = (
    output_root
    / "result.json"
)

state_path = (
    output_root
    / "resume_state.json"
)

history_path = (
    output_root
    / "cycle_history.jsonl"
)

report_path = (
    output_root
    / "report.txt"
)

manifest_path = (
    output_root
    / "evidence_manifest.json"
)

if not package_path.is_file():
    raise SystemExit(
        "BLOCKED: starting package missing: "
        + str(package_path)
    )

if not dataset_path.is_file():
    raise SystemExit(
        "BLOCKED: dataset missing: "
        + str(dataset_path)
    )

package_hash_before = sha256_file(
    package_path
)

dataset_hash_before = sha256_file(
    dataset_path
)

original_package = joblib.load(
    package_path
)

estimator_key, starting_estimator = (
    find_estimator(
        original_package
    )
)

if not isinstance(
    original_package,
    dict,
):
    raise SystemExit(
        "BLOCKED: starting package "
        "metadata is unavailable."
    )

features = [
    str(value)
    for value
    in original_package.get(
        "features",
        [],
    )
]

target = str(
    original_package.get(
        "target",
        "",
    )
)

if len(features) != 18:
    raise SystemExit(
        "BLOCKED: expected exactly "
        "18 model features."
    )

if not target:
    raise SystemExit(
        "BLOCKED: package target missing."
    )

header = [
    str(column)
    for column
    in pd.read_csv(
        dataset_path,
        nrows=0,
    ).columns
]

missing = sorted(
    set(
        features
        + [target]
    )
    - set(header)
)

if missing:
    raise SystemExit(
        "BLOCKED: dataset missing columns:\n  "
        + "\n  ".join(
            missing
        )
    )

timestamp_column = next(
    (
        column
        for column in (
            "timestamp",
            "date",
            "datetime",
            "market_date",
            "bar_time",
            "event_time",
        )
        if column in header
    ),
    None,
)

use_columns = list(
    dict.fromkeys(
        (
            [timestamp_column]
            if timestamp_column
            else []
        )
        + features
        + [target]
    )
)

frame = pd.read_csv(
    dataset_path,
    usecols=use_columns,
    low_memory=False,
)

if timestamp_column:
    frame[
        timestamp_column
    ] = pd.to_datetime(
        frame[
            timestamp_column
        ],
        errors="coerce",
        utc=True,
    )

    frame = frame.dropna(
        subset=[
            timestamp_column,
        ]
    )

    frame = frame.sort_values(
        timestamp_column,
        kind="stable",
    )

for feature in features:
    frame[
        feature
    ] = pd.to_numeric(
        frame[
            feature
        ],
        errors="coerce",
    )

frame = frame.replace(
    [np.inf, -np.inf],
    np.nan,
)

frame = frame.dropna(
    subset=
        features
        + [target]
)

frame[
    target
] = (
    frame[
        target
    ]
    .astype(str)
)

frame = frame.reset_index(
    drop=True
)

row_count = int(
    len(frame)
)

split_index = int(
    row_count
    * args.phase_two_end_fraction
)

if not (
    0
    < split_index
    < row_count
):
    raise SystemExit(
        "BLOCKED: invalid chronological split."
    )

training_frame = frame.iloc[
    :split_index
].copy()

holdout_frame = frame.iloc[
    split_index:
].copy()

X_train = training_frame[
    features
]

y_train = training_frame[
    target
]

X_holdout = holdout_frame[
    features
]

y_holdout = holdout_frame[
    target
]

current_estimator = deepcopy(
    starting_estimator
)

best_estimator = deepcopy(
    starting_estimator
)

starting_prediction = np.asarray(
    starting_estimator.predict(
        X_holdout
    )
).astype(str)

current_prediction = (
    starting_prediction.copy()
)

best_prediction = (
    starting_prediction.copy()
)

starting_metrics = metrics(
    y_holdout,
    starting_prediction,
)

current_metrics = dict(
    starting_metrics
)

best_metrics = dict(
    starting_metrics
)

cycle_number = 0
accepted_cycles = 0
rejected_cycles = 0
rollback_count = 0

started_wall = time.time()
deadline = (
    started_wall
    + (
        args.duration_hours
        * 3600.0
    )
)

started_at = datetime.now(
    UTC
).isoformat()

cycle_seconds = (
    args.cycle_minutes
    * 60.0
)

joblib.dump(
    current_estimator,
    resume_root
    / "current_estimator.joblib",
)

joblib.dump(
    best_estimator,
    resume_root
    / "best_estimator.joblib",
)

joblib.dump(
    package_with_estimator(
        original_package,
        estimator_key,
        current_estimator,
    ),
    resume_root
    / "current_candidate_package.joblib",
)

joblib.dump(
    package_with_estimator(
        original_package,
        estimator_key,
        best_estimator,
    ),
    resume_root
    / "best_candidate_package.joblib",
)

print()
print("=" * 110)
print(
    "NEUROVEST — GENERATION 276 "
    "REAL 24-HOUR CONTINUOUS TRAINING"
)
print("=" * 110)
print(
    "Duration hours:",
    args.duration_hours,
)
print(
    "Cycle minutes:",
    args.cycle_minutes,
)
print(
    "Iterations per cycle:",
    args.iterations_per_cycle,
)
print(
    "Training rows:",
    len(training_frame),
)
print(
    "Frozen holdout rows:",
    len(holdout_frame),
)
print(
    "Starting iteration state:",
    estimator_iteration_state(
        starting_estimator
    ),
)
print(
    "Starting balanced accuracy:",
    starting_metrics[
        "balanced_accuracy"
    ],
)
print(
    "Starting F1 macro:",
    starting_metrics[
        "f1_macro"
    ],
)
print()
print(
    "Registration: disabled"
)
print(
    "Promotion: disabled"
)
print(
    "Parent replacement: disabled"
)
print(
    "Runtime activation: disabled"
)
print(
    "Orders: disabled"
)
print()

try:
    while time.time() < deadline:
        cycle_number += 1

        cycle_started = (
            time.time()
        )

        candidate = deepcopy(
            current_estimator
        )

        (
            iteration_parameter,
            previous_iteration,
            target_iteration,
        ) = configure_next_iteration(
            candidate,
            args.iterations_per_cycle,
        )

        print()
        print("=" * 110)
        print(
            "CYCLE",
            cycle_number,
        )
        print("=" * 110)
        print(
            "Iteration parameter:",
            iteration_parameter,
        )
        print(
            "Previous:",
            previous_iteration,
        )
        print(
            "Target:",
            target_iteration,
        )
        print(
            "Training started:",
            datetime.now(
                UTC
            ).isoformat(),
        )

        fit_started = (
            time.time()
        )

        candidate.fit(
            X_train,
            y_train,
        )

        fit_seconds = (
            time.time()
            - fit_started
        )

        candidate_prediction = np.asarray(
            candidate.predict(
                X_holdout
            )
        ).astype(str)

        candidate_metrics = metrics(
            y_holdout,
            candidate_prediction,
        )

        change_from_previous = (
            prediction_change(
                current_prediction,
                candidate_prediction,
            )
        )

        change_from_start = (
            prediction_change(
                starting_prediction,
                candidate_prediction,
            )
        )

        balanced_degradation = (
            best_metrics[
                "balanced_accuracy"
            ]
            - candidate_metrics[
                "balanced_accuracy"
            ]
        )

        f1_degradation = (
            best_metrics[
                "f1_macro"
            ]
            - candidate_metrics[
                "f1_macro"
            ]
        )

        within_degradation = bool(
            balanced_degradation
            <= args.balanced_accuracy_tolerance
            and f1_degradation
            <= args.f1_tolerance
        )

        accepted = (
            within_degradation
        )

        improved_best = bool(
            candidate_metrics[
                "balanced_accuracy"
            ]
            > best_metrics[
                "balanced_accuracy"
            ]
            or (
                math.isclose(
                    candidate_metrics[
                        "balanced_accuracy"
                    ],
                    best_metrics[
                        "balanced_accuracy"
                    ],
                    rel_tol=0.0,
                    abs_tol=1e-15,
                )
                and candidate_metrics[
                    "f1_macro"
                ]
                > best_metrics[
                    "f1_macro"
                ]
            )
        )

        if accepted:
            current_estimator = (
                candidate
            )

            current_prediction = (
                candidate_prediction
            )

            current_metrics = dict(
                candidate_metrics
            )

            accepted_cycles += 1

            if improved_best:
                best_estimator = deepcopy(
                    candidate
                )

                best_prediction = (
                    candidate_prediction.copy()
                )

                best_metrics = dict(
                    candidate_metrics
                )

        else:
            rejected_cycles += 1
            rollback_count += 1

            current_estimator = deepcopy(
                best_estimator
            )

            current_prediction = (
                best_prediction.copy()
            )

            current_metrics = dict(
                best_metrics
            )

        checkpoint_name = (
            "cycle_"
            + str(
                cycle_number
            ).zfill(4)
            + "_iter_"
            + str(
                target_iteration
            )
        )

        checkpoint_dir = (
            checkpoint_root
            / checkpoint_name
        )

        checkpoint_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        joblib.dump(
            candidate,
            checkpoint_dir
            / "trained_estimator.joblib",
        )

        joblib.dump(
            package_with_estimator(
                original_package,
                estimator_key,
                candidate,
            ),
            checkpoint_dir
            / "trained_candidate_package.joblib",
        )

        cycle_record = {
            "cycle":
                cycle_number,

            "checkpoint":
                checkpoint_name,

            "started_at":
                datetime.now(
                    UTC
                ).isoformat(),

            "fit_seconds":
                fit_seconds,

            "iteration_parameter":
                iteration_parameter,

            "previous_iteration":
                previous_iteration,

            "requested_iteration":
                target_iteration,

            "effective_iteration_state":
                estimator_iteration_state(
                    candidate
                ),

            "metrics":
                candidate_metrics,

            "prediction_change_from_previous":
                change_from_previous,

            "prediction_change_from_start":
                change_from_start,

            "balanced_accuracy_degradation_from_best":
                balanced_degradation,

            "f1_degradation_from_best":
                f1_degradation,

            "within_degradation_limit":
                within_degradation,

            "accepted":
                accepted,

            "improved_best":
                improved_best
                if accepted
                else False,

            "rollback_performed":
                not accepted,

            "current_metrics_after_cycle":
                current_metrics,

            "best_metrics_after_cycle":
                best_metrics,

            "authorization": {
                "register_candidate":
                    False,

                "promote_candidate":
                    False,

                "replace_parent_model":
                    False,

                "runtime_activation":
                    False,

                "paper_execution":
                    False,

                "broker_execution":
                    False,

                "live_execution":
                    False,
            },
        }

        write_json(
            checkpoint_dir
            / "metrics.json",
            cycle_record,
        )

        with history_path.open(
            "a",
            encoding="utf-8",
        ) as handle:
            handle.write(
                json.dumps(
                    finite_json(
                        cycle_record
                    ),
                    sort_keys=True,
                    default=str,
                )
                + "\n"
            )

        joblib.dump(
            current_estimator,
            resume_root
            / "current_estimator.joblib",
        )

        joblib.dump(
            best_estimator,
            resume_root
            / "best_estimator.joblib",
        )

        joblib.dump(
            package_with_estimator(
                original_package,
                estimator_key,
                current_estimator,
            ),
            resume_root
            / "current_candidate_package.joblib",
        )

        joblib.dump(
            package_with_estimator(
                original_package,
                estimator_key,
                best_estimator,
            ),
            resume_root
            / "best_candidate_package.joblib",
        )

        state = {
            "classification":
                "generation276_24h_continuous_training_state",

            "started_at":
                started_at,

            "updated_at":
                datetime.now(
                    UTC
                ).isoformat(),

            "duration_hours":
                args.duration_hours,

            "cycle_minutes":
                args.cycle_minutes,

            "cycle_number":
                cycle_number,

            "accepted_cycles":
                accepted_cycles,

            "rejected_cycles":
                rejected_cycles,

            "rollback_count":
                rollback_count,

            "starting_metrics":
                starting_metrics,

            "current_metrics":
                current_metrics,

            "best_metrics":
                best_metrics,

            "current_iteration_state":
                estimator_iteration_state(
                    current_estimator
                ),

            "best_iteration_state":
                estimator_iteration_state(
                    best_estimator
                ),

            "seconds_elapsed":
                time.time()
                - started_wall,

            "seconds_remaining":
                max(
                    0.0,
                    deadline
                    - time.time(),
                ),

            "training_performed":
                accepted_cycles
                + rejected_cycles
                > 0,

            "safety": {
                "candidate_registered":
                    False,

                "candidate_promoted":
                    False,

                "parent_replaced":
                    False,

                "runtime_activated":
                    False,

                "orders_submitted":
                    0,
            },
        }

        write_json(
            state_path,
            state,
        )

        write_json(
            heartbeat_root
            / (
                "cycle_"
                + str(
                    cycle_number
                ).zfill(4)
                + ".json"
            ),
            cycle_record,
        )

        print(
            "Balanced accuracy:",
            candidate_metrics[
                "balanced_accuracy"
            ],
        )
        print(
            "F1 macro:",
            candidate_metrics[
                "f1_macro"
            ],
        )
        print(
            "Prediction change previous:",
            change_from_previous,
        )
        print(
            "Prediction change start:",
            change_from_start,
        )
        print(
            "Fit seconds:",
            fit_seconds,
        )
        print(
            "Accepted:",
            accepted,
        )
        print(
            "New best:",
            (
                improved_best
                if accepted
                else False
            ),
        )
        print(
            "Rollback:",
            not accepted,
        )
        print(
            "Accepted cycles:",
            accepted_cycles,
        )
        print(
            "Rejected cycles:",
            rejected_cycles,
        )
        print(
            "Current iteration state:",
            estimator_iteration_state(
                current_estimator
            ),
        )
        print(
            "Hours elapsed:",
            (
                time.time()
                - started_wall
            )
            / 3600.0,
        )

        sys.stdout.flush()

        cycle_elapsed = (
            time.time()
            - cycle_started
        )

        sleep_seconds = max(
            0.0,
            cycle_seconds
            - cycle_elapsed,
        )

        remaining = (
            deadline
            - time.time()
        )

        if remaining <= 0:
            break

        if sleep_seconds > 0:
            time.sleep(
                min(
                    sleep_seconds,
                    remaining,
                )
            )

finally:
    package_hash_after = (
        sha256_file(
            package_path
        )
    )

    dataset_hash_after = (
        sha256_file(
            dataset_path
        )
    )

    preservation = {
        "starting_package_preserved":
            package_hash_before
            == package_hash_after,

        "frozen_dataset_preserved":
            dataset_hash_before
            == dataset_hash_after,
    }

    completed_duration = (
        time.time()
        - started_wall
    )

    duration_requirement_met = bool(
        completed_duration
        >= (
            args.duration_hours
            * 3600.0
            - 5.0
        )
    )

    training_performed = bool(
        accepted_cycles
        + rejected_cycles
        > 0
    )

    completed = bool(
        duration_requirement_met
        and training_performed
        and all(
            preservation.values()
        )
    )

    final_result = {
        "classification":
            (
                "generation276_24h_continuous_training_complete"
                if completed
                else
                "generation276_24h_continuous_training_incomplete"
            ),

        "passed":
            completed,

        "training_completed":
            completed,

        "duration_requirement_met":
            duration_requirement_met,

        "training_performed":
            training_performed,

        "started_at":
            started_at,

        "completed_at":
            datetime.now(
                UTC
            ).isoformat(),

        "requested_duration_hours":
            args.duration_hours,

        "actual_duration_hours":
            completed_duration
            / 3600.0,

        "cycles_completed":
            cycle_number,

        "accepted_cycles":
            accepted_cycles,

        "rejected_cycles":
            rejected_cycles,

        "rollback_count":
            rollback_count,

        "iterations_per_cycle":
            args.iterations_per_cycle,

        "starting_iteration_state":
            estimator_iteration_state(
                starting_estimator
            ),

        "current_iteration_state":
            estimator_iteration_state(
                current_estimator
            ),

        "best_iteration_state":
            estimator_iteration_state(
                best_estimator
            ),

        "starting_metrics":
            starting_metrics,

        "current_metrics":
            current_metrics,

        "best_metrics":
            best_metrics,

        "preservation":
            preservation,

        "authorization": {
            "register_candidate":
                False,

            "database_registration":
                False,

            "promote_candidate":
                False,

            "replace_parent_model":
                False,

            "runtime_activation":
                False,

            "paper_execution":
                False,

            "broker_execution":
                False,

            "snaptrade_execution":
                False,

            "live_execution":
                False,
        },

        "safety": {
            "source_package_modified":
                False,

            "frozen_dataset_modified":
                False,

            "candidate_registered":
                False,

            "candidate_promoted":
                False,

            "parent_replaced":
                False,

            "runtime_activated":
                False,

            "orders_submitted":
                0,
        },
    }

    write_json(
        result_path,
        final_result,
    )

    manifest = {
        "classification":
            "generation276_24h_continuous_training_evidence_manifest",

        "starting_package": {
            "path":
                str(
                    package_path
                ),

            "sha256":
                package_hash_before,
        },

        "frozen_dataset": {
            "path":
                str(
                    dataset_path
                ),

            "sha256":
                dataset_hash_before,
        },

        "features":
            features,

        "target":
            target,

        "training_rows":
            int(
                len(
                    training_frame
                )
            ),

        "holdout_rows":
            int(
                len(
                    holdout_frame
                )
            ),

        "checkpoints_directory":
            str(
                checkpoint_root
            ),

        "cycle_history":
            str(
                history_path
            ),

        "result":
            str(
                result_path
            ),

        "preservation":
            preservation,
    }

    write_json(
        manifest_path,
        manifest,
    )

    report_lines = [
        "=" * 110,
        "NEUROVEST — GENERATION 276",
        "24-HOUR CONTINUOUS REPLAY TRAINING",
        "=" * 110,
        "",
        "Completed:                    "
        + str(
            completed
        ),

        "Requested duration hours:     "
        + str(
            args.duration_hours
        ),

        "Actual duration hours:        "
        + str(
            completed_duration
            / 3600.0
        ),

        "Cycles completed:             "
        + str(
            cycle_number
        ),

        "Accepted cycles:              "
        + str(
            accepted_cycles
        ),

        "Rejected cycles:              "
        + str(
            rejected_cycles
        ),

        "Rollbacks:                    "
        + str(
            rollback_count
        ),

        "",
        "STARTING METRICS",
        "  Balanced accuracy:           "
        + str(
            starting_metrics[
                "balanced_accuracy"
            ]
        ),

        "  F1 macro:                    "
        + str(
            starting_metrics[
                "f1_macro"
            ]
        ),

        "",
        "BEST METRICS",
        "  Balanced accuracy:           "
        + str(
            best_metrics[
                "balanced_accuracy"
            ]
        ),

        "  F1 macro:                    "
        + str(
            best_metrics[
                "f1_macro"
            ]
        ),

        "",
        "FINAL ITERATION STATE",
        "  "
        + json.dumps(
            estimator_iteration_state(
                current_estimator
            ),
            sort_keys=True,
            default=str,
        ),

        "",
        "BEST ITERATION STATE",
        "  "
        + json.dumps(
            estimator_iteration_state(
                best_estimator
            ),
            sort_keys=True,
            default=str,
        ),

        "",
        "PRESERVATION",
        "  Starting package preserved:  "
        + str(
            preservation[
                "starting_package_preserved"
            ]
        ),

        "  Frozen dataset preserved:    "
        + str(
            preservation[
                "frozen_dataset_preserved"
            ]
        ),

        "",
        "Candidate registration:        False",
        "Candidate promotion:           False",
        "Parent replacement:            False",
        "Runtime activation:            False",
        "Orders submitted:              0",
    ]

    report_path.write_text(
        "\n".join(
            report_lines
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print("=" * 110)
    print(
        "GENERATION 276 "
        "24-HOUR CONTINUOUS TRAINING FINALIZATION"
    )
    print("=" * 110)
    print(
        report_path.read_text(
            encoding="utf-8"
        )
    )

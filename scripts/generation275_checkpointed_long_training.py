#!/usr/bin/env python3
"""
Generation 275 checkpointed long-training runner.

Starts from the qualified Generation 275B +15 candidate package.

The runner writes only isolated checkpoint artifacts. Candidate
registration, database registration, promotion, parent replacement,
runtime activation, service restart, paper execution, broker
execution, SnapTrade execution, and live execution are disabled.
"""

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
import pickle
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


REPO_ROOT = Path(__file__).resolve().parents[1]

SOURCE_FREEZE_ROOT = (
    REPO_ROOT
    / "runtime"
    / "training"
    / "generation275b_repaired_effective_iteration_sensitivity_20260806_190837"
)

SOURCE_RESULT_PATH = (
    SOURCE_FREEZE_ROOT
    / "result.json"
)

START_PACKAGE_PATH = (
    SOURCE_FREEZE_ROOT
    / "branches"
    / "plus_15"
    / "models"
    / "continued_candidate_package.joblib"
)

START_MODEL_PATH = (
    SOURCE_FREEZE_ROOT
    / "branches"
    / "plus_15"
    / "models"
    / "continued_estimator.joblib"
)

DATASET_PATH = (
    REPO_ROOT
    / "runtime"
    / "training"
    / "generation274_challenger_confirmation_freeze_20260806_085814"
    / "evidence"
    / "inputs"
    / "training_dataset.csv"
)

EXPECTED_FEATURE_COUNT = 18
EXPECTED_START_N_ITER = 115

DISABLED_OPERATIONS = {
    "candidate_registration": False,
    "database_registration": False,
    "candidate_promotion": False,
    "parent_model_replacement": False,
    "runtime_activation": False,
    "service_restart": False,
    "paper_execution": False,
    "broker_execution": False,
    "snaptrade_execution": False,
    "live_execution": False,
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_text(
            encoding="utf-8",
        )
    )

    if not isinstance(value, dict):
        raise TypeError(
            f"Expected JSON object: {path}"
        )

    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(
        value
    ).hexdigest()


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

    if isinstance(value, float) and not math.isfinite(value):
        return None

    return value


def utc_stamp() -> str:
    return datetime.now(
        UTC
    ).strftime(
        "%Y%m%d_%H%M%S"
    )


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
            "Starting package is neither an estimator nor dictionary."
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
        "No estimator was found in the starting package."
    )


def evaluate(
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
) -> dict[str, Any]:
    if len(first) != len(second):
        raise RuntimeError(
            "Prediction arrays have different lengths."
        )

    changed_rows = int(
        np.sum(
            first != second
        )
    )

    return {
        "rows":
            int(
                len(first)
            ),

        "changed_rows":
            changed_rows,

        "change_fraction":
            (
                float(
                    changed_rows
                    / len(first)
                )
                if len(first)
                else 0.0
            ),
    }


def predictor_profile(
    estimator: Any,
) -> dict[str, Any]:
    predictors = getattr(
        estimator,
        "_predictors",
        None,
    )

    if predictors is None:
        return {
            "present": False,
            "count": None,
            "sha256": None,
        }

    count = 0

    for entry in predictors:
        try:
            count += len(entry)
        except Exception:
            count += 1

    serialized = pickle.dumps(
        predictors,
        protocol=pickle.HIGHEST_PROTOCOL,
    )

    return {
        "present": True,
        "count": int(count),
        "sha256": sha256_bytes(serialized),
    }


def qualification_contract() -> dict[str, Any]:
    source_result = load_json(
        SOURCE_RESULT_PATH
    )

    package_present = (
        START_PACKAGE_PATH.is_file()
        and START_PACKAGE_PATH.stat().st_size > 0
    )

    model_present = (
        START_MODEL_PATH.is_file()
        and START_MODEL_PATH.stat().st_size > 0
    )

    dataset_present = (
        DATASET_PATH.is_file()
        and DATASET_PATH.stat().st_size > 0
    )

    package_loaded = False
    feature_count = None
    effective_n_iter = None
    early_stopping = None
    warm_start = None

    if package_present:
        package = joblib.load(
            START_PACKAGE_PATH
        )

        _, estimator = find_estimator(
            package
        )

        package_loaded = True

        features = (
            package.get(
                "features",
                [],
            )
            if isinstance(package, dict)
            else []
        )

        feature_count = len(
            features
        )

        effective_n_iter = int(
            getattr(
                estimator,
                "n_iter_",
                -1,
            )
        )

        early_stopping = getattr(
            estimator,
            "early_stopping",
            None,
        )

        warm_start = getattr(
            estimator,
            "warm_start",
            None,
        )

    checks = {
        "source_result_passed":
            source_result.get("passed") is True,

        "repaired_sensitivity_qualified":
            source_result.get(
                "repaired_sensitivity_qualified"
            ) is True,

        "long_training_ready":
            source_result.get(
                "long_training_ready"
            ) is True,

        "starting_package_present":
            package_present,

        "starting_model_present":
            model_present,

        "dataset_present":
            dataset_present,

        "starting_package_loaded":
            package_loaded,

        "exact_18_features":
            feature_count
            == EXPECTED_FEATURE_COUNT,

        "starting_n_iter_is_115":
            effective_n_iter
            == EXPECTED_START_N_ITER,

        "warm_start_enabled":
            warm_start is True,

        "early_stopping_disabled":
            early_stopping is False,

        "registration_disabled":
            DISABLED_OPERATIONS[
                "candidate_registration"
            ]
            is False,

        "promotion_disabled":
            DISABLED_OPERATIONS[
                "candidate_promotion"
            ]
            is False,

        "parent_replacement_disabled":
            DISABLED_OPERATIONS[
                "parent_model_replacement"
            ]
            is False,

        "runtime_activation_disabled":
            DISABLED_OPERATIONS[
                "runtime_activation"
            ]
            is False,

        "execution_disabled":
            not any(
                DISABLED_OPERATIONS[
                    name
                ]
                for name in (
                    "paper_execution",
                    "broker_execution",
                    "snaptrade_execution",
                    "live_execution",
                )
            ),
    }

    qualified = all(
        checks.values()
    )

    return {
        "classification":
            (
                "generation275_checkpointed_long_runner_qualified"
                if qualified
                else
                "generation275_checkpointed_long_runner_blocked"
            ),

        "qualified":
            qualified,

        "checks":
            checks,

        "starting_checkpoint": {
            "package":
                str(
                    START_PACKAGE_PATH
                ),

            "package_sha256":
                (
                    sha256_file(
                        START_PACKAGE_PATH
                    )
                    if package_present
                    else None
                ),

            "model":
                str(
                    START_MODEL_PATH
                ),

            "model_sha256":
                (
                    sha256_file(
                        START_MODEL_PATH
                    )
                    if model_present
                    else None
                ),

            "effective_n_iter":
                effective_n_iter,

            "feature_count":
                feature_count,
        },

        "dataset": {
            "path":
                str(
                    DATASET_PATH
                ),

            "sha256":
                (
                    sha256_file(
                        DATASET_PATH
                    )
                    if dataset_present
                    else None
                ),
        },

        "authorization": {
            "run_isolated_checkpointed_training":
                qualified,

            "write_isolated_checkpoints":
                qualified,

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
    }


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
            finite_json(
                value
            ),
            indent=2,
            sort_keys=True,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )


def load_dataset(
    features: list[str],
    target: str,
    phase_two_end_fraction: float,
) -> tuple[
    pd.DataFrame,
    pd.Series,
    pd.DataFrame,
    pd.Series,
    pd.Series | None,
]:
    header = [
        str(column)
        for column in pd.read_csv(
            DATASET_PATH,
            nrows=0,
        ).columns
    ]

    missing = sorted(
        set(
            features
            + [
                target,
            ]
        )
        - set(header)
    )

    if missing:
        raise RuntimeError(
            "Dataset is missing required columns:\n  "
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
            + [
                target,
            ]
        )
    )

    frame = pd.read_csv(
        DATASET_PATH,
        usecols=use_columns,
        low_memory=False,
    )

    if timestamp_column:
        frame[timestamp_column] = pd.to_datetime(
            frame[timestamp_column],
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
        frame[feature] = pd.to_numeric(
            frame[feature],
            errors="coerce",
        )

    frame = frame.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    frame = frame.dropna(
        subset=features + [target],
    )

    frame[target] = frame[target].astype(
        str
    )

    frame = frame.reset_index(
        drop=True
    )

    phase_two_end = int(
        len(frame)
        * phase_two_end_fraction
    )

    if not (
        0
        < phase_two_end
        < len(frame)
    ):
        raise RuntimeError(
            "Chronological training/holdout split is invalid."
        )

    training = frame.iloc[
        :phase_two_end
    ].copy()

    holdout = frame.iloc[
        phase_two_end:
    ].copy()

    timestamps = (
        holdout[
            timestamp_column
        ].reset_index(
            drop=True
        )
        if timestamp_column
        else None
    )

    return (
        training[
            features
        ],
        training[
            target
        ],
        holdout[
            features
        ],
        holdout[
            target
        ],
        timestamps,
    )


def run_training(
    output_root: Path,
    checkpoint_step: int,
    checkpoint_count: int,
    phase_two_end_fraction: float,
    minimum_prediction_change: float,
) -> int:
    qualification = qualification_contract()

    write_json(
        output_root
        / "runner_qualification.json",
        qualification,
    )

    if not qualification[
        "qualified"
    ]:
        print(
            json.dumps(
                qualification,
                indent=2,
                sort_keys=True,
            )
        )

        print(
            "BLOCKED: runner qualification failed.",
            file=sys.stderr,
        )

        return 1

    if checkpoint_step < 1:
        raise ValueError(
            "checkpoint_step must be at least 1."
        )

    if checkpoint_count < 1:
        raise ValueError(
            "checkpoint_count must be at least 1."
        )

    output_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    checkpoints_root = (
        output_root
        / "checkpoints"
    )

    checkpoints_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    starting_package = joblib.load(
        START_PACKAGE_PATH
    )

    package_key, starting_estimator = find_estimator(
        starting_package
    )

    if not isinstance(
        starting_package,
        dict,
    ):
        raise RuntimeError(
            "Starting package metadata is unavailable."
        )

    features = [
        str(value)
        for value in starting_package.get(
            "features",
            [],
        )
    ]

    target = str(
        starting_package.get(
            "target",
            "",
        )
    )

    if len(features) != EXPECTED_FEATURE_COUNT:
        raise RuntimeError(
            "Starting package does not expose exactly 18 features."
        )

    if not target:
        raise RuntimeError(
            "Starting package target is missing."
        )

    (
        X_training,
        y_training,
        X_holdout,
        y_holdout,
        timestamps,
    ) = load_dataset(
        features,
        target,
        phase_two_end_fraction,
    )

    current_model = deepcopy(
        starting_estimator
    )

    current_model.set_params(
        warm_start=True,
        early_stopping=False,
    )

    starting_n_iter = int(
        getattr(
            current_model,
            "n_iter_",
            -1,
        )
    )

    if starting_n_iter != EXPECTED_START_N_ITER:
        raise RuntimeError(
            "Starting estimator does not expose n_iter_=115."
        )

    previous_prediction = np.asarray(
        current_model.predict(
            X_holdout
        )
    ).astype(str)

    starting_metrics = evaluate(
        y_holdout,
        previous_prediction,
    )

    starting_profile = predictor_profile(
        current_model
    )

    prediction_frame = pd.DataFrame(
        {
            "actual":
                y_holdout.reset_index(
                    drop=True
                ),

            "checkpoint_000_start":
                previous_prediction,
        }
    )

    if timestamps is not None:
        prediction_frame.insert(
            0,
            "timestamp",
            timestamps,
        )

    records: list[
        dict[str, Any]
    ] = []

    run_started = time.monotonic()

    print()
    print("=" * 110)
    print("NEUROVEST — GENERATION 275 CHECKPOINTED LONG TRAINING")
    print("=" * 110)
    print("Starting n_iter_:", starting_n_iter)
    print("Checkpoint step:", checkpoint_step)
    print("Checkpoint count:", checkpoint_count)
    print("Training rows:", len(X_training))
    print("Holdout rows:", len(X_holdout))
    print("Warm start: True")
    print("Early stopping: False")
    print("Registration: disabled")
    print("Promotion: disabled")
    print("Parent replacement: disabled")
    print("Runtime activation: disabled")
    print()

    for checkpoint_index in range(
        1,
        checkpoint_count + 1,
    ):
        target_n_iter = (
            starting_n_iter
            + checkpoint_index
            * checkpoint_step
        )

        checkpoint_name = (
            "checkpoint_"
            + str(
                checkpoint_index
            ).zfill(3)
            + "_iter_"
            + str(
                target_n_iter
            )
        )

        checkpoint_root = (
            checkpoints_root
            / checkpoint_name
        )

        checkpoint_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        current_model.set_params(
            warm_start=True,
            early_stopping=False,
            max_iter=target_n_iter,
        )

        started = time.monotonic()

        current_model.fit(
            X_training,
            y_training,
        )

        elapsed = (
            time.monotonic()
            - started
        )

        actual_n_iter = int(
            getattr(
                current_model,
                "n_iter_",
                -1,
            )
        )

        current_prediction = np.asarray(
            current_model.predict(
                X_holdout
            )
        ).astype(str)

        current_metrics = evaluate(
            y_holdout,
            current_prediction,
        )

        change = prediction_change(
            previous_prediction,
            current_prediction,
        )

        starting_change = prediction_change(
            prediction_frame[
                "checkpoint_000_start"
            ].to_numpy(
                dtype=str
            ),
            current_prediction,
        )

        profile = predictor_profile(
            current_model
        )

        model_path = (
            checkpoint_root
            / "estimator.joblib"
        )

        package_path = (
            checkpoint_root
            / "candidate_package.joblib"
        )

        predictions_path = (
            checkpoint_root
            / "holdout_predictions.csv"
        )

        checkpoint_result_path = (
            checkpoint_root
            / "result.json"
        )

        joblib.dump(
            current_model,
            model_path,
        )

        package = dict(
            starting_package
        )

        package[
            package_key
        ] = current_model

        package.update(
            {
                "classification":
                    "generation275_checkpointed_long_training_candidate",

                "generation":
                    275,

                "checkpoint":
                    checkpoint_index,

                "checkpoint_name":
                    checkpoint_name,

                "starting_effective_n_iter":
                    starting_n_iter,

                "checkpoint_step":
                    checkpoint_step,

                "target_n_iter":
                    target_n_iter,

                "effective_n_iter":
                    actual_n_iter,

                "warm_start":
                    True,

                "early_stopping":
                    False,

                "metrics":
                    current_metrics,

                "starting_package_sha256":
                    sha256_file(
                        START_PACKAGE_PATH
                    ),

                "registration_authorized":
                    False,

                "promotion_authorized":
                    False,

                "parent_replacement_authorized":
                    False,

                "runtime_activation_authorized":
                    False,
            }
        )

        joblib.dump(
            package,
            package_path,
        )

        checkpoint_prediction_frame = pd.DataFrame(
            {
                "actual":
                    y_holdout.reset_index(
                        drop=True
                    ),

                "previous_checkpoint":
                    previous_prediction,

                "current_checkpoint":
                    current_prediction,
            }
        )

        if timestamps is not None:
            checkpoint_prediction_frame.insert(
                0,
                "timestamp",
                timestamps,
            )

        checkpoint_prediction_frame.to_csv(
            predictions_path,
            index=False,
        )

        exact_target_reached = (
            actual_n_iter
            == target_n_iter
        )

        behavior_changed = (
            change[
                "change_fraction"
            ]
            >= minimum_prediction_change
        )

        checkpoint_passed = bool(
            exact_target_reached
            and profile[
                "present"
            ]
            and current_model.warm_start
            is True
            and current_model.early_stopping
            is False
        )

        record = {
            "classification":
                (
                    "generation275_long_checkpoint_qualified"
                    if checkpoint_passed
                    else
                    "generation275_long_checkpoint_blocked"
                ),

            "passed":
                checkpoint_passed,

            "checkpoint":
                checkpoint_index,

            "checkpoint_name":
                checkpoint_name,

            "starting_n_iter":
                starting_n_iter,

            "target_n_iter":
                target_n_iter,

            "actual_n_iter":
                actual_n_iter,

            "elapsed_seconds":
                elapsed,

            "metrics":
                current_metrics,

            "metric_change_from_start": {
                "accuracy":
                    current_metrics[
                        "accuracy"
                    ]
                    - starting_metrics[
                        "accuracy"
                    ],

                "balanced_accuracy":
                    current_metrics[
                        "balanced_accuracy"
                    ]
                    - starting_metrics[
                        "balanced_accuracy"
                    ],

                "f1_macro":
                    current_metrics[
                        "f1_macro"
                    ]
                    - starting_metrics[
                        "f1_macro"
                    ],
            },

            "prediction_change_from_previous":
                change,

            "prediction_change_from_start":
                starting_change,

            "behavior_changed_from_previous":
                behavior_changed,

            "predictor_profile":
                profile,

            "checks": {
                "exact_target_n_iter_reached":
                    exact_target_reached,

                "warm_start_enabled":
                    current_model.warm_start
                    is True,

                "early_stopping_disabled":
                    current_model.early_stopping
                    is False,

                "predictor_state_present":
                    profile[
                        "present"
                    ],

                "isolated_model_written":
                    model_path.is_file(),

                "isolated_package_written":
                    package_path.is_file(),

                "predictions_written":
                    predictions_path.is_file(),
            },

            "artifacts": {
                "model":
                    str(model_path),

                "model_sha256":
                    sha256_file(
                        model_path
                    ),

                "package":
                    str(package_path),

                "package_sha256":
                    sha256_file(
                        package_path
                    ),

                "predictions":
                    str(predictions_path),

                "predictions_sha256":
                    sha256_file(
                        predictions_path
                    ),
            },

            "authorization": {
                "continue_to_next_checkpoint":
                    checkpoint_passed,

                "register_candidate":
                    False,

                "promote_candidate":
                    False,

                "replace_parent_model":
                    False,

                "runtime_activation":
                    False,
            },
        }

        write_json(
            checkpoint_result_path,
            record,
        )

        records.append(
            record
        )

        prediction_frame[
            checkpoint_name
        ] = current_prediction

        previous_prediction = (
            current_prediction
        )

        print(
            "=" * 110
        )

        print(
            checkpoint_name
        )

        print(
            "=" * 110
        )

        print(
            "Target n_iter_:",
            target_n_iter,
        )

        print(
            "Actual n_iter_:",
            actual_n_iter,
        )

        print(
            "Balanced accuracy:",
            current_metrics[
                "balanced_accuracy"
            ],
        )

        print(
            "F1 macro:",
            current_metrics[
                "f1_macro"
            ],
        )

        print(
            "Prediction change from previous:",
            change[
                "change_fraction"
            ],
        )

        print(
            "Prediction change from start:",
            starting_change[
                "change_fraction"
            ],
        )

        print(
            "Passed:",
            checkpoint_passed,
        )

        print()

        if not checkpoint_passed:
            break

    prediction_frame.to_csv(
        output_root
        / "checkpoint_holdout_predictions.csv",
        index=False,
    )

    all_checkpoints_passed = bool(
        len(records)
        == checkpoint_count
        and all(
            record[
                "passed"
            ]
            for record in records
        )
    )

    n_iters = [
        record[
            "actual_n_iter"
        ]
        for record in records
    ]

    model_hashes = [
        record[
            "artifacts"
        ][
            "model_sha256"
        ]
        for record in records
    ]

    predictor_hashes = [
        record[
            "predictor_profile"
        ][
            "sha256"
        ]
        for record in records
    ]

    distinct_checkpoint_states = bool(
        len(n_iters)
        == len(set(n_iters))
        and len(model_hashes)
        == len(set(model_hashes))
        and len(predictor_hashes)
        == len(set(predictor_hashes))
    )

    final_record = (
        records[-1]
        if records
        else None
    )

    result = {
        "classification":
            (
                "generation275_checkpointed_long_training_complete"
                if all_checkpoints_passed
                and distinct_checkpoint_states
                else
                "generation275_checkpointed_long_training_incomplete"
            ),

        "passed":
            all_checkpoints_passed
            and distinct_checkpoint_states,

        "training_completed":
            all_checkpoints_passed,

        "checkpoint_count_requested":
            checkpoint_count,

        "checkpoint_count_completed":
            len(records),

        "checkpoint_step":
            checkpoint_step,

        "starting_n_iter":
            starting_n_iter,

        "final_n_iter":
            (
                final_record[
                    "actual_n_iter"
                ]
                if final_record
                else None
            ),

        "starting_metrics":
            starting_metrics,

        "final_metrics":
            (
                final_record[
                    "metrics"
                ]
                if final_record
                else None
            ),

        "distinct_checkpoint_states":
            distinct_checkpoint_states,

        "elapsed_seconds":
            time.monotonic()
            - run_started,

        "checkpoints":
            records,

        "authorization": {
            "evaluate_long_training_evidence":
                all_checkpoints_passed
                and distinct_checkpoint_states,

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
            "starting_package_modified":
                False,

            "dataset_modified":
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
        output_root
        / "result.json",
        result,
    )

    manifest = {
        "classification":
            "generation275_checkpointed_long_training_manifest",

        "created_at":
            datetime.now(
                UTC
            ).isoformat(),

        "starting_package": {
            "path":
                str(
                    START_PACKAGE_PATH
                ),

            "sha256":
                sha256_file(
                    START_PACKAGE_PATH
                ),
        },

        "dataset": {
            "path":
                str(
                    DATASET_PATH
                ),

            "sha256":
                sha256_file(
                    DATASET_PATH
                ),
        },

        "starting_model": {
            "path":
                str(
                    START_MODEL_PATH
                ),

            "sha256":
                sha256_file(
                    START_MODEL_PATH
                ),

            "n_iter":
                starting_n_iter,

            "predictor_profile":
                starting_profile,
        },

        "checkpoints":
            records,

        "disabled_operations":
            DISABLED_OPERATIONS,
    }

    write_json(
        output_root
        / "evidence_manifest.json",
        manifest,
    )

    report_lines = [
        "=" * 110,
        "NEUROVEST — GENERATION 275 CHECKPOINTED LONG TRAINING",
        "=" * 110,
        "",
        "Training completion: "
        + (
            "PASS"
            if result[
                "passed"
            ]
            else "BLOCKED"
        ),
        "",
        "Starting n_iter_:              "
        + str(
            starting_n_iter
        ),
        "Checkpoint step:               "
        + str(
            checkpoint_step
        ),
        "Requested checkpoints:         "
        + str(
            checkpoint_count
        ),
        "Completed checkpoints:         "
        + str(
            len(records)
        ),
        "Distinct checkpoint states:    "
        + str(
            distinct_checkpoint_states
        ),
        "",
        "Starting balanced accuracy:    "
        + str(
            starting_metrics[
                "balanced_accuracy"
            ]
        ),
        "Starting F1 macro:             "
        + str(
            starting_metrics[
                "f1_macro"
            ]
        ),
    ]

    for record in records:
        report_lines.extend(
            [
                "",
                record[
                    "checkpoint_name"
                ],

                "  Passed:                       "
                + str(
                    record[
                        "passed"
                    ]
                ),

                "  Effective n_iter_:            "
                + str(
                    record[
                        "actual_n_iter"
                    ]
                ),

                "  Balanced accuracy:            "
                + str(
                    record[
                        "metrics"
                    ][
                        "balanced_accuracy"
                    ]
                ),

                "  F1 macro:                     "
                + str(
                    record[
                        "metrics"
                    ][
                        "f1_macro"
                    ]
                ),

                "  Prediction change from prior: "
                + str(
                    record[
                        "prediction_change_from_previous"
                    ][
                        "change_fraction"
                    ]
                ),

                "  Prediction change from start: "
                + str(
                    record[
                        "prediction_change_from_start"
                    ][
                        "change_fraction"
                    ]
                ),
            ]
        )

    report_lines.extend(
        [
            "",
            "FINAL DISPOSITION",
            "  Training completed:           "
            + str(
                all_checkpoints_passed
            ),

            "  Distinct checkpoint states:   "
            + str(
                distinct_checkpoint_states
            ),

            "  Candidate registration:       False",
            "  Candidate promotion:          False",
            "  Parent replacement:           False",
            "  Runtime activation:           False",
            "  Orders submitted:             0",
            "",
            "Structured result:",
            "  "
            + str(
                output_root
                / "result.json"
            ),
            "",
            "Evidence manifest:",
            "  "
            + str(
                output_root
                / "evidence_manifest.json"
            ),
            "",
            "Terminal remains open.",
        ]
    )

    (
        output_root
        / "report.txt"
    ).write_text(
        "\n".join(
            report_lines
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        (
            output_root
            / "report.txt"
        ).read_text(
            encoding="utf-8",
        )
    )

    return (
        0
        if result[
            "passed"
        ]
        else 1
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generation 275 isolated checkpointed long-training "
            "runner starting from the qualified +15 branch."
        )
    )

    parser.add_argument(
        "--qualify-only",
        action="store_true",
        help=(
            "Validate the runner and source checkpoint without "
            "starting training."
        ),
    )

    parser.add_argument(
        "--qualification-output",
        type=Path,
        default=None,
        help=(
            "Optional qualification JSON path."
        ),
    )

    parser.add_argument(
        "--run-training",
        action="store_true",
        help=(
            "Request isolated checkpointed training."
        ),
    )

    parser.add_argument(
        "--allow-training",
        action="store_true",
        help=(
            "Second explicit authorization required before training."
        ),
    )

    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help=(
            "Required isolated output directory."
        ),
    )

    parser.add_argument(
        "--checkpoint-step",
        type=int,
        default=25,
        help=(
            "Additional effective iterations per checkpoint."
        ),
    )

    parser.add_argument(
        "--checkpoint-count",
        type=int,
        default=8,
        help=(
            "Number of sequential checkpoints."
        ),
    )

    parser.add_argument(
        "--phase-two-end-fraction",
        type=float,
        default=0.80,
        help=(
            "Chronological training boundary; remainder is holdout."
        ),
    )

    parser.add_argument(
        "--minimum-prediction-change",
        type=float,
        default=0.0001,
        help=(
            "Minimum recorded behavior change from the previous "
            "checkpoint. This is reported but does not automatically "
            "discard an otherwise valid checkpoint."
        ),
    )

    return parser


def main() -> int:
    parser = build_parser()

    args = parser.parse_args()

    qualification = qualification_contract()

    qualification_output = (
        args.qualification_output
        or (
            REPO_ROOT
            / "runtime"
            / "training"
            / (
                "generation275_long_runner_qualification_"
                + utc_stamp()
            )
            / "qualification.json"
        )
    )

    write_json(
        qualification_output,
        qualification,
    )

    if args.qualify_only:
        print(
            json.dumps(
                qualification,
                indent=2,
                sort_keys=True,
            )
        )

        return (
            0
            if qualification[
                "qualified"
            ]
            else 1
        )

    if not args.run_training:
        parser.error(
            "Use --qualify-only or provide --run-training "
            "together with --allow-training."
        )

    if not args.allow_training:
        parser.error(
            "--run-training requires --allow-training."
        )

    if args.output_root is None:
        parser.error(
            "--output-root is required for training."
        )

    if not qualification[
        "qualified"
    ]:
        print(
            json.dumps(
                qualification,
                indent=2,
                sort_keys=True,
            )
        )

        print(
            "BLOCKED: long-training runner qualification failed.",
            file=sys.stderr,
        )

        return 1

    return run_training(
        output_root=args.output_root,
        checkpoint_step=args.checkpoint_step,
        checkpoint_count=args.checkpoint_count,
        phase_two_end_fraction=args.phase_two_end_fraction,
        minimum_prediction_change=args.minimum_prediction_change,
    )


if __name__ == "__main__":
    raise SystemExit(
        main()
    )

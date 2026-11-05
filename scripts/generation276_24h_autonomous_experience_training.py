#!/usr/bin/env python3
"""
Generation 276 — 24-hour autonomous experience accumulation.

The runner starts from the qualified Generation 275 checkpoint at
effective n_iter_=165.

It does not repeatedly train on unchanged data. A training cycle occurs
only when a new immutable CSV batch appears in the experience-feed
directory and passes chronological, schema, uniqueness, and safety
qualification.

No candidate registration, database registration, promotion, parent
replacement, runtime activation, service restart, paper execution,
broker execution, SnapTrade execution, or live execution is available.
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
import shutil
import signal
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

GENERATION275_ROOT = (
    REPO_ROOT
    / "runtime"
    / "training"
    / "generation275_checkpointed_long_training_20260806_191828"
)

START_CHECKPOINT_ROOT = (
    GENERATION275_ROOT
    / "checkpoints"
    / "checkpoint_002_iter_165"
)

START_RESULT_PATH = (
    START_CHECKPOINT_ROOT
    / "result.json"
)

START_MODEL_PATH = (
    START_CHECKPOINT_ROOT
    / "estimator.joblib"
)

START_PACKAGE_PATH = (
    START_CHECKPOINT_ROOT
    / "candidate_package.joblib"
)

FROZEN_DATASET_PATH = (
    REPO_ROOT
    / "runtime"
    / "training"
    / "generation274_challenger_confirmation_freeze_20260806_085814"
    / "evidence"
    / "inputs"
    / "training_dataset.csv"
)

DEFAULT_FEED_ROOT = (
    REPO_ROOT
    / "runtime"
    / "training"
    / "generation276_experience_feed"
)

EXPECTED_FEATURE_COUNT = 18
EXPECTED_START_N_ITER = 165
MINIMUM_DURATION_HOURS = 24.0

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

STOP_REQUESTED = False


def handle_stop_signal(
    signum: int,
    frame: Any,
) -> None:
    del signum
    del frame

    global STOP_REQUESTED
    STOP_REQUESTED = True


def load_json(
    path: Path,
) -> dict[str, Any]:
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


def finite_json(
    value: Any,
) -> Any:
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


def sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def sha256_bytes(
    value: bytes,
) -> str:
    return hashlib.sha256(value).hexdigest()


def utc_now() -> datetime:
    return datetime.now(UTC)


def utc_stamp() -> str:
    return utc_now().strftime(
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

    preferred_keys = (
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

    for key in preferred_keys:
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
        "No estimator was found in the package."
    )


def evaluate_predictions(
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
        np.sum(first != second)
    )

    return {
        "rows":
            int(len(first)),

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

    predictor_count = 0

    for entry in predictors:
        try:
            predictor_count += len(entry)
        except Exception:
            predictor_count += 1

    serialized = pickle.dumps(
        predictors,
        protocol=pickle.HIGHEST_PROTOCOL,
    )

    return {
        "present": True,
        "count": int(predictor_count),
        "sha256": sha256_bytes(serialized),
    }


def detect_timestamp_column(
    columns: list[str],
) -> str | None:
    for candidate in (
        "timestamp",
        "date",
        "datetime",
        "market_date",
        "bar_time",
        "event_time",
    ):
        if candidate in columns:
            return candidate

    return None


def detect_symbol_column(
    columns: list[str],
) -> str | None:
    for candidate in (
        "provider_symbol",
        "symbol",
        "ticker",
        "asset",
        "instrument",
    ):
        if candidate in columns:
            return candidate

    return None


def load_frozen_dataset(
    features: list[str],
    target: str,
    phase_two_end_fraction: float,
) -> dict[str, Any]:
    header = [
        str(column)
        for column in pd.read_csv(
            FROZEN_DATASET_PATH,
            nrows=0,
        ).columns
    ]

    missing = sorted(
        set(features + [target])
        - set(header)
    )

    if missing:
        raise RuntimeError(
            "Frozen dataset is missing required columns:\n  "
            + "\n  ".join(missing)
        )

    timestamp_column = detect_timestamp_column(
        header
    )

    symbol_column = detect_symbol_column(
        header
    )

    optional_columns = [
        column
        for column in (
            timestamp_column,
            symbol_column,
        )
        if column is not None
    ]

    use_columns = list(
        dict.fromkeys(
            optional_columns
            + features
            + [target]
        )
    )

    frame = pd.read_csv(
        FROZEN_DATASET_PATH,
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
            subset=[timestamp_column]
        )

        frame = frame.sort_values(
            timestamp_column,
            kind="stable",
        )

    if symbol_column:
        frame[symbol_column] = (
            frame[symbol_column]
            .astype(str)
            .str.upper()
            .str.strip()
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

    frame[target] = frame[target].astype(str)

    frame = frame.reset_index(drop=True)

    split_index = int(
        len(frame)
        * phase_two_end_fraction
    )

    if not (
        0
        < split_index
        < len(frame)
    ):
        raise RuntimeError(
            "Frozen chronological split is invalid."
        )

    training = frame.iloc[
        :split_index
    ].copy()

    holdout = frame.iloc[
        split_index:
    ].copy()

    latest_training_timestamp = None

    if timestamp_column:
        latest_training_timestamp = (
            training[timestamp_column]
            .max()
        )

    return {
        "training_frame":
            training,

        "holdout_frame":
            holdout,

        "X_training":
            training[features],

        "y_training":
            training[target],

        "X_holdout":
            holdout[features],

        "y_holdout":
            holdout[target],

        "timestamp_column":
            timestamp_column,

        "symbol_column":
            symbol_column,

        "latest_training_timestamp":
            latest_training_timestamp,

        "row_count":
            int(len(frame)),

        "training_rows":
            int(len(training)),

        "holdout_rows":
            int(len(holdout)),
    }


def qualification_contract() -> dict[str, Any]:
    source_result = load_json(
        START_RESULT_PATH
    )

    package_present = bool(
        START_PACKAGE_PATH.is_file()
        and START_PACKAGE_PATH.stat().st_size > 0
    )

    model_present = bool(
        START_MODEL_PATH.is_file()
        and START_MODEL_PATH.stat().st_size > 0
    )

    dataset_present = bool(
        FROZEN_DATASET_PATH.is_file()
        and FROZEN_DATASET_PATH.stat().st_size > 0
    )

    package_loaded = False
    feature_count = None
    effective_n_iter = None
    warm_start = None
    early_stopping = None
    target_present = False

    if package_present:
        package = joblib.load(
            START_PACKAGE_PATH
        )

        _, estimator = find_estimator(
            package
        )

        package_loaded = True

        features = (
            package.get("features", [])
            if isinstance(package, dict)
            else []
        )

        target = (
            str(package.get("target", ""))
            if isinstance(package, dict)
            else ""
        )

        feature_count = len(features)
        target_present = bool(target)

        effective_n_iter = int(
            getattr(
                estimator,
                "n_iter_",
                -1,
            )
        )

        warm_start = getattr(
            estimator,
            "warm_start",
            None,
        )

        early_stopping = getattr(
            estimator,
            "early_stopping",
            None,
        )

    checks = {
        "generation275_checkpoint_passed":
            source_result.get("passed") is True,

        "starting_checkpoint_is_165":
            (
                source_result.get("actual_n_iter")
                == EXPECTED_START_N_ITER
            ),

        "starting_package_present":
            package_present,

        "starting_model_present":
            model_present,

        "frozen_dataset_present":
            dataset_present,

        "starting_package_loaded":
            package_loaded,

        "exact_18_features":
            feature_count
            == EXPECTED_FEATURE_COUNT,

        "target_present":
            target_present,

        "effective_n_iter_is_165":
            effective_n_iter
            == EXPECTED_START_N_ITER,

        "warm_start_enabled":
            warm_start is True,

        "early_stopping_disabled":
            early_stopping is False,

        "candidate_registration_disabled":
            DISABLED_OPERATIONS[
                "candidate_registration"
            ]
            is False,

        "candidate_promotion_disabled":
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

        "all_execution_disabled":
            not any(
                DISABLED_OPERATIONS[name]
                for name in (
                    "paper_execution",
                    "broker_execution",
                    "snaptrade_execution",
                    "live_execution",
                )
            ),
    }

    qualified = all(checks.values())

    return {
        "classification":
            (
                "generation276_24h_runner_qualified"
                if qualified
                else
                "generation276_24h_runner_blocked"
            ),

        "qualified":
            qualified,

        "checks":
            checks,

        "starting_checkpoint": {
            "result":
                str(START_RESULT_PATH),

            "package":
                str(START_PACKAGE_PATH),

            "package_sha256":
                (
                    sha256_file(START_PACKAGE_PATH)
                    if package_present
                    else None
                ),

            "model":
                str(START_MODEL_PATH),

            "model_sha256":
                (
                    sha256_file(START_MODEL_PATH)
                    if model_present
                    else None
                ),

            "effective_n_iter":
                effective_n_iter,

            "feature_count":
                feature_count,
        },

        "frozen_dataset": {
            "path":
                str(FROZEN_DATASET_PATH),

            "sha256":
                (
                    sha256_file(FROZEN_DATASET_PATH)
                    if dataset_present
                    else None
                ),
        },

        "minimum_duration_hours":
            MINIMUM_DURATION_HOURS,

        "experience_feed":
            str(DEFAULT_FEED_ROOT),

        "authorization": {
            "run_24h_autonomous_cycle":
                qualified,

            "consume_qualified_experience_batches":
                qualified,

            "write_isolated_checkpoints":
                qualified,

            "resume_isolated_run":
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


def discover_incoming_batches(
    incoming_root: Path,
    consumed_hashes: set[str],
) -> list[Path]:
    incoming_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    candidates = []

    for path in incoming_root.glob("*.csv"):
        if not path.is_file():
            continue

        if path.stat().st_size <= 0:
            continue

        file_hash = sha256_file(path)

        if file_hash in consumed_hashes:
            continue

        candidates.append(path)

    return sorted(
        candidates,
        key=lambda path: (
            path.stat().st_mtime_ns,
            path.name,
        ),
    )


def qualify_experience_batch(
    path: Path,
    features: list[str],
    target: str,
    timestamp_column: str,
    symbol_column: str | None,
    latest_training_timestamp: pd.Timestamp | None,
    seen_keys: set[tuple[str, str]],
) -> tuple[
    bool,
    pd.DataFrame | None,
    dict[str, Any],
]:
    record: dict[str, Any] = {
        "path":
            str(path),

        "sha256":
            sha256_file(path),

        "bytes":
            int(path.stat().st_size),

        "qualified":
            False,

        "checks":
            {},

        "reason":
            None,
    }

    try:
        header = [
            str(column)
            for column in pd.read_csv(
                path,
                nrows=0,
            ).columns
        ]

        required_columns = set(
            features
            + [
                target,
                timestamp_column,
            ]
        )

        if symbol_column:
            required_columns.add(
                symbol_column
            )

        missing_columns = sorted(
            required_columns
            - set(header)
        )

        record["checks"][
            "required_columns_present"
        ] = not missing_columns

        if missing_columns:
            raise RuntimeError(
                "Missing required columns: "
                + ", ".join(missing_columns)
            )

        use_columns = list(
            dict.fromkeys(
                [
                    timestamp_column,
                ]
                + (
                    [symbol_column]
                    if symbol_column
                    else []
                )
                + features
                + [target]
            )
        )

        frame = pd.read_csv(
            path,
            usecols=use_columns,
            low_memory=False,
        )

        frame[timestamp_column] = pd.to_datetime(
            frame[timestamp_column],
            errors="coerce",
            utc=True,
        )

        frame = frame.dropna(
            subset=[timestamp_column]
        )

        if symbol_column:
            frame[symbol_column] = (
                frame[symbol_column]
                .astype(str)
                .str.upper()
                .str.strip()
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

        frame[target] = frame[target].astype(str)

        frame = frame.sort_values(
            timestamp_column,
            kind="stable",
        )

        frame = frame.reset_index(drop=True)

        record["checks"][
            "rows_present"
        ] = not frame.empty

        if frame.empty:
            raise RuntimeError(
                "No usable rows remain after normalization."
            )

        batch_first_timestamp = (
            frame[timestamp_column].min()
        )

        batch_last_timestamp = (
            frame[timestamp_column].max()
        )

        chronologically_new = bool(
            latest_training_timestamp is None
            or batch_first_timestamp
            > latest_training_timestamp
        )

        record["checks"][
            "chronologically_new"
        ] = chronologically_new

        if not chronologically_new:
            raise RuntimeError(
                "Batch does not begin after the latest "
                "accepted training timestamp."
            )

        duplicate_rows = int(
            frame.duplicated(
                subset=(
                    [
                        timestamp_column,
                        symbol_column,
                    ]
                    if symbol_column
                    else [
                        timestamp_column,
                    ]
                )
            ).sum()
        )

        record["checks"][
            "zero_internal_duplicate_keys"
        ] = duplicate_rows == 0

        if duplicate_rows:
            raise RuntimeError(
                "Batch contains duplicate chronological keys."
            )

        new_keys: set[tuple[str, str]] = set()

        for _, row in frame.iterrows():
            timestamp_key = (
                row[timestamp_column]
                .isoformat()
            )

            symbol_key = (
                str(row[symbol_column])
                if symbol_column
                else ""
            )

            key = (
                timestamp_key,
                symbol_key,
            )

            new_keys.add(key)

        overlap_count = len(
            new_keys
            & seen_keys
        )

        record["checks"][
            "zero_previously_seen_keys"
        ] = overlap_count == 0

        if overlap_count:
            raise RuntimeError(
                "Batch overlaps previously accepted experience."
            )

        all_prices_finite = bool(
            np.isfinite(
                frame[features]
                .to_numpy(
                    dtype=float
                )
            ).all()
        )

        record["checks"][
            "all_features_finite"
        ] = all_prices_finite

        if not all_prices_finite:
            raise RuntimeError(
                "Batch contains non-finite feature values."
            )

        record.update(
            {
                "qualified":
                    True,

                "rows":
                    int(len(frame)),

                "first_timestamp":
                    batch_first_timestamp.isoformat(),

                "last_timestamp":
                    batch_last_timestamp.isoformat(),

                "key_count":
                    len(new_keys),

                "reason":
                    None,
            }
        )

        return (
            True,
            frame,
            record,
        )

    except Exception as error:
        record[
            "qualified"
        ] = False

        record[
            "reason"
        ] = repr(error)

        return (
            False,
            None,
            record,
        )


def checkpoint_paths(
    run_root: Path,
    cycle_number: int,
    effective_n_iter: int,
) -> dict[str, Path]:
    name = (
        "cycle_"
        + str(cycle_number).zfill(4)
        + "_iter_"
        + str(effective_n_iter)
    )

    root = (
        run_root
        / "checkpoints"
        / name
    )

    return {
        "name":
            Path(name),

        "root":
            root,

        "model":
            root
            / "estimator.joblib",

        "package":
            root
            / "candidate_package.joblib",

        "predictions":
            root
            / "holdout_predictions.csv",

        "result":
            root
            / "result.json",
    }


def load_resume_state(
    output_root: Path,
) -> dict[str, Any] | None:
    state_path = (
        output_root
        / "resume_state.json"
    )

    if not state_path.is_file():
        return None

    state = load_json(state_path)

    if state.get(
        "classification"
    ) != "generation276_resume_state":
        raise RuntimeError(
            "Existing resume state has an unexpected classification."
        )

    return state


def run_autonomous_cycle(
    output_root: Path,
    feed_root: Path,
    duration_hours: float,
    cycle_minutes: float,
    iterations_per_batch: int,
    phase_two_end_fraction: float,
    balanced_accuracy_tolerance: float,
    f1_tolerance: float,
) -> int:
    if duration_hours < MINIMUM_DURATION_HOURS:
        raise ValueError(
            "Generation 276 requires at least 24 hours."
        )

    if cycle_minutes <= 0:
        raise ValueError(
            "cycle_minutes must be greater than zero."
        )

    if iterations_per_batch < 1:
        raise ValueError(
            "iterations_per_batch must be at least one."
        )

    qualification = qualification_contract()

    write_json(
        output_root
        / "runner_qualification.json",
        qualification,
    )

    if not qualification["qualified"]:
        print(
            json.dumps(
                qualification,
                indent=2,
                sort_keys=True,
            )
        )

        print(
            "BLOCKED: Generation 276 runner qualification failed.",
            file=sys.stderr,
        )

        return 1

    output_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    checkpoints_root = (
        output_root
        / "checkpoints"
    )

    heartbeats_root = (
        output_root
        / "heartbeats"
    )

    rejected_root = (
        output_root
        / "rejected_cycles"
    )

    checkpoints_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    heartbeats_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    rejected_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    incoming_root = (
        feed_root
        / "incoming"
    )

    accepted_feed_root = (
        feed_root
        / "accepted"
    )

    rejected_feed_root = (
        feed_root
        / "rejected"
    )

    incoming_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    accepted_feed_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    rejected_feed_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    starting_package = joblib.load(
        START_PACKAGE_PATH
    )

    package_key, starting_estimator = find_estimator(
        starting_package
    )

    if not isinstance(starting_package, dict):
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

    frozen = load_frozen_dataset(
        features=features,
        target=target,
        phase_two_end_fraction=phase_two_end_fraction,
    )

    timestamp_column = frozen[
        "timestamp_column"
    ]

    symbol_column = frozen[
        "symbol_column"
    ]

    if timestamp_column is None:
        raise RuntimeError(
            "Generation 276 requires a timestamp column."
        )

    base_training_frame = frozen[
        "training_frame"
    ].copy()

    X_holdout = frozen[
        "X_holdout"
    ]

    y_holdout = frozen[
        "y_holdout"
    ]

    current_model = deepcopy(
        starting_estimator
    )

    current_model.set_params(
        warm_start=True,
        early_stopping=False,
    )

    current_package = dict(
        starting_package
    )

    current_n_iter = int(
        getattr(
            current_model,
            "n_iter_",
            -1,
        )
    )

    if current_n_iter != EXPECTED_START_N_ITER:
        raise RuntimeError(
            "Starting model does not expose n_iter_=165."
        )

    start_prediction = np.asarray(
        current_model.predict(
            X_holdout
        )
    ).astype(str)

    start_metrics = evaluate_predictions(
        y_holdout,
        start_prediction,
    )

    best_model = deepcopy(
        current_model
    )

    best_package = dict(
        current_package
    )

    best_prediction = (
        start_prediction.copy()
    )

    best_metrics = dict(
        start_metrics
    )

    best_n_iter = current_n_iter
    best_cycle = 0

    accumulated_training = (
        base_training_frame.copy()
    )

    latest_training_timestamp = frozen[
        "latest_training_timestamp"
    ]

    seen_keys: set[
        tuple[str, str]
    ] = set()

    for _, row in accumulated_training.iterrows():
        timestamp_key = (
            row[timestamp_column]
            .isoformat()
        )

        symbol_key = (
            str(row[symbol_column])
            if symbol_column
            else ""
        )

        seen_keys.add(
            (
                timestamp_key,
                symbol_key,
            )
        )

    consumed_hashes: set[str] = set()

    accepted_batches: list[
        dict[str, Any]
    ] = []

    rejected_batches: list[
        dict[str, Any]
    ] = []

    cycle_records: list[
        dict[str, Any]
    ] = []

    resume_count = 0
    resumed = False

    resume_state = load_resume_state(
        output_root
    )

    if resume_state is not None:
        resume_model_path = Path(
            str(
                resume_state.get(
                    "current_model_path",
                    "",
                )
            )
        )

        resume_package_path = Path(
            str(
                resume_state.get(
                    "current_package_path",
                    "",
                )
            )
        )

        accumulated_path = Path(
            str(
                resume_state.get(
                    "accumulated_training_path",
                    "",
                )
            )
        )

        if not resume_model_path.is_file():
            raise RuntimeError(
                "Resume model artifact is missing."
            )

        if not resume_package_path.is_file():
            raise RuntimeError(
                "Resume package artifact is missing."
            )

        if not accumulated_path.is_file():
            raise RuntimeError(
                "Resume accumulated-training artifact is missing."
            )

        current_model = joblib.load(
            resume_model_path
        )

        current_package = joblib.load(
            resume_package_path
        )

        accumulated_training = pd.read_parquet(
            accumulated_path
        )

        latest_raw = resume_state.get(
            "latest_training_timestamp"
        )

        latest_training_timestamp = (
            pd.Timestamp(latest_raw)
            if latest_raw
            else latest_training_timestamp
        )

        consumed_hashes = set(
            str(value)
            for value in resume_state.get(
                "consumed_hashes",
                []
            )
        )

        accepted_batches = list(
            resume_state.get(
                "accepted_batches",
                []
            )
        )

        rejected_batches = list(
            resume_state.get(
                "rejected_batches",
                []
            )
        )

        cycle_records = list(
            resume_state.get(
                "cycle_records",
                []
            )
        )

        best_model_path = Path(
            str(
                resume_state.get(
                    "best_model_path",
                    "",
                )
            )
        )

        best_package_path = Path(
            str(
                resume_state.get(
                    "best_package_path",
                    "",
                )
            )
        )

        if best_model_path.is_file():
            best_model = joblib.load(
                best_model_path
            )

        if best_package_path.is_file():
            best_package = joblib.load(
                best_package_path
            )

        best_metrics = dict(
            resume_state.get(
                "best_metrics",
                best_metrics,
            )
        )

        best_n_iter = int(
            resume_state.get(
                "best_n_iter",
                best_n_iter,
            )
        )

        best_cycle = int(
            resume_state.get(
                "best_cycle",
                best_cycle,
            )
        )

        current_n_iter = int(
            getattr(
                current_model,
                "n_iter_",
                -1,
            )
        )

        resume_count = int(
            resume_state.get(
                "resume_count",
                0,
            )
        ) + 1

        resumed = True

    seen_keys.clear()

    for _, row in accumulated_training.iterrows():
        timestamp_key = (
            pd.Timestamp(
                row[timestamp_column]
            ).isoformat()
        )

        symbol_key = (
            str(row[symbol_column])
            if symbol_column
            else ""
        )

        seen_keys.add(
            (
                timestamp_key,
                symbol_key,
            )
        )

    run_started_monotonic = time.monotonic()
    run_started_at = utc_now()

    requested_seconds = (
        duration_hours
        * 60.0
        * 60.0
    )

    cycle_seconds = (
        cycle_minutes
        * 60.0
    )

    end_monotonic = (
        run_started_monotonic
        + requested_seconds
    )

    initial_cycle_number = len(
        cycle_records
    )

    print()
    print("=" * 110)
    print("NEUROVEST — GENERATION 276 24-HOUR AUTONOMOUS TRAINING")
    print("=" * 110)
    print("Duration hours:", duration_hours)
    print("Cycle minutes:", cycle_minutes)
    print("Iterations per accepted batch:", iterations_per_batch)
    print("Starting n_iter_:", current_n_iter)
    print("Frozen holdout rows:", len(X_holdout))
    print("Experience feed:", incoming_root)
    print("Resumed:", resumed)
    print("Resume count:", resume_count)
    print("Registration: disabled")
    print("Promotion: disabled")
    print("Parent replacement: disabled")
    print("Runtime activation: disabled")
    print()

    cycle_number = initial_cycle_number

    while time.monotonic() < end_monotonic:
        cycle_number += 1

        cycle_started_at = utc_now()
        cycle_started_monotonic = time.monotonic()

        incoming_batches = discover_incoming_batches(
            incoming_root=incoming_root,
            consumed_hashes=consumed_hashes,
        )

        cycle_record: dict[str, Any] = {
            "cycle":
                cycle_number,

            "started_at":
                cycle_started_at.isoformat(),

            "incoming_batch_count":
                len(incoming_batches),

            "accepted_batch_count":
                0,

            "rejected_batch_count":
                0,

            "training_performed":
                False,

            "checkpoint_accepted":
                False,

            "rollback_performed":
                False,

            "heartbeat_only":
                False,

            "batches":
                [],
        }

        cycle_new_frames: list[
            pd.DataFrame
        ] = []

        for batch_path in incoming_batches:
            file_hash = sha256_file(
                batch_path
            )

            qualified, frame, batch_record = (
                qualify_experience_batch(
                    path=batch_path,
                    features=features,
                    target=target,
                    timestamp_column=timestamp_column,
                    symbol_column=symbol_column,
                    latest_training_timestamp=latest_training_timestamp,
                    seen_keys=seen_keys,
                )
            )

            consumed_hashes.add(
                file_hash
            )

            cycle_record[
                "batches"
            ].append(
                batch_record
            )

            if qualified and frame is not None:
                accepted_destination = (
                    accepted_feed_root
                    / (
                        file_hash
                        + "_"
                        + batch_path.name
                    )
                )

                shutil.copy2(
                    batch_path,
                    accepted_destination,
                )

                accepted_record = {
                    **batch_record,

                    "accepted_copy":
                        str(
                            accepted_destination
                        ),

                    "accepted_copy_sha256":
                        sha256_file(
                            accepted_destination
                        ),
                }

                accepted_batches.append(
                    accepted_record
                )

                cycle_record[
                    "accepted_batch_count"
                ] += 1

                cycle_new_frames.append(
                    frame
                )

                latest_training_timestamp = (
                    frame[timestamp_column]
                    .max()
                )

                for _, row in frame.iterrows():
                    timestamp_key = (
                        row[timestamp_column]
                        .isoformat()
                    )

                    symbol_key = (
                        str(row[symbol_column])
                        if symbol_column
                        else ""
                    )

                    seen_keys.add(
                        (
                            timestamp_key,
                            symbol_key,
                        )
                    )

            else:
                rejected_destination = (
                    rejected_feed_root
                    / (
                        file_hash
                        + "_"
                        + batch_path.name
                    )
                )

                shutil.copy2(
                    batch_path,
                    rejected_destination,
                )

                rejected_record = {
                    **batch_record,

                    "rejected_copy":
                        str(
                            rejected_destination
                        ),

                    "rejected_copy_sha256":
                        sha256_file(
                            rejected_destination
                        ),
                }

                rejected_batches.append(
                    rejected_record
                )

                cycle_record[
                    "rejected_batch_count"
                ] += 1

        if cycle_new_frames:
            accumulated_training = pd.concat(
                [
                    accumulated_training,
                    *cycle_new_frames,
                ],
                ignore_index=True,
                sort=False,
            )

            accumulated_training = (
                accumulated_training
                .sort_values(
                    timestamp_column,
                    kind="stable",
                )
                .drop_duplicates(
                    subset=(
                        [
                            timestamp_column,
                            symbol_column,
                        ]
                        if symbol_column
                        else [
                            timestamp_column,
                        ]
                    ),
                    keep="last",
                )
                .reset_index(drop=True)
            )

            X_training = accumulated_training[
                features
            ]

            y_training = accumulated_training[
                target
            ].astype(str)

            prior_model = deepcopy(
                current_model
            )

            prior_package = dict(
                current_package
            )

            prior_prediction = np.asarray(
                prior_model.predict(
                    X_holdout
                )
            ).astype(str)

            prior_metrics = evaluate_predictions(
                y_holdout,
                prior_prediction,
            )

            target_n_iter = (
                int(
                    getattr(
                        current_model,
                        "n_iter_",
                        current_n_iter,
                    )
                )
                + iterations_per_batch
            )

            current_model.set_params(
                warm_start=True,
                early_stopping=False,
                max_iter=target_n_iter,
            )

            training_started = time.monotonic()

            current_model.fit(
                X_training,
                y_training,
            )

            training_elapsed = (
                time.monotonic()
                - training_started
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

            current_metrics = evaluate_predictions(
                y_holdout,
                current_prediction,
            )

            change_from_prior = prediction_change(
                prior_prediction,
                current_prediction,
            )

            change_from_start = prediction_change(
                start_prediction,
                current_prediction,
            )

            balanced_accuracy_floor = (
                best_metrics[
                    "balanced_accuracy"
                ]
                - balanced_accuracy_tolerance
            )

            f1_floor = (
                best_metrics[
                    "f1_macro"
                ]
                - f1_tolerance
            )

            degradation_blocked = bool(
                current_metrics[
                    "balanced_accuracy"
                ]
                < balanced_accuracy_floor
                or current_metrics[
                    "f1_macro"
                ]
                < f1_floor
            )

            improves_best = bool(
                current_metrics[
                    "balanced_accuracy"
                ]
                > best_metrics[
                    "balanced_accuracy"
                ]
                or (
                    math.isclose(
                        current_metrics[
                            "balanced_accuracy"
                        ],
                        best_metrics[
                            "balanced_accuracy"
                        ],
                        rel_tol=0.0,
                        abs_tol=1e-15,
                    )
                    and current_metrics[
                        "f1_macro"
                    ]
                    > best_metrics[
                        "f1_macro"
                    ]
                )
            )

            checkpoint = checkpoint_paths(
                run_root=output_root,
                cycle_number=cycle_number,
                effective_n_iter=actual_n_iter,
            )

            checkpoint_root = checkpoint[
                "root"
            ]

            checkpoint_root.mkdir(
                parents=True,
                exist_ok=True,
            )

            cycle_record.update(
                {
                    "training_performed":
                        True,

                    "training_rows":
                        int(
                            len(
                                accumulated_training
                            )
                        ),

                    "new_rows":
                        int(
                            sum(
                                len(frame)
                                for frame
                                in cycle_new_frames
                            )
                        ),

                    "target_n_iter":
                        target_n_iter,

                    "actual_n_iter":
                        actual_n_iter,

                    "training_elapsed_seconds":
                        training_elapsed,

                    "prior_metrics":
                        prior_metrics,

                    "candidate_metrics":
                        current_metrics,

                    "best_metrics_before_cycle":
                        best_metrics,

                    "prediction_change_from_prior":
                        change_from_prior,

                    "prediction_change_from_generation275_start":
                        change_from_start,

                    "balanced_accuracy_floor":
                        balanced_accuracy_floor,

                    "f1_floor":
                        f1_floor,

                    "degradation_blocked":
                        degradation_blocked,

                    "improves_best":
                        improves_best,

                    "predictor_profile":
                        predictor_profile(
                            current_model
                        ),
                }
            )

            if degradation_blocked:
                rejected_cycle_root = (
                    rejected_root
                    / (
                        "cycle_"
                        + str(
                            cycle_number
                        ).zfill(4)
                    )
                )

                rejected_cycle_root.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                rejected_model_path = (
                    rejected_cycle_root
                    / "rejected_estimator.joblib"
                )

                rejected_package_path = (
                    rejected_cycle_root
                    / "rejected_candidate_package.joblib"
                )

                joblib.dump(
                    current_model,
                    rejected_model_path,
                )

                rejected_package = dict(
                    current_package
                )

                rejected_package[
                    package_key
                ] = current_model

                joblib.dump(
                    rejected_package,
                    rejected_package_path,
                )

                cycle_record[
                    "rejected_model"
                ] = str(
                    rejected_model_path
                )

                cycle_record[
                    "rejected_model_sha256"
                ] = sha256_file(
                    rejected_model_path
                )

                cycle_record[
                    "rejected_package"
                ] = str(
                    rejected_package_path
                )

                cycle_record[
                    "rejected_package_sha256"
                ] = sha256_file(
                    rejected_package_path
                )

                current_model = deepcopy(
                    best_model
                )

                current_package = dict(
                    best_package
                )

                current_n_iter = int(
                    getattr(
                        current_model,
                        "n_iter_",
                        best_n_iter,
                    )
                )

                cycle_record[
                    "rollback_performed"
                ] = True

                cycle_record[
                    "checkpoint_accepted"
                ] = False

                cycle_record[
                    "disposition"
                ] = "rejected_and_rolled_back"

            else:
                current_n_iter = actual_n_iter

                current_package = dict(
                    starting_package
                )

                current_package[
                    package_key
                ] = current_model

                current_package.update(
                    {
                        "classification":
                            "generation276_autonomous_experience_checkpoint",

                        "generation":
                            276,

                        "cycle":
                            cycle_number,

                        "effective_n_iter":
                            actual_n_iter,

                        "metrics":
                            current_metrics,

                        "best_checkpoint":
                            improves_best,

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
                    current_model,
                    checkpoint[
                        "model"
                    ],
                )

                joblib.dump(
                    current_package,
                    checkpoint[
                        "package"
                    ],
                )

                checkpoint_predictions = pd.DataFrame(
                    {
                        "actual":
                            y_holdout.reset_index(
                                drop=True
                            ),

                        "previous_checkpoint":
                            prior_prediction,

                        "current_checkpoint":
                            current_prediction,
                    }
                )

                holdout_frame = frozen[
                    "holdout_frame"
                ]

                checkpoint_predictions.insert(
                    0,
                    timestamp_column,
                    holdout_frame[
                        timestamp_column
                    ].reset_index(
                        drop=True
                    ),
                )

                if symbol_column:
                    checkpoint_predictions.insert(
                        1,
                        symbol_column,
                        holdout_frame[
                            symbol_column
                        ].reset_index(
                            drop=True
                        ),
                    )

                checkpoint_predictions.to_csv(
                    checkpoint[
                        "predictions"
                    ],
                    index=False,
                )

                cycle_record[
                    "checkpoint_accepted"
                ] = True

                cycle_record[
                    "disposition"
                ] = (
                    "accepted_as_new_best"
                    if improves_best
                    else
                    "accepted_non_best"
                )

                cycle_record[
                    "checkpoint"
                ] = {
                    "root":
                        str(
                            checkpoint[
                                "root"
                            ]
                        ),

                    "model":
                        str(
                            checkpoint[
                                "model"
                            ]
                        ),

                    "model_sha256":
                        sha256_file(
                            checkpoint[
                                "model"
                            ]
                        ),

                    "package":
                        str(
                            checkpoint[
                                "package"
                            ]
                        ),

                    "package_sha256":
                        sha256_file(
                            checkpoint[
                                "package"
                            ]
                        ),

                    "predictions":
                        str(
                            checkpoint[
                                "predictions"
                            ]
                        ),

                    "predictions_sha256":
                        sha256_file(
                            checkpoint[
                                "predictions"
                            ]
                        ),
                }

                if improves_best:
                    best_model = deepcopy(
                        current_model
                    )

                    best_package = dict(
                        current_package
                    )

                    best_prediction = (
                        current_prediction.copy()
                    )

                    best_metrics = dict(
                        current_metrics
                    )

                    best_n_iter = actual_n_iter
                    best_cycle = cycle_number

            write_json(
                checkpoint[
                    "result"
                ],
                cycle_record,
            )

        else:
            cycle_record[
                "heartbeat_only"
            ] = True

            cycle_record[
                "disposition"
            ] = "no_new_qualified_experience"

            cycle_record[
                "current_n_iter"
            ] = int(
                getattr(
                    current_model,
                    "n_iter_",
                    current_n_iter,
                )
            )

            cycle_record[
                "best_cycle"
            ] = best_cycle

            cycle_record[
                "best_n_iter"
            ] = best_n_iter

            cycle_record[
                "best_metrics"
            ] = best_metrics

        cycle_record[
            "completed_at"
        ] = utc_now().isoformat()

        cycle_record[
            "elapsed_seconds"
        ] = (
            time.monotonic()
            - cycle_started_monotonic
        )

        cycle_records.append(
            cycle_record
        )

        heartbeat_path = (
            heartbeats_root
            / (
                "cycle_"
                + str(
                    cycle_number
                ).zfill(4)
                + ".json"
            )
        )

        write_json(
            heartbeat_path,
            cycle_record,
        )

        resume_root = (
            output_root
            / "resume"
        )

        resume_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        current_model_path = (
            resume_root
            / "current_estimator.joblib"
        )

        current_package_path = (
            resume_root
            / "current_candidate_package.joblib"
        )

        best_model_path = (
            resume_root
            / "best_estimator.joblib"
        )

        best_package_path = (
            resume_root
            / "best_candidate_package.joblib"
        )

        accumulated_training_path = (
            resume_root
            / "accumulated_training.parquet"
        )

        joblib.dump(
            current_model,
            current_model_path,
        )

        joblib.dump(
            current_package,
            current_package_path,
        )

        joblib.dump(
            best_model,
            best_model_path,
        )

        joblib.dump(
            best_package,
            best_package_path,
        )

        accumulated_training.to_parquet(
            accumulated_training_path,
            index=False,
        )

        resume_state_document = {
            "classification":
                "generation276_resume_state",

            "updated_at":
                utc_now().isoformat(),

            "run_started_at":
                run_started_at.isoformat(),

            "resume_count":
                resume_count,

            "cycle_count":
                len(cycle_records),

            "current_model_path":
                str(current_model_path),

            "current_model_sha256":
                sha256_file(
                    current_model_path
                ),

            "current_package_path":
                str(
                    current_package_path
                ),

            "current_package_sha256":
                sha256_file(
                    current_package_path
                ),

            "best_model_path":
                str(best_model_path),

            "best_model_sha256":
                sha256_file(
                    best_model_path
                ),

            "best_package_path":
                str(best_package_path),

            "best_package_sha256":
                sha256_file(
                    best_package_path
                ),

            "accumulated_training_path":
                str(
                    accumulated_training_path
                ),

            "accumulated_training_sha256":
                sha256_file(
                    accumulated_training_path
                ),

            "latest_training_timestamp":
                (
                    latest_training_timestamp.isoformat()
                    if latest_training_timestamp
                    is not None
                    else None
                ),

            "current_n_iter":
                int(
                    getattr(
                        current_model,
                        "n_iter_",
                        current_n_iter,
                    )
                ),

            "best_cycle":
                best_cycle,

            "best_n_iter":
                best_n_iter,

            "best_metrics":
                best_metrics,

            "consumed_hashes":
                sorted(
                    consumed_hashes
                ),

            "accepted_batches":
                accepted_batches,

            "rejected_batches":
                rejected_batches,

            "cycle_records":
                cycle_records,

            "safe_to_resume":
                True,

            "registration_performed":
                False,

            "promotion_performed":
                False,

            "parent_replaced":
                False,

            "runtime_activated":
                False,

            "orders_submitted":
                0,
        }

        write_json(
            output_root
            / "resume_state.json",
            resume_state_document,
        )

        print(
            "=" * 110
        )

        print(
            "GENERATION 276 CYCLE",
            cycle_number,
        )

        print(
            "=" * 110
        )

        print(
            "Incoming batches:",
            cycle_record[
                "incoming_batch_count"
            ],
        )

        print(
            "Accepted batches:",
            cycle_record[
                "accepted_batch_count"
            ],
        )

        print(
            "Rejected batches:",
            cycle_record[
                "rejected_batch_count"
            ],
        )

        print(
            "Training performed:",
            cycle_record[
                "training_performed"
            ],
        )

        print(
            "Checkpoint accepted:",
            cycle_record[
                "checkpoint_accepted"
            ],
        )

        print(
            "Rollback performed:",
            cycle_record[
                "rollback_performed"
            ],
        )

        print(
            "Disposition:",
            cycle_record[
                "disposition"
            ],
        )

        print(
            "Current n_iter_:",
            int(
                getattr(
                    current_model,
                    "n_iter_",
                    current_n_iter,
                )
            ),
        )

        print(
            "Best cycle:",
            best_cycle,
        )

        print(
            "Best balanced accuracy:",
            best_metrics[
                "balanced_accuracy"
            ],
        )

        print(
            "Best F1 macro:",
            best_metrics[
                "f1_macro"
            ],
        )

        print()

        if STOP_REQUESTED:
            print(
                "Controlled stop requested. "
                "Resume state has been written."
            )

            break

        remaining_seconds = (
            end_monotonic
            - time.monotonic()
        )

        if remaining_seconds <= 0:
            break

        sleep_seconds = min(
            cycle_seconds,
            remaining_seconds,
        )

        sleep_deadline = (
            time.monotonic()
            + sleep_seconds
        )

        while time.monotonic() < sleep_deadline:
            if STOP_REQUESTED:
                break

            time.sleep(
                min(
                    5.0,
                    max(
                        0.0,
                        sleep_deadline
                        - time.monotonic(),
                    ),
                )
            )

        if STOP_REQUESTED:
            break

    run_completed_at = utc_now()

    elapsed_seconds = (
        time.monotonic()
        - run_started_monotonic
    )

    duration_requirement_met = bool(
        elapsed_seconds
        >= requested_seconds
        - 1.0
    )

    controlled_stop = STOP_REQUESTED

    best_root = (
        output_root
        / "best_checkpoint"
    )

    best_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    final_best_model_path = (
        best_root
        / "best_estimator.joblib"
    )

    final_best_package_path = (
        best_root
        / "best_candidate_package.joblib"
    )

    final_best_predictions_path = (
        best_root
        / "best_holdout_predictions.csv"
    )

    joblib.dump(
        best_model,
        final_best_model_path,
    )

    joblib.dump(
        best_package,
        final_best_package_path,
    )

    final_best_prediction = np.asarray(
        best_model.predict(
            X_holdout
        )
    ).astype(str)

    best_prediction_frame = pd.DataFrame(
        {
            "actual":
                y_holdout.reset_index(
                    drop=True
                ),

            "best_checkpoint":
                final_best_prediction,
        }
    )

    holdout_frame = frozen[
        "holdout_frame"
    ]

    best_prediction_frame.insert(
        0,
        timestamp_column,
        holdout_frame[
            timestamp_column
        ].reset_index(
            drop=True
        ),
    )

    if symbol_column:
        best_prediction_frame.insert(
            1,
            symbol_column,
            holdout_frame[
                symbol_column
            ].reset_index(
                drop=True
            ),
        )

    best_prediction_frame.to_csv(
        final_best_predictions_path,
        index=False,
    )

    accepted_training_cycles = [
        record
        for record in cycle_records
        if record.get(
            "checkpoint_accepted"
        ) is True
    ]

    rejected_training_cycles = [
        record
        for record in cycle_records
        if record.get(
            "rollback_performed"
        ) is True
    ]

    heartbeat_cycles = [
        record
        for record in cycle_records
        if record.get(
            "heartbeat_only"
        ) is True
    ]

    final_status = (
        "completed"
        if duration_requirement_met
        else (
            "controlled_stop_resume_available"
            if controlled_stop
            else
            "incomplete"
        )
    )

    evidence_freeze = {
        "classification":
            "generation276_24h_evidence_freeze",

        "created_at":
            run_completed_at.isoformat(),

        "status":
            final_status,

        "duration": {
            "requested_hours":
                duration_hours,

            "elapsed_seconds":
                elapsed_seconds,

            "minimum_24h_requirement_met":
                duration_requirement_met,
        },

        "resume": {
            "resumed":
                resumed,

            "resume_count":
                resume_count,

            "controlled_stop":
                controlled_stop,

            "resume_state":
                str(
                    output_root
                    / "resume_state.json"
                ),
        },

        "starting_checkpoint": {
            "package":
                str(
                    START_PACKAGE_PATH
                ),

            "package_sha256":
                sha256_file(
                    START_PACKAGE_PATH
                ),

            "model":
                str(
                    START_MODEL_PATH
                ),

            "model_sha256":
                sha256_file(
                    START_MODEL_PATH
                ),

            "effective_n_iter":
                EXPECTED_START_N_ITER,

            "metrics":
                start_metrics,
        },

        "best_checkpoint": {
            "cycle":
                best_cycle,

            "effective_n_iter":
                best_n_iter,

            "metrics":
                best_metrics,

            "model":
                str(
                    final_best_model_path
                ),

            "model_sha256":
                sha256_file(
                    final_best_model_path
                ),

            "package":
                str(
                    final_best_package_path
                ),

            "package_sha256":
                sha256_file(
                    final_best_package_path
                ),

            "predictions":
                str(
                    final_best_predictions_path
                ),

            "predictions_sha256":
                sha256_file(
                    final_best_predictions_path
                ),
        },

        "experience": {
            "accepted_batch_count":
                len(
                    accepted_batches
                ),

            "rejected_batch_count":
                len(
                    rejected_batches
                ),

            "accepted_batches":
                accepted_batches,

            "rejected_batches":
                rejected_batches,

            "latest_training_timestamp":
                (
                    latest_training_timestamp.isoformat()
                    if latest_training_timestamp
                    is not None
                    else None
                ),
        },

        "cycles": {
            "total":
                len(cycle_records),

            "accepted_training_cycles":
                len(
                    accepted_training_cycles
                ),

            "degraded_cycles_rolled_back":
                len(
                    rejected_training_cycles
                ),

            "heartbeat_only_cycles":
                len(
                    heartbeat_cycles
                ),

            "records":
                cycle_records,
        },

        "frozen_holdout": {
            "rows":
                int(
                    len(
                        X_holdout
                    )
                ),

            "dataset":
                str(
                    FROZEN_DATASET_PATH
                ),

            "dataset_sha256":
                sha256_file(
                    FROZEN_DATASET_PATH
                ),

            "used_for_training":
                False,
        },

        "safety": {
            "candidate_registered":
                False,

            "database_registration":
                False,

            "candidate_promoted":
                False,

            "parent_replaced":
                False,

            "runtime_activated":
                False,

            "services_restarted":
                False,

            "orders_submitted":
                0,
        },
    }

    write_json(
        output_root
        / "evidence_freeze_manifest.json",
        evidence_freeze,
    )

    run_passed = bool(
        duration_requirement_met
        and len(cycle_records) > 0
        and final_best_model_path.is_file()
        and final_best_package_path.is_file()
    )

    result = {
        "classification":
            (
                "generation276_24h_autonomous_cycle_complete"
                if run_passed
                else (
                    "generation276_24h_autonomous_cycle_resumable"
                    if controlled_stop
                    else
                    "generation276_24h_autonomous_cycle_incomplete"
                )
            ),

        "passed":
            run_passed,

        "status":
            final_status,

        "duration_requirement_met":
            duration_requirement_met,

        "elapsed_seconds":
            elapsed_seconds,

        "cycle_count":
            len(cycle_records),

        "accepted_experience_batches":
            len(
                accepted_batches
            ),

        "rejected_experience_batches":
            len(
                rejected_batches
            ),

        "accepted_training_cycles":
            len(
                accepted_training_cycles
            ),

        "degraded_cycles_rolled_back":
            len(
                rejected_training_cycles
            ),

        "heartbeat_only_cycles":
            len(
                heartbeat_cycles
            ),

        "resumed":
            resumed,

        "resume_count":
            resume_count,

        "controlled_stop":
            controlled_stop,

        "starting_metrics":
            start_metrics,

        "best_cycle":
            best_cycle,

        "best_n_iter":
            best_n_iter,

        "best_metrics":
            best_metrics,

        "authorization": {
            "perform_final_generation276_review":
                run_passed,

            "resume_run":
                controlled_stop,

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

            "frozen_dataset_modified":
                False,

            "holdout_used_for_training":
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

        "artifacts": {
            "evidence_freeze":
                str(
                    output_root
                    / "evidence_freeze_manifest.json"
                ),

            "resume_state":
                str(
                    output_root
                    / "resume_state.json"
                ),

            "best_model":
                str(
                    final_best_model_path
                ),

            "best_package":
                str(
                    final_best_package_path
                ),

            "best_predictions":
                str(
                    final_best_predictions_path
                ),
        },
    }

    write_json(
        output_root
        / "result.json",
        result,
    )

    report_lines = [
        "=" * 110,
        "NEUROVEST — GENERATION 276 24-HOUR AUTONOMOUS TRAINING",
        "=" * 110,
        "",
        "Status:                         "
        + final_status,

        "Passed:                         "
        + str(run_passed),

        "Requested duration hours:       "
        + str(duration_hours),

        "Elapsed seconds:                "
        + str(elapsed_seconds),

        "24-hour requirement met:        "
        + str(
            duration_requirement_met
        ),

        "Controlled stop:                "
        + str(controlled_stop),

        "Resumed:                        "
        + str(resumed),

        "Resume count:                   "
        + str(resume_count),

        "",
        "EXPERIENCE",
        "  Accepted batches:              "
        + str(
            len(
                accepted_batches
            )
        ),

        "  Rejected batches:              "
        + str(
            len(
                rejected_batches
            )
        ),

        "  Accepted training cycles:      "
        + str(
            len(
                accepted_training_cycles
            )
        ),

        "  Degraded cycles rolled back:   "
        + str(
            len(
                rejected_training_cycles
            )
        ),

        "  Heartbeat-only cycles:         "
        + str(
            len(
                heartbeat_cycles
            )
        ),

        "",
        "BEST CHECKPOINT",
        "  Cycle:                         "
        + str(best_cycle),

        "  Effective n_iter_:             "
        + str(best_n_iter),

        "  Balanced accuracy:             "
        + str(
            best_metrics[
                "balanced_accuracy"
            ]
        ),

        "  F1 macro:                      "
        + str(
            best_metrics[
                "f1_macro"
            ]
        ),

        "",
        "SAFETY",
        "  Holdout used for training:     False",
        "  Candidate registration:        False",
        "  Database registration:         False",
        "  Candidate promotion:           False",
        "  Parent replacement:            False",
        "  Runtime activation:            False",
        "  Paper execution:               False",
        "  Broker execution:              False",
        "  SnapTrade execution:           False",
        "  Live execution:                False",
        "  Orders submitted:              0",
        "",
        "Structured result:",
        "  "
        + str(
            output_root
            / "result.json"
        ),

        "",
        "Evidence freeze:",
        "  "
        + str(
            output_root
            / "evidence_freeze_manifest.json"
        ),

        "",
        "Resume state:",
        "  "
        + str(
            output_root
            / "resume_state.json"
        ),

        "",
        "Best checkpoint package:",
        "  "
        + str(
            final_best_package_path
        ),

        "",
        "Terminal remains open.",
    ]

    (
        output_root
        / "report.txt"
    ).write_text(
        "\n".join(report_lines)
        + "\n",
        encoding="utf-8",
    )

    print()
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
        if run_passed
        else (
            2
            if controlled_stop
            else 1
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generation 276 24-hour autonomous experience "
            "accumulation with checkpoint resume, degradation "
            "rollback, and evidence freezing."
        )
    )

    parser.add_argument(
        "--qualify-only",
        action="store_true",
        help=(
            "Validate the runner without starting training."
        ),
    )

    parser.add_argument(
        "--qualification-output",
        type=Path,
        default=None,
        help=(
            "Optional qualification JSON destination."
        ),
    )

    parser.add_argument(
        "--run-training",
        action="store_true",
        help=(
            "Request the autonomous training cycle."
        ),
    )

    parser.add_argument(
        "--allow-training",
        action="store_true",
        help=(
            "Second explicit authorization required for training."
        ),
    )

    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help=(
            "Required isolated run directory."
        ),
    )

    parser.add_argument(
        "--experience-feed",
        type=Path,
        default=DEFAULT_FEED_ROOT,
        help=(
            "Directory containing incoming, accepted, and rejected "
            "experience-batch directories."
        ),
    )

    parser.add_argument(
        "--duration-hours",
        type=float,
        default=24.0,
        help=(
            "Wall-clock duration. Generation 276 requires at least 24."
        ),
    )

    parser.add_argument(
        "--cycle-minutes",
        type=float,
        default=60.0,
        help=(
            "Interval between experience-feed checks."
        ),
    )

    parser.add_argument(
        "--iterations-per-batch",
        type=int,
        default=5,
        help=(
            "Warm-start iterations added after each accepted batch."
        ),
    )

    parser.add_argument(
        "--phase-two-end-fraction",
        type=float,
        default=0.80,
        help=(
            "Frozen chronological training/holdout boundary."
        ),
    )

    parser.add_argument(
        "--balanced-accuracy-tolerance",
        type=float,
        default=0.0025,
        help=(
            "Maximum balanced-accuracy degradation from the best "
            "accepted checkpoint."
        ),
    )

    parser.add_argument(
        "--f1-tolerance",
        type=float,
        default=0.0025,
        help=(
            "Maximum F1-macro degradation from the best accepted "
            "checkpoint."
        ),
    )

    return parser


def main() -> int:
    signal.signal(
        signal.SIGINT,
        handle_stop_signal,
    )

    signal.signal(
        signal.SIGTERM,
        handle_stop_signal,
    )

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
                "generation276_runner_qualification_"
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

    if args.duration_hours < MINIMUM_DURATION_HOURS:
        parser.error(
            "--duration-hours must be at least 24."
        )

    if not qualification["qualified"]:
        print(
            json.dumps(
                qualification,
                indent=2,
                sort_keys=True,
            )
        )

        print(
            "BLOCKED: Generation 276 qualification failed.",
            file=sys.stderr,
        )

        return 1

    return run_autonomous_cycle(
        output_root=args.output_root,
        feed_root=args.experience_feed,
        duration_hours=args.duration_hours,
        cycle_minutes=args.cycle_minutes,
        iterations_per_batch=args.iterations_per_batch,
        phase_two_end_fraction=args.phase_two_end_fraction,
        balanced_accuracy_tolerance=args.balanced_accuracy_tolerance,
        f1_tolerance=args.f1_tolerance,
    )


if __name__ == "__main__":
    raise SystemExit(main())

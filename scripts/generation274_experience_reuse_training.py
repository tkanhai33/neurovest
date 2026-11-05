#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
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

from sklearn.base import clone
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
)


@dataclass(frozen=True)
class ChronologicalSplit:
    total_rows: int
    phase_one_end: int
    phase_two_end: int
    phase_one_rows: int
    phase_two_rows: int
    cumulative_training_rows: int
    holdout_rows: int


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


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


def write_json(
    path: Path,
    value: Any,
) -> None:
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
            "Model package is neither an estimator nor a dictionary."
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
        "No estimator exposing fit() and predict() was found."
    )


def extract_contract(
    package: Any,
) -> tuple[list[str], str]:
    if not isinstance(package, dict):
        raise RuntimeError(
            "Model package metadata is unavailable."
        )

    features = [
        str(value)
        for value in package.get(
            "features",
            [],
        )
    ]

    target = str(
        package.get(
            "target",
            "",
        )
    )

    if not features:
        raise RuntimeError(
            "Model package has no feature contract."
        )

    if not target:
        raise RuntimeError(
            "Model package has no target contract."
        )

    return features, target


def detect_timestamp_column(
    columns: list[str],
) -> str | None:
    candidates = (
        "timestamp",
        "date",
        "datetime",
        "market_date",
        "bar_time",
        "event_time",
    )

    for candidate in candidates:
        if candidate in columns:
            return candidate

    return None


def load_training_frame(
    dataset_path: Path,
    features: list[str],
    target: str,
) -> tuple[pd.DataFrame, str | None]:
    header = [
        str(column)
        for column in pd.read_csv(
            dataset_path,
            nrows=0,
        ).columns
    ]

    missing = sorted(
        set(features + [target])
        - set(header)
    )

    if missing:
        raise RuntimeError(
            "Dataset is missing required model columns:\n  "
            + "\n  ".join(missing)
        )

    timestamp_column = detect_timestamp_column(
        header
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

    if frame.empty:
        raise RuntimeError(
            "No usable rows remain after dataset normalization."
        )

    return frame, timestamp_column


def chronological_split(
    frame: pd.DataFrame,
    phase_one_fraction: float,
    phase_two_end_fraction: float,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    ChronologicalSplit,
]:
    row_count = int(
        len(frame)
    )

    phase_one_end = int(
        row_count
        * phase_one_fraction
    )

    phase_two_end = int(
        row_count
        * phase_two_end_fraction
    )

    if not (
        0
        < phase_one_end
        < phase_two_end
        < row_count
    ):
        raise RuntimeError(
            "Chronological split is invalid."
        )

    phase_one = frame.iloc[
        :phase_one_end
    ].copy()

    phase_two = frame.iloc[
        phase_one_end:
        phase_two_end
    ].copy()

    holdout = frame.iloc[
        phase_two_end:
    ].copy()

    split = ChronologicalSplit(
        total_rows=row_count,
        phase_one_end=phase_one_end,
        phase_two_end=phase_two_end,
        phase_one_rows=int(
            len(phase_one)
        ),
        phase_two_rows=int(
            len(phase_two)
        ),
        cumulative_training_rows=int(
            len(phase_one)
            + len(phase_two)
        ),
        holdout_rows=int(
            len(holdout)
        ),
    )

    return (
        phase_one,
        phase_two,
        holdout,
        split,
    )


def estimator_parameters(
    estimator: Any,
) -> dict[str, Any]:
    if not hasattr(
        estimator,
        "get_params",
    ):
        return {}

    return dict(
        estimator.get_params(
            deep=False
        )
    )


def determine_iteration_contract(
    estimator: Any,
    additional_iterations: int,
) -> tuple[str, int, int]:
    parameters = estimator_parameters(
        estimator
    )

    iteration_candidates = (
        "max_iter",
        "n_estimators",
        "max_iterations",
        "iterations",
    )

    for parameter in iteration_candidates:
        if parameter not in parameters:
            continue

        current = parameters.get(
            parameter
        )

        if not isinstance(
            current,
            (
                int,
                np.integer,
            ),
        ):
            continue

        current_value = int(
            current
        )

        final_value = (
            current_value
            + int(
                additional_iterations
            )
        )

        return (
            parameter,
            current_value,
            final_value,
        )

    raise RuntimeError(
        "Estimator has no supported iteration-count parameter."
    )


def build_phase_one_model(
    parent_estimator: Any,
    iteration_parameter: str,
    phase_one_iterations: int,
) -> Any:
    try:
        model = clone(
            parent_estimator
        )
    except Exception:
        model = deepcopy(
            parent_estimator
        )

    parameters = estimator_parameters(
        model
    )

    updates: dict[str, Any] = {
        iteration_parameter:
            int(
                phase_one_iterations
            ),
    }

    if "warm_start" in parameters:
        updates[
            "warm_start"
        ] = True

    model.set_params(
        **updates
    )

    return model


def continue_model(
    phase_one_model: Any,
    iteration_parameter: str,
    final_iterations: int,
) -> Any:
    model = deepcopy(
        phase_one_model
    )

    parameters = estimator_parameters(
        model
    )

    updates: dict[str, Any] = {
        iteration_parameter:
            int(
                final_iterations
            ),
    }

    if "warm_start" not in parameters:
        raise RuntimeError(
            "Estimator does not expose warm_start."
        )

    updates["warm_start"] = True

    model.set_params(
        **updates
    )

    return model


def build_cold_phase_two_model(
    parent_estimator: Any,
    iteration_parameter: str,
    additional_iterations: int,
) -> Any:
    try:
        model = clone(
            parent_estimator
        )
    except Exception:
        model = deepcopy(
            parent_estimator
        )

    parameters = estimator_parameters(
        model
    )

    updates: dict[str, Any] = {
        iteration_parameter:
            max(
                1,
                int(
                    additional_iterations
                ),
            ),
    }

    if "warm_start" in parameters:
        updates[
            "warm_start"
        ] = False

    model.set_params(
        **updates
    )

    return model


def evaluate(
    actual: pd.Series,
    predicted: np.ndarray,
) -> dict[str, float]:
    actual_values = actual.astype(
        str
    )

    predicted_values = np.asarray(
        predicted
    ).astype(str)

    return {
        "accuracy":
            float(
                accuracy_score(
                    actual_values,
                    predicted_values,
                )
            ),

        "balanced_accuracy":
            float(
                balanced_accuracy_score(
                    actual_values,
                    predicted_values,
                )
            ),

        "f1_macro":
            float(
                f1_score(
                    actual_values,
                    predicted_values,
                    average="macro",
                    zero_division=0,
                )
            ),
    }


def prediction_change_fraction(
    first: np.ndarray,
    second: np.ndarray,
) -> float:
    first_values = np.asarray(
        first
    ).astype(str)

    second_values = np.asarray(
        second
    ).astype(str)

    if len(first_values) != len(
        second_values
    ):
        return 1.0

    if len(first_values) == 0:
        return 0.0

    return float(
        np.mean(
            first_values
            != second_values
        )
    )


def replace_package_estimator(
    package: Any,
    package_key: str,
    estimator: Any,
) -> Any:
    if package_key == "package_root":
        return estimator

    if not isinstance(package, dict):
        raise RuntimeError(
            "Cannot replace estimator in non-dictionary package."
        )

    candidate_package = deepcopy(
        package
    )

    candidate_package[
        package_key
    ] = estimator

    candidate_package[
        "experience_reuse"
    ] = {
        "enabled":
            True,

        "strategy":
            "warm_start",

        "parent_package_preserved":
            True,
    }

    return candidate_package


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run isolated chronological experience-reuse training "
            "without replacing or promoting the parent model."
        )
    )

    parser.add_argument(
        "--parent-package",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--dataset",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--output",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--phase-one-fraction",
        type=float,
        default=0.60,
    )

    parser.add_argument(
        "--phase-two-end-fraction",
        type=float,
        default=0.80,
    )

    parser.add_argument(
        "--additional-iterations",
        type=int,
        default=25,
    )

    parser.add_argument(
        "--minimum-prediction-change",
        type=float,
        default=0.001,
    )

    parser.add_argument(
        "--require-metric-improvement",
        action="store_true",
    )

    arguments = parser.parse_args()

    parent_package_path = (
        arguments.parent_package.resolve()
    )

    dataset_path = (
        arguments.dataset.resolve()
    )

    output_root = (
        arguments.output.resolve()
    )

    output_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    models_root = (
        output_root
        / "models"
    )

    models_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    result_path = (
        output_root
        / "result.json"
    )

    metrics_path = (
        output_root
        / "qualification_metrics.json"
    )

    predictions_path = (
        output_root
        / "holdout_predictions.csv"
    )

    contract_path = (
        output_root
        / "training_contract.json"
    )

    report_path = (
        output_root
        / "report.txt"
    )

    handoff_path = (
        output_root
        / "handoff.txt"
    )

    phase_one_path = (
        models_root
        / "phase_one_model.joblib"
    )

    continued_estimator_path = (
        models_root
        / "continued_estimator.joblib"
    )

    continued_package_path = (
        models_root
        / "continued_candidate_package.joblib"
    )

    cold_phase_two_path = (
        models_root
        / "cold_phase_two_model.joblib"
    )

    if not parent_package_path.is_file():
        raise SystemExit(
            "BLOCKED: parent package does not exist."
        )

    if not dataset_path.is_file():
        raise SystemExit(
            "BLOCKED: dataset does not exist."
        )

    started = time.monotonic()

    parent_package = joblib.load(
        parent_package_path
    )

    package_key, parent_estimator = (
        find_estimator(
            parent_package
        )
    )

    features, target = extract_contract(
        parent_package
    )

    frame, timestamp_column = (
        load_training_frame(
            dataset_path,
            features,
            target,
        )
    )

    (
        phase_one,
        phase_two,
        holdout,
        split,
    ) = chronological_split(
        frame,
        arguments.phase_one_fraction,
        arguments.phase_two_end_fraction,
    )

    (
        iteration_parameter,
        parent_iterations,
        final_iterations,
    ) = determine_iteration_contract(
        parent_estimator,
        arguments.additional_iterations,
    )

    phase_one_iterations = max(
        1,
        parent_iterations,
    )

    phase_one_model = (
        build_phase_one_model(
            parent_estimator,
            iteration_parameter,
            phase_one_iterations,
        )
    )

    X_phase_one = phase_one[
        features
    ]

    y_phase_one = phase_one[
        target
    ]

    X_phase_two = phase_two[
        features
    ]

    y_phase_two = phase_two[
        target
    ]

    cumulative = pd.concat(
        [
            phase_one,
            phase_two,
        ],
        ignore_index=True,
    )

    X_cumulative = cumulative[
        features
    ]

    y_cumulative = cumulative[
        target
    ]

    X_holdout = holdout[
        features
    ]

    y_holdout = holdout[
        target
    ]

    print()
    print("=" * 110)
    print("PHASE 1 — INITIAL EXPERIENCE")
    print("=" * 110)
    print(
        "Rows:",
        len(X_phase_one),
        flush=True,
    )
    print(
        "Iterations:",
        phase_one_iterations,
        flush=True,
    )

    phase_one_model.fit(
        X_phase_one,
        y_phase_one,
    )

    joblib.dump(
        phase_one_model,
        phase_one_path,
        compress=3,
    )

    phase_one_prediction = np.asarray(
        phase_one_model.predict(
            X_holdout
        )
    ).astype(str)

    print()
    print("=" * 110)
    print("PHASE 2 — CONTINUE FROM PRESERVED EXPERIENCE")
    print("=" * 110)
    print(
        "New rows:",
        len(X_phase_two),
        flush=True,
    )
    print(
        "Cumulative rows:",
        len(X_cumulative),
        flush=True,
    )
    print(
        "Final iterations:",
        final_iterations,
        flush=True,
    )

    continued_model = continue_model(
        phase_one_model,
        iteration_parameter,
        final_iterations,
    )

    continued_model.fit(
        X_cumulative,
        y_cumulative,
    )

    joblib.dump(
        continued_model,
        continued_estimator_path,
        compress=3,
    )

    continued_package = (
        replace_package_estimator(
            parent_package,
            package_key,
            continued_model,
        )
    )

    if isinstance(
        continued_package,
        dict,
    ):
        continued_package[
            "experience_reuse"
        ].update(
            {
                "parent_package_sha256":
                    sha256_file(
                        parent_package_path
                    ),

                "dataset_sha256":
                    sha256_file(
                        dataset_path
                    ),

                "iteration_parameter":
                    iteration_parameter,

                "phase_one_iterations":
                    phase_one_iterations,

                "final_iterations":
                    final_iterations,

                "additional_iterations":
                    int(
                        arguments.additional_iterations
                    ),

                "phase_one_rows":
                    split.phase_one_rows,

                "phase_two_rows":
                    split.phase_two_rows,

                "cumulative_training_rows":
                    split.cumulative_training_rows,

                "holdout_rows":
                    split.holdout_rows,

                "qualified":
                    False,
            }
        )

    joblib.dump(
        continued_package,
        continued_package_path,
        compress=3,
    )

    continued_prediction = np.asarray(
        continued_model.predict(
            X_holdout
        )
    ).astype(str)

    print()
    print("=" * 110)
    print("PHASE 2 — COLD BASELINE")
    print("=" * 110)
    print(
        "Rows:",
        len(X_phase_two),
        flush=True,
    )
    print(
        "Iterations:",
        arguments.additional_iterations,
        flush=True,
    )

    cold_phase_two_model = (
        build_cold_phase_two_model(
            parent_estimator,
            iteration_parameter,
            arguments.additional_iterations,
        )
    )

    cold_phase_two_model.fit(
        X_phase_two,
        y_phase_two,
    )

    joblib.dump(
        cold_phase_two_model,
        cold_phase_two_path,
        compress=3,
    )

    cold_prediction = np.asarray(
        cold_phase_two_model.predict(
            X_holdout
        )
    ).astype(str)

    phase_one_metrics = evaluate(
        y_holdout,
        phase_one_prediction,
    )

    continued_metrics = evaluate(
        y_holdout,
        continued_prediction,
    )

    cold_metrics = evaluate(
        y_holdout,
        cold_prediction,
    )

    phase_one_to_continued_change = (
        prediction_change_fraction(
            phase_one_prediction,
            continued_prediction,
        )
    )

    continued_to_cold_change = (
        prediction_change_fraction(
            continued_prediction,
            cold_prediction,
        )
    )

    balanced_accuracy_improvement = (
        continued_metrics[
            "balanced_accuracy"
        ]
        - phase_one_metrics[
            "balanced_accuracy"
        ]
    )

    f1_improvement = (
        continued_metrics[
            "f1_macro"
        ]
        - phase_one_metrics[
            "f1_macro"
        ]
    )

    accuracy_improvement = (
        continued_metrics[
            "accuracy"
        ]
        - phase_one_metrics[
            "accuracy"
        ]
    )

    phase_one_hash = sha256_file(
        phase_one_path
    )

    continued_hash = sha256_file(
        continued_estimator_path
    )

    cold_hash = sha256_file(
        cold_phase_two_path
    )

    parent_hash = sha256_file(
        parent_package_path
    )

    state_changed = (
        phase_one_hash
        != continued_hash
    )

    parent_preserved = (
        sha256_file(
            parent_package_path
        )
        == parent_hash
    )

    state_continuity_proven = bool(
        state_changed
        and phase_one_path.is_file()
        and continued_estimator_path.is_file()
    )

    behavioral_learning_proven = bool(
        state_continuity_proven
        and phase_one_to_continued_change
        >= arguments.minimum_prediction_change
        and continued_to_cold_change
        >= arguments.minimum_prediction_change
    )

    metric_improvement = bool(
        balanced_accuracy_improvement > 0.0
        and f1_improvement > 0.0
    )

    if arguments.require_metric_improvement:
        qualified = bool(
            behavioral_learning_proven
            and metric_improvement
            and parent_preserved
        )
    else:
        qualified = bool(
            behavioral_learning_proven
            and parent_preserved
        )

    if isinstance(
        continued_package,
        dict,
    ):
        continued_package[
            "experience_reuse"
        ][
            "qualified"
        ] = qualified

        continued_package[
            "experience_reuse"
        ][
            "qualification_metrics"
        ] = {
            "state_continuity_proven":
                state_continuity_proven,

            "behavioral_learning_proven":
                behavioral_learning_proven,

            "metric_improvement":
                metric_improvement,

            "phase_one_to_continued_prediction_change":
                phase_one_to_continued_change,

            "continued_to_cold_prediction_change":
                continued_to_cold_change,

            "balanced_accuracy_improvement":
                balanced_accuracy_improvement,

            "f1_macro_improvement":
                f1_improvement,
        }

        joblib.dump(
            continued_package,
            continued_package_path,
            compress=3,
        )

    prediction_frame = pd.DataFrame(
        {
            "actual":
                y_holdout.reset_index(
                    drop=True
                ),

            "phase_one":
                phase_one_prediction,

            "continued_after_phase_two":
                continued_prediction,

            "cold_phase_two_only":
                cold_prediction,
        }
    )

    if timestamp_column:
        prediction_frame.insert(
            0,
            "timestamp",
            holdout[
                timestamp_column
            ].reset_index(
                drop=True
            ),
        )

    prediction_frame.to_csv(
        predictions_path,
        index=False,
    )

    contract = {
        "classification":
            "generation274_repository_experience_reuse_training_contract",

        "parent_package": {
            "path":
                str(
                    parent_package_path
                ),

            "sha256":
                parent_hash,

            "estimator_key":
                package_key,

            "estimator_module":
                parent_estimator.__class__.__module__,

            "estimator_class":
                parent_estimator.__class__.__name__,
        },

        "dataset": {
            "path":
                str(
                    dataset_path
                ),

            "sha256":
                sha256_file(
                    dataset_path
                ),

            "timestamp_column":
                timestamp_column,

            "rows":
                int(
                    len(frame)
                ),
        },

        "model_contract": {
            "feature_count":
                len(features),

            "features":
                features,

            "target":
                target,
        },

        "continuation": {
            "strategy":
                "warm_start",

            "iteration_parameter":
                iteration_parameter,

            "parent_iterations":
                parent_iterations,

            "phase_one_iterations":
                phase_one_iterations,

            "additional_iterations":
                int(
                    arguments.additional_iterations
                ),

            "final_iterations":
                final_iterations,

            "phase_two_uses_cumulative_history":
                True,

            "parent_package_preserved":
                parent_preserved,
        },

        "split":
            asdict(split),
    }

    write_json(
        contract_path,
        contract,
    )

    metrics = {
        "classification":
            (
                "generation274_repository_experience_reuse_qualified"
                if qualified
                else
                "generation274_repository_experience_reuse_blocked"
            ),

        "qualified":
            qualified,

        "state_continuity_proven":
            state_continuity_proven,

        "behavioral_learning_proven":
            behavioral_learning_proven,

        "metric_improvement":
            metric_improvement,

        "require_metric_improvement":
            bool(
                arguments.require_metric_improvement
            ),

        "metrics": {
            "phase_one":
                phase_one_metrics,

            "continued_after_phase_two":
                continued_metrics,

            "cold_phase_two_only":
                cold_metrics,
        },

        "comparisons": {
            "phase_one_to_continued_prediction_change_fraction":
                phase_one_to_continued_change,

            "continued_to_cold_prediction_change_fraction":
                continued_to_cold_change,

            "accuracy_improvement":
                accuracy_improvement,

            "balanced_accuracy_improvement":
                balanced_accuracy_improvement,

            "f1_macro_improvement":
                f1_improvement,
        },

        "hashes": {
            "parent_package":
                parent_hash,

            "phase_one_model":
                phase_one_hash,

            "continued_estimator":
                continued_hash,

            "continued_candidate_package":
                sha256_file(
                    continued_package_path
                ),

            "cold_phase_two_model":
                cold_hash,
        },

        "elapsed_seconds":
            time.monotonic()
            - started,
    }

    write_json(
        metrics_path,
        metrics,
    )

    checks = {
        "parent_package_loaded":
            parent_package is not None,

        "estimator_found":
            parent_estimator is not None,

        "feature_contract_loaded":
            bool(features),

        "exact_18_features_loaded":
            len(features) == 18,

        "target_loaded":
            bool(target),

        "chronological_split_valid":
            (
                split.phase_one_rows > 0
                and split.phase_two_rows > 0
                and split.holdout_rows > 0
            ),

        "warm_start_supported":
            (
                "warm_start"
                in estimator_parameters(
                    parent_estimator
                )
            ),

        "phase_one_model_preserved":
            phase_one_path.is_file(),

        "continued_model_created":
            continued_estimator_path.is_file(),

        "continued_candidate_package_created":
            continued_package_path.is_file(),

        "cold_phase_two_baseline_created":
            cold_phase_two_path.is_file(),

        "parent_package_preserved":
            parent_preserved,

        "model_state_changed":
            state_changed,

        "holdout_behavior_changed":
            phase_one_to_continued_change
            >= arguments.minimum_prediction_change,

        "continued_behavior_differs_from_cold":
            continued_to_cold_change
            >= arguments.minimum_prediction_change,

        "state_continuity_proven":
            state_continuity_proven,

        "behavioral_learning_proven":
            behavioral_learning_proven,

        "repository_training_path_qualified":
            qualified,
    }

    result = {
        "classification":
            metrics[
                "classification"
            ],

        "passed":
            qualified,

        "repository_training_path_qualified":
            qualified,

        "state_continuity_proven":
            state_continuity_proven,

        "behavioral_learning_proven":
            behavioral_learning_proven,

        "metric_improvement":
            metric_improvement,

        "checks":
            checks,

        "authorization": {
            "use_repository_experience_reuse_path_in_controlled_training":
                qualified,

            "replace_production_parent":
                False,

            "promote_candidate":
                False,

            "runtime_activation":
                False,

            "database_registration":
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
            "parent_package_modified":
                False,

            "production_model_replaced":
                False,

            "candidate_promoted":
                False,

            "runtime_activated":
                False,

            "orders_submitted":
                0,
        },

        "artifacts": {
            "contract":
                str(
                    contract_path
                ),

            "metrics":
                str(
                    metrics_path
                ),

            "predictions":
                str(
                    predictions_path
                ),

            "phase_one_model":
                str(
                    phase_one_path
                ),

            "continued_estimator":
                str(
                    continued_estimator_path
                ),

            "continued_candidate_package":
                str(
                    continued_package_path
                ),

            "cold_phase_two_model":
                str(
                    cold_phase_two_path
                ),
        },
    }

    write_json(
        result_path,
        result,
    )

    report_lines = [
        "=" * 110,
        "NEUROVEST — REPOSITORY EXPERIENCE-REUSE TRAINING QUALIFICATION",
        "=" * 110,
        "",
        "Qualification: "
        + (
            "PASS"
            if qualified
            else "BLOCKED"
        ),
        "",
        "ESTIMATOR",
        "  Class:                         "
        + parent_estimator.__class__.__module__
        + "."
        + parent_estimator.__class__.__name__,

        "  Package key:                   "
        + package_key,

        "  Continuation strategy:         warm_start",
        "  Phase-2 input:                 cumulative Phase 1 + Phase 2",
        "  Iteration parameter:           "
        + iteration_parameter,

        "  Phase-1 iterations:            "
        + str(
            phase_one_iterations
        ),

        "  Final iterations:              "
        + str(
            final_iterations
        ),
        "",
        "DATA",
        "  Total usable rows:             "
        + str(
            split.total_rows
        ),

        "  Phase-1 rows:                  "
        + str(
            split.phase_one_rows
        ),

        "  New Phase-2 rows:              "
        + str(
            split.phase_two_rows
        ),

        "  Cumulative training rows:      "
        + str(
            split.cumulative_training_rows
        ),

        "  Holdout rows:                  "
        + str(
            split.holdout_rows
        ),
        "",
        "CHECKS",
    ]

    for name, value in checks.items():
        report_lines.append(
            "  "
            + (
                "PASS"
                if value
                else "BLOCKED"
            )
            + " — "
            + name
        )

    report_lines.extend(
        [
            "",
            "PHASE-1 METRICS",
            "  Accuracy:                     "
            + str(
                phase_one_metrics[
                    "accuracy"
                ]
            ),

            "  Balanced accuracy:            "
            + str(
                phase_one_metrics[
                    "balanced_accuracy"
                ]
            ),

            "  F1 macro:                     "
            + str(
                phase_one_metrics[
                    "f1_macro"
                ]
            ),
            "",
            "CONTINUED MODEL METRICS",
            "  Accuracy:                     "
            + str(
                continued_metrics[
                    "accuracy"
                ]
            ),

            "  Balanced accuracy:            "
            + str(
                continued_metrics[
                    "balanced_accuracy"
                ]
            ),

            "  F1 macro:                     "
            + str(
                continued_metrics[
                    "f1_macro"
                ]
            ),
            "",
            "COLD PHASE-2 METRICS",
            "  Accuracy:                     "
            + str(
                cold_metrics[
                    "accuracy"
                ]
            ),

            "  Balanced accuracy:            "
            + str(
                cold_metrics[
                    "balanced_accuracy"
                ]
            ),

            "  F1 macro:                     "
            + str(
                cold_metrics[
                    "f1_macro"
                ]
            ),
            "",
            "LEARNING COMPARISONS",
            "  Phase-1 → continued prediction change:"
            + " "
            + str(
                phase_one_to_continued_change
            ),

            "  Continued vs cold prediction change:"
            + " "
            + str(
                continued_to_cold_change
            ),

            "  Balanced-accuracy improvement:"
            + " "
            + str(
                balanced_accuracy_improvement
            ),

            "  F1 improvement:               "
            + str(
                f1_improvement
            ),
            "",
            "FINAL DISPOSITION",
            "  State continuity proven:      "
            + str(
                state_continuity_proven
            ),

            "  Behavioral learning proven:  "
            + str(
                behavioral_learning_proven
            ),

            "  Metric improvement:           "
            + str(
                metric_improvement
            ),

            "  Repository path qualified:   "
            + str(
                qualified
            ),

            "  Parent package preserved:    "
            + str(
                parent_preserved
            ),

            "  Production replacement:      False",
            "  Promotion:                   False",
            "  Runtime activation:          False",
            "",
            "Continued candidate package:",
            "  "
            + str(
                continued_package_path
            ),

            "",
            "Qualification metrics:",
            "  "
            + str(
                metrics_path
            ),

            "",
            "Training contract:",
            "  "
            + str(
                contract_path
            ),

            "",
            "Holdout predictions:",
            "  "
            + str(
                predictions_path
            ),

            "",
            "Structured result:",
            "  "
            + str(
                result_path
            ),

            "",
            "Parent model modified: no",
            "Production model replaced: no",
            "Candidate promoted: no",
            "Runtime activation: disabled",
            "Orders submitted: 0",
            "Terminal remains open.",
        ]
    )

    report_path.write_text(
        "\n".join(
            report_lines
        )
        + "\n",
        encoding="utf-8",
    )

    handoff_path.write_text(
        "\n".join(
            [
                "=" * 110,
                "NEUROVEST — REPOSITORY EXPERIENCE-REUSE HANDOFF",
                "=" * 110,
                "",
                "Repository training path qualified:",
                "  "
                + str(
                    qualified
                ),
                "",
                "State continuity proven:",
                "  "
                + str(
                    state_continuity_proven
                ),
                "",
                "Behavioral learning proven:",
                "  "
                + str(
                    behavioral_learning_proven
                ),
                "",
                "Metric improvement:",
                "  "
                + str(
                    metric_improvement
                ),
                "",
                "Continued candidate package:",
                "  "
                + str(
                    continued_package_path
                ),
                "",
                "Next action:",
                (
                    "  Connect this qualified path to the controlled Generation trainer"
                    if qualified
                    else
                    "  Review qualification_metrics.json"
                ),
                "",
                "Parent replacement:",
                "  NOT PERFORMED",
                "",
                "Promotion:",
                "  NOT AUTHORIZED",
                "",
                "Runtime activation:",
                "  DISABLED",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print(
        report_path.read_text(
            encoding="utf-8",
        )
    )

    return 0 if qualified else 1


if __name__ == "__main__":
    raise SystemExit(
        main()
    )

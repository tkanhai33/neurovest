#!/usr/bin/env python3

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
import argparse
import csv
import hashlib
import json
import math
import sys
import time

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import (
    ExtraTreesClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


FEATURE_COLUMNS = [
    "return_1d",
    "return_5d",
    "return_10d",
    "return_20d",
    "volatility_5d",
    "volatility_20d",
    "range_fraction",
    "close_to_sma_5",
    "close_to_sma_20",
    "close_to_sma_50",
    "volume_change_1d",
    "volume_ratio_20d",
]

TARGET_COLUMN = "target_next_up"
RETURN_COLUMN = "future_return_1d"

RANDOM_SEED = 20260803
TRANSACTION_COST_BPS = 10.0
TRANSACTION_COST_RATE = (
    TRANSACTION_COST_BPS
    / 10000.0
)

THRESHOLDS = [
    round(value, 2)
    for value in np.arange(
        0.50,
        0.601,
        0.01,
    )
]

SCOPES = (
    "ALL",
    "CA",
    "US",
)

MODES = (
    "long_only",
    "long_short",
)


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def model_factories() -> dict[
    str,
    Callable[[], Any],
]:
    return {
        "logistic_regression":
            lambda: Pipeline(
                [
                    (
                        "scale",
                        StandardScaler(),
                    ),
                    (
                        "model",
                        LogisticRegression(
                            max_iter=1000,
                            class_weight="balanced",
                            random_state=RANDOM_SEED,
                        ),
                    ),
                ]
            ),

        "hist_gradient_boosting":
            lambda: HistGradientBoostingClassifier(
                learning_rate=0.05,
                max_iter=220,
                max_leaf_nodes=31,
                min_samples_leaf=30,
                l2_regularization=1.0,
                random_state=RANDOM_SEED,
            ),

        "random_forest":
            lambda: RandomForestClassifier(
                n_estimators=180,
                max_depth=12,
                min_samples_leaf=20,
                max_features="sqrt",
                class_weight="balanced_subsample",
                n_jobs=-1,
                random_state=RANDOM_SEED,
            ),

        "extra_trees":
            lambda: ExtraTreesClassifier(
                n_estimators=180,
                max_depth=14,
                min_samples_leaf=15,
                max_features="sqrt",
                class_weight="balanced",
                n_jobs=-1,
                random_state=RANDOM_SEED,
            ),
    }


def probability_one(
    model: Any,
    features: pd.DataFrame,
) -> np.ndarray:
    probabilities = model.predict_proba(
        features
    )

    classes = getattr(
        model,
        "classes_",
        None,
    )

    if (
        classes is None
        and hasattr(
            model,
            "named_steps",
        )
    ):
        classes = getattr(
            model.named_steps["model"],
            "classes_",
            None,
        )

    class_values = list(
        classes
        if classes is not None
        else [0, 1]
    )

    index = (
        class_values.index(1)
        if 1 in class_values
        else probabilities.shape[1] - 1
    )

    return probabilities[:, index]


def safe_auc(
    target: pd.Series,
    probability: np.ndarray,
) -> float | None:
    try:
        return float(
            roc_auc_score(
                target,
                probability,
            )
        )
    except ValueError:
        return None


def classification_metrics(
    target: pd.Series,
    probability: np.ndarray,
) -> dict[str, Any]:
    prediction = (
        probability >= 0.50
    ).astype(int)

    majority = int(
        target.value_counts()
        .idxmax()
    )

    baseline = np.full(
        len(target),
        majority,
        dtype=int,
    )

    accuracy = float(
        accuracy_score(
            target,
            prediction,
        )
    )

    baseline_accuracy = float(
        accuracy_score(
            target,
            baseline,
        )
    )

    return {
        "rows":
            int(len(target)),

        "accuracy":
            accuracy,

        "baseline_accuracy":
            baseline_accuracy,

        "accuracy_delta":
            accuracy
            - baseline_accuracy,

        "balanced_accuracy":
            float(
                balanced_accuracy_score(
                    target,
                    prediction,
                )
            ),

        "roc_auc":
            safe_auc(
                target,
                probability,
            ),
    }


def maximum_drawdown(
    returns: pd.Series,
) -> float:
    if returns.empty:
        return 0.0

    equity = (
        1.0
        + returns.fillna(0.0)
    ).cumprod()

    drawdown = (
        equity
        / equity.cummax()
        - 1.0
    )

    return float(
        drawdown.min()
    )


def strategy_metrics(
    frame: pd.DataFrame,
    probability: np.ndarray,
    *,
    threshold: float,
    mode: str,
) -> dict[str, Any]:
    working = frame[
        [
            "timestamp",
            "provider_symbol",
            RETURN_COLUMN,
        ]
    ].copy()

    working["probability"] = probability

    if mode == "long_only":
        working["position"] = np.where(
            working["probability"]
            >= threshold,
            1.0,
            0.0,
        )

    elif mode == "long_short":
        working["position"] = np.select(
            [
                working["probability"]
                >= threshold,

                working["probability"]
                <= 1.0 - threshold,
            ],
            [
                1.0,
                -1.0,
            ],
            default=0.0,
        )

    else:
        raise ValueError(
            f"Unsupported strategy mode: {mode}"
        )

    working = working.sort_values(
        [
            "provider_symbol",
            "timestamp",
        ],
        kind="stable",
    )

    working["previous_position"] = (
        working.groupby(
            "provider_symbol",
            sort=False,
        )["position"]
        .shift(1)
        .fillna(0.0)
    )

    working["turnover"] = (
        working["position"]
        - working["previous_position"]
    ).abs()

    working["gross_return"] = (
        working["position"]
        * working[RETURN_COLUMN]
    )

    working["transaction_cost"] = (
        working["turnover"]
        * TRANSACTION_COST_RATE
    )

    working["net_return"] = (
        working["gross_return"]
        - working["transaction_cost"]
    )

    active = (
        working["position"] != 0.0
    )

    daily = (
        working.groupby(
            "timestamp",
            sort=True,
        )
        .agg(
            net_return=(
                "net_return",
                "mean",
            ),
            gross_return=(
                "gross_return",
                "mean",
            ),
            active_positions=(
                "position",
                lambda values:
                    int(
                        (
                            values != 0.0
                        ).sum()
                    ),
            ),
            turnover_units=(
                "turnover",
                "sum",
            ),
        )
        .reset_index()
    )

    daily_returns = (
        daily["net_return"]
        .replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )
        .dropna()
    )

    total_return = 0.0
    annualized_return = 0.0
    annualized_volatility = 0.0
    sharpe = 0.0

    if not daily_returns.empty:
        gross = float(
            (
                1.0
                + daily_returns
            ).prod()
        )

        total_return = (
            gross - 1.0
        )

        if gross > 0.0:
            annualized_return = float(
                gross
                ** (
                    252.0
                    / len(daily_returns)
                )
                - 1.0
            )

        if len(daily_returns) > 1:
            annualized_volatility = float(
                daily_returns.std(
                    ddof=1
                )
                * math.sqrt(252.0)
            )

        if annualized_volatility > 0.0:
            sharpe = (
                annualized_return
                / annualized_volatility
            )

    trades = int(
        (
            working["turnover"]
            > 0.0
        ).sum()
    )

    active_rows = int(
        active.sum()
    )

    winning_rows = int(
        (
            active
            & (
                working["net_return"]
                > 0.0
            )
        ).sum()
    )

    return {
        "threshold":
            float(threshold),

        "mode":
            mode,

        "rows":
            int(len(working)),

        "days":
            int(
                daily["timestamp"]
                .nunique()
            ),

        "active_rows":
            active_rows,

        "coverage":
            float(active.mean()),

        "trades":
            trades,

        "turnover_units":
            float(
                working["turnover"]
                .sum()
            ),

        "transaction_cost_bps":
            TRANSACTION_COST_BPS,

        "net_total_return":
            float(total_return),

        "net_annualized_return":
            float(annualized_return),

        "net_annualized_volatility":
            float(annualized_volatility),

        "net_sharpe":
            float(sharpe),

        "maximum_drawdown":
            maximum_drawdown(
                daily_returns
            ),

        "hit_rate":
            (
                float(
                    winning_rows
                    / active_rows
                )
                if active_rows
                else 0.0
            ),

        "average_daily_positions":
            float(
                daily[
                    "active_positions"
                ].mean()
            )
            if not daily.empty
            else 0.0,

        "minimum_daily_positions":
            int(
                daily[
                    "active_positions"
                ].min()
            )
            if not daily.empty
            else 0,
    }


def scope_frame(
    frame: pd.DataFrame,
    scope: str,
) -> pd.DataFrame:
    if scope == "ALL":
        return frame.copy()

    return frame[
        frame["country"] == scope
    ].copy()


def candidate_id(
    *,
    model_name: str,
    scope: str,
    mode: str,
    threshold: float,
) -> str:
    payload = (
        f"{model_name}|"
        f"{scope}|"
        f"{mode}|"
        f"{threshold:.2f}|"
        f"{TRANSACTION_COST_BPS}|"
        f"{RANDOM_SEED}"
    )

    return (
        "stage7s_candidate_"
        + hashlib.sha256(
            payload.encode(
                "utf-8"
            )
        ).hexdigest()[:20]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Stage 7S isolated strategy "
            "threshold search"
        )
    )

    parser.add_argument(
        "--features",
        required=True,
    )

    parser.add_argument(
        "--stage7r-result",
        required=True,
    )

    parser.add_argument(
        "--output",
        required=True,
    )

    parser.add_argument(
        "--minimum-trades",
        type=int,
        default=100,
    )

    parser.add_argument(
        "--minimum-coverage",
        type=float,
        default=0.01,
    )

    args = parser.parse_args()

    features_path = Path(
        args.features
    )

    stage7r_result_path = Path(
        args.stage7r_result
    )

    output_root = Path(
        args.output
    )

    output_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    candidates_path = (
        output_root
        / "strategy_candidates.csv"
    )

    walk_path = (
        output_root
        / "walk_forward.csv"
    )

    selected_path = (
        output_root
        / "selected_strategy.json"
    )

    model_path = (
        output_root
        / "stage7s_selected_model.joblib"
    )

    result_path = (
        output_root
        / "result.json"
    )

    report_path = (
        output_root
        / "report.txt"
    )

    print()
    print("=" * 100)
    print(
        "STAGE 7S STRATEGY THRESHOLD SEARCH"
    )
    print("=" * 100)

    dataset = pd.read_csv(
        features_path,
        low_memory=False,
    )

    stage7r_result = json.loads(
        stage7r_result_path.read_text(
            encoding="utf-8"
        )
    )

    required_columns = {
        "timestamp",
        "provider_symbol",
        "country",
        TARGET_COLUMN,
        RETURN_COLUMN,
        *FEATURE_COLUMNS,
    }

    missing_columns = sorted(
        required_columns
        - set(dataset.columns)
    )

    if missing_columns:
        raise SystemExit(
            "BLOCKED: required columns missing: "
            + ", ".join(
                missing_columns
            )
        )

    dataset["timestamp"] = (
        pd.to_datetime(
            dataset["timestamp"],
            errors="coerce",
            utc=True,
        )
    )

    numeric_columns = (
        FEATURE_COLUMNS
        + [
            TARGET_COLUMN,
            RETURN_COLUMN,
        ]
    )

    for column in numeric_columns:
        dataset[column] = (
            pd.to_numeric(
                dataset[column],
                errors="coerce",
            )
        )

    dataset = (
        dataset.replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )
        .dropna(
            subset=[
                "timestamp",
                "provider_symbol",
                "country",
                *numeric_columns,
            ]
        )
        .sort_values(
            [
                "timestamp",
                "provider_symbol",
            ],
            kind="stable",
        )
        .drop_duplicates(
            subset=[
                "provider_symbol",
                "timestamp",
            ],
            keep="last",
        )
        .reset_index(
            drop=True
        )
    )

    dataset[TARGET_COLUMN] = (
        dataset[TARGET_COLUMN]
        .astype(int)
    )

    unique_dates = np.array(
        sorted(
            dataset["timestamp"]
            .unique()
        )
    )

    if len(unique_dates) < 300:
        raise SystemExit(
            "BLOCKED: fewer than 300 "
            "unique trading dates."
        )

    training_boundary = unique_dates[
        int(
            len(unique_dates)
            * 0.60
        )
    ]

    validation_boundary = unique_dates[
        int(
            len(unique_dates)
            * 0.80
        )
    ]

    training = dataset[
        dataset["timestamp"]
        < training_boundary
    ].copy()

    validation = dataset[
        (
            dataset["timestamp"]
            >= training_boundary
        )
        & (
            dataset["timestamp"]
            < validation_boundary
        )
    ].copy()

    test = dataset[
        dataset["timestamp"]
        >= validation_boundary
    ].copy()

    if min(
        len(training),
        len(validation),
        len(test),
    ) <= 0:
        raise SystemExit(
            "BLOCKED: one chronological "
            "partition is empty."
        )

    if not (
        training["timestamp"].max()
        < validation["timestamp"].min()
        <= validation["timestamp"].max()
        < test["timestamp"].min()
    ):
        raise SystemExit(
            "BLOCKED: chronological "
            "partition overlap detected."
        )

    factories = model_factories()

    selected_model_name = str(
        stage7r_result.get(
            "summary",
            {},
        ).get(
            "selected_model",
            "extra_trees",
        )
    )

    if selected_model_name not in factories:
        selected_model_name = (
            "extra_trees"
        )

    print()
    print("Dataset:")
    print(
        f"  rows={len(dataset)}"
    )
    print(
        "  symbols="
        f"{dataset['provider_symbol'].nunique()}"
    )
    print(
        f"  countries="
        f"{sorted(dataset['country'].unique())}"
    )

    print()
    print("Chronological partitions:")
    print(
        f"  training={len(training)}"
    )
    print(
        f"  validation={len(validation)}"
    )
    print(
        f"  test={len(test)}"
    )

    print()
    print("Model family:")
    print(
        f"  {selected_model_name}"
    )

    model = factories[
        selected_model_name
    ]()

    started = time.time()

    print()
    print("Fitting validation-selection model...")

    model.fit(
        training[FEATURE_COLUMNS],
        training[TARGET_COLUMN],
    )

    print(
        f"  completed in "
        f"{time.time() - started:.1f}s"
    )

    validation_probability = (
        probability_one(
            model,
            validation[
                FEATURE_COLUMNS
            ],
        )
    )

    test_probability_before_refit = (
        probability_one(
            model,
            test[
                FEATURE_COLUMNS
            ],
        )
    )

    candidate_records: list[
        dict[str, Any]
    ] = []

    print()
    print("Searching thresholds, scopes and modes...")

    for scope in SCOPES:
        validation_scope = scope_frame(
            validation,
            scope,
        )

        test_scope = scope_frame(
            test,
            scope,
        )

        if (
            validation_scope.empty
            or test_scope.empty
        ):
            continue

        validation_indices = (
            validation_scope.index
            .to_numpy()
        )

        test_indices = (
            test_scope.index
            .to_numpy()
        )

        validation_position = (
            validation.index.get_indexer(
                validation_indices
            )
        )

        test_position = (
            test.index.get_indexer(
                test_indices
            )
        )

        scoped_validation_probability = (
            validation_probability[
                validation_position
            ]
        )

        scoped_test_probability = (
            test_probability_before_refit[
                test_position
            ]
        )

        validation_classification = (
            classification_metrics(
                validation_scope[
                    TARGET_COLUMN
                ],
                scoped_validation_probability,
            )
        )

        test_classification = (
            classification_metrics(
                test_scope[
                    TARGET_COLUMN
                ],
                scoped_test_probability,
            )
        )

        for mode in MODES:
            for threshold in THRESHOLDS:
                validation_strategy = (
                    strategy_metrics(
                        validation_scope,
                        scoped_validation_probability,
                        threshold=threshold,
                        mode=mode,
                    )
                )

                test_strategy = (
                    strategy_metrics(
                        test_scope,
                        scoped_test_probability,
                        threshold=threshold,
                        mode=mode,
                    )
                )

                eligible = (
                    validation_strategy[
                        "trades"
                    ]
                    >= args.minimum_trades
                    and validation_strategy[
                        "coverage"
                    ]
                    >= args.minimum_coverage
                )

                candidate_records.append(
                    {
                        "candidate_id":
                            candidate_id(
                                model_name=
                                    selected_model_name,

                                scope=scope,
                                mode=mode,
                                threshold=threshold,
                            ),

                        "model_name":
                            selected_model_name,

                        "scope":
                            scope,

                        "mode":
                            mode,

                        "threshold":
                            threshold,

                        "minimum_required_trades":
                            args.minimum_trades,

                        "minimum_required_coverage":
                            args.minimum_coverage,

                        "validation_eligible":
                            bool(eligible),

                        "validation_rows":
                            int(
                                len(
                                    validation_scope
                                )
                            ),

                        "validation_symbols":
                            int(
                                validation_scope[
                                    "provider_symbol"
                                ].nunique()
                            ),

                        "validation_accuracy":
                            validation_classification[
                                "accuracy"
                            ],

                        "validation_baseline_accuracy":
                            validation_classification[
                                "baseline_accuracy"
                            ],

                        "validation_accuracy_delta":
                            validation_classification[
                                "accuracy_delta"
                            ],

                        "validation_roc_auc":
                            validation_classification[
                                "roc_auc"
                            ],

                        "validation_trades":
                            validation_strategy[
                                "trades"
                            ],

                        "validation_coverage":
                            validation_strategy[
                                "coverage"
                            ],

                        "validation_average_daily_positions":
                            validation_strategy[
                                "average_daily_positions"
                            ],

                        "validation_net_total_return":
                            validation_strategy[
                                "net_total_return"
                            ],

                        "validation_net_annualized_return":
                            validation_strategy[
                                "net_annualized_return"
                            ],

                        "validation_net_sharpe":
                            validation_strategy[
                                "net_sharpe"
                            ],

                        "validation_maximum_drawdown":
                            validation_strategy[
                                "maximum_drawdown"
                            ],

                        "validation_hit_rate":
                            validation_strategy[
                                "hit_rate"
                            ],

                        "test_rows":
                            int(
                                len(test_scope)
                            ),

                        "test_symbols":
                            int(
                                test_scope[
                                    "provider_symbol"
                                ].nunique()
                            ),

                        "test_accuracy":
                            test_classification[
                                "accuracy"
                            ],

                        "test_baseline_accuracy":
                            test_classification[
                                "baseline_accuracy"
                            ],

                        "test_accuracy_delta":
                            test_classification[
                                "accuracy_delta"
                            ],

                        "test_roc_auc":
                            test_classification[
                                "roc_auc"
                            ],

                        "test_trades":
                            test_strategy[
                                "trades"
                            ],

                        "test_coverage":
                            test_strategy[
                                "coverage"
                            ],

                        "test_average_daily_positions":
                            test_strategy[
                                "average_daily_positions"
                            ],

                        "test_net_total_return":
                            test_strategy[
                                "net_total_return"
                            ],

                        "test_net_annualized_return":
                            test_strategy[
                                "net_annualized_return"
                            ],

                        "test_net_sharpe":
                            test_strategy[
                                "net_sharpe"
                            ],

                        "test_maximum_drawdown":
                            test_strategy[
                                "maximum_drawdown"
                            ],

                        "test_hit_rate":
                            test_strategy[
                                "hit_rate"
                            ],

                        "transaction_cost_bps":
                            TRANSACTION_COST_BPS,

                        "promotion_authorized":
                            False,

                        "paper_execution_authorized":
                            False,

                        "broker_execution_authorized":
                            False,

                        "live_execution_authorized":
                            False,
                    }
                )

    candidate_frame = pd.DataFrame(
        candidate_records
    )

    if candidate_frame.empty:
        raise SystemExit(
            "BLOCKED: no Stage 7S "
            "candidates were produced."
        )

    eligible_frame = candidate_frame[
        candidate_frame[
            "validation_eligible"
        ]
        == True
    ].copy()

    if eligible_frame.empty:
        selected_row = (
            candidate_frame.sort_values(
                by=[
                    "validation_net_sharpe",
                    "validation_net_annualized_return",
                    "validation_trades",
                    "validation_coverage",
                ],
                ascending=[
                    False,
                    False,
                    False,
                    False,
                ],
                kind="stable",
            )
            .iloc[0]
        )

        selection_classification = (
            "no_candidate_met_minimum_activity"
        )

    else:
        selected_row = (
            eligible_frame.sort_values(
                by=[
                    "validation_net_sharpe",
                    "validation_net_annualized_return",
                    "validation_accuracy_delta",
                    "validation_trades",
                ],
                ascending=[
                    False,
                    False,
                    False,
                    False,
                ],
                kind="stable",
            )
            .iloc[0]
        )

        selection_classification = (
            "validation_candidate_selected"
        )

    selected_candidate = {
        key:
            (
                value.item()
                if hasattr(
                    value,
                    "item",
                )
                else value
            )
        for key, value
        in selected_row.to_dict().items()
    }

    candidate_frame = (
        candidate_frame.sort_values(
            by=[
                "validation_eligible",
                "validation_net_sharpe",
                "validation_net_annualized_return",
                "validation_trades",
            ],
            ascending=[
                False,
                False,
                False,
                False,
            ],
            kind="stable",
        )
        .reset_index(
            drop=True
        )
    )

    candidate_frame.insert(
        0,
        "rank",
        range(
            1,
            len(candidate_frame) + 1,
        ),
    )

    candidate_frame.to_csv(
        candidates_path,
        index=False,
    )

    selected_scope = str(
        selected_candidate["scope"]
    )

    selected_mode = str(
        selected_candidate["mode"]
    )

    selected_threshold = float(
        selected_candidate["threshold"]
    )

    print()
    print("Selected validation candidate:")
    print(
        json.dumps(
            {
                "candidate_id":
                    selected_candidate[
                        "candidate_id"
                    ],

                "scope":
                    selected_scope,

                "mode":
                    selected_mode,

                "threshold":
                    selected_threshold,

                "validation_eligible":
                    selected_candidate[
                        "validation_eligible"
                    ],

                "validation_trades":
                    selected_candidate[
                        "validation_trades"
                    ],

                "validation_coverage":
                    selected_candidate[
                        "validation_coverage"
                    ],

                "validation_net_sharpe":
                    selected_candidate[
                        "validation_net_sharpe"
                    ],

                "test_trades":
                    selected_candidate[
                        "test_trades"
                    ],

                "test_coverage":
                    selected_candidate[
                        "test_coverage"
                    ],

                "test_net_sharpe":
                    selected_candidate[
                        "test_net_sharpe"
                    ],
            },
            indent=2,
            sort_keys=True,
        )
    )

    print()
    print("Running five walk-forward folds...")

    fold_ranges = [
        (0.50, 0.60),
        (0.60, 0.70),
        (0.70, 0.80),
        (0.80, 0.90),
        (0.90, 1.00),
    ]

    walk_records = []

    for fold_number, (
        test_start_fraction,
        test_end_fraction,
    ) in enumerate(
        fold_ranges,
        start=1,
    ):
        train_end_index = int(
            len(unique_dates)
            * test_start_fraction
        )

        test_end_index = min(
            int(
                len(unique_dates)
                * test_end_fraction
            ),
            len(unique_dates),
        )

        if (
            train_end_index <= 0
            or test_end_index
            <= train_end_index
        ):
            continue

        fold_train_end = (
            unique_dates[
                train_end_index - 1
            ]
        )

        fold_test_start = (
            unique_dates[
                train_end_index
            ]
        )

        fold_test_end = (
            unique_dates[
                test_end_index - 1
            ]
        )

        fold_train = dataset[
            dataset["timestamp"]
            <= fold_train_end
        ].copy()

        fold_test = dataset[
            (
                dataset["timestamp"]
                >= fold_test_start
            )
            & (
                dataset["timestamp"]
                <= fold_test_end
            )
        ].copy()

        fold_test_scope = scope_frame(
            fold_test,
            selected_scope,
        )

        if (
            len(fold_train) < 5000
            or len(fold_test_scope) < 1000
        ):
            continue

        print(
            f"  fold {fold_number}: "
            f"train={len(fold_train)} "
            f"test={len(fold_test_scope)}"
        )

        fold_model = factories[
            selected_model_name
        ]()

        fold_model.fit(
            fold_train[
                FEATURE_COLUMNS
            ],
            fold_train[
                TARGET_COLUMN
            ],
        )

        fold_probability = (
            probability_one(
                fold_model,
                fold_test_scope[
                    FEATURE_COLUMNS
                ],
            )
        )

        fold_classification = (
            classification_metrics(
                fold_test_scope[
                    TARGET_COLUMN
                ],
                fold_probability,
            )
        )

        fold_strategy = (
            strategy_metrics(
                fold_test_scope,
                fold_probability,
                threshold=
                    selected_threshold,
                mode=selected_mode,
            )
        )

        walk_records.append(
            {
                "fold":
                    fold_number,

                "scope":
                    selected_scope,

                "mode":
                    selected_mode,

                "threshold":
                    selected_threshold,

                "train_start":
                    str(
                        fold_train[
                            "timestamp"
                        ].min()
                    ),

                "train_end":
                    str(
                        fold_train[
                            "timestamp"
                        ].max()
                    ),

                "test_start":
                    str(
                        fold_test_scope[
                            "timestamp"
                        ].min()
                    ),

                "test_end":
                    str(
                        fold_test_scope[
                            "timestamp"
                        ].max()
                    ),

                "training_rows":
                    int(
                        len(fold_train)
                    ),

                "test_rows":
                    int(
                        len(
                            fold_test_scope
                        )
                    ),

                "test_symbols":
                    int(
                        fold_test_scope[
                            "provider_symbol"
                        ].nunique()
                    ),

                "accuracy":
                    fold_classification[
                        "accuracy"
                    ],

                "baseline_accuracy":
                    fold_classification[
                        "baseline_accuracy"
                    ],

                "accuracy_delta":
                    fold_classification[
                        "accuracy_delta"
                    ],

                "roc_auc":
                    fold_classification[
                        "roc_auc"
                    ],

                "trades":
                    fold_strategy[
                        "trades"
                    ],

                "coverage":
                    fold_strategy[
                        "coverage"
                    ],

                "average_daily_positions":
                    fold_strategy[
                        "average_daily_positions"
                    ],

                "net_annualized_return":
                    fold_strategy[
                        "net_annualized_return"
                    ],

                "net_sharpe":
                    fold_strategy[
                        "net_sharpe"
                    ],

                "maximum_drawdown":
                    fold_strategy[
                        "maximum_drawdown"
                    ],

                "transaction_cost_bps":
                    TRANSACTION_COST_BPS,
            }
        )

    walk_frame = pd.DataFrame(
        walk_records
    )

    walk_frame.to_csv(
        walk_path,
        index=False,
    )

    development = dataset[
        dataset["timestamp"]
        < validation_boundary
    ].copy()

    final_model = factories[
        selected_model_name
    ]()

    print()
    print("Fitting final isolated Stage 7S model...")

    final_model.fit(
        development[
            FEATURE_COLUMNS
        ],
        development[
            TARGET_COLUMN
        ],
    )

    artifact = {
        "model":
            final_model,

        "model_name":
            selected_model_name,

        "feature_columns":
            FEATURE_COLUMNS,

        "target_column":
            TARGET_COLUMN,

        "future_return_column":
            RETURN_COLUMN,

        "strategy":
            {
                "candidate_id":
                    selected_candidate[
                        "candidate_id"
                    ],

                "scope":
                    selected_scope,

                "mode":
                    selected_mode,

                "threshold":
                    selected_threshold,

                "transaction_cost_bps":
                    TRANSACTION_COST_BPS,
            },

        "trained_at":
            utc_now(),

        "authorization":
            {
                "runtime_integration":
                    False,

                "model_replacement":
                    False,

                "strategy_promotion":
                    False,

                "paper_execution":
                    False,

                "broker_execution":
                    False,

                "live_execution":
                    False,
            },
    }

    joblib.dump(
        artifact,
        model_path,
    )

    positive_sharpe_folds = (
        int(
            (
                walk_frame[
                    "net_sharpe"
                ]
                > 0.0
            ).sum()
        )
        if not walk_frame.empty
        else 0
    )

    positive_return_folds = (
        int(
            (
                walk_frame[
                    "net_annualized_return"
                ]
                > 0.0
            ).sum()
        )
        if not walk_frame.empty
        else 0
    )

    activity_qualified = bool(
        selected_candidate[
            "validation_eligible"
        ]
    )

    robustness_qualified = bool(
        len(walk_frame) == 5
        and positive_sharpe_folds >= 3
        and positive_return_folds >= 3
    )

    test_qualified = bool(
        selected_candidate[
            "test_trades"
        ]
        >= args.minimum_trades
        and selected_candidate[
            "test_coverage"
        ]
        >= args.minimum_coverage
        and selected_candidate[
            "test_net_sharpe"
        ]
        > 0.0
        and selected_candidate[
            "test_net_annualized_return"
        ]
        > 0.0
    )

    promotion_qualified = bool(
        activity_qualified
        and robustness_qualified
        and test_qualified
    )

    checks = {
        "dataset_loaded":
            bool(len(dataset) > 0),

        "canadian_rows_present":
            bool(
                (
                    dataset["country"]
                    == "CA"
                ).any()
            ),

        "us_rows_present":
            bool(
                (
                    dataset["country"]
                    == "US"
                ).any()
            ),

        "chronological_partitions_isolated":
            bool(
                training["timestamp"].max()
                < validation[
                    "timestamp"
                ].min()
                < test[
                    "timestamp"
                ].min()
            ),

        "all_candidate_combinations_evaluated":
            bool(
                len(candidate_frame)
                == (
                    len(SCOPES)
                    * len(MODES)
                    * len(THRESHOLDS)
                )
            ),

        "selected_candidate_present":
            bool(selected_candidate),

        "five_walk_forward_folds_completed":
            bool(
                len(walk_frame) == 5
            ),

        "isolated_model_persisted":
            bool(
                model_path.is_file()
            ),

        "strategy_not_promoted":
            bool(
                artifact[
                    "authorization"
                ][
                    "strategy_promotion"
                ]
                is False
            ),

        "paper_execution_disabled":
            bool(
                artifact[
                    "authorization"
                ][
                    "paper_execution"
                ]
                is False
            ),

        "broker_execution_disabled":
            bool(
                artifact[
                    "authorization"
                ][
                    "broker_execution"
                ]
                is False
            ),

        "live_execution_disabled":
            bool(
                artifact[
                    "authorization"
                ][
                    "live_execution"
                ]
                is False
            ),
    }

    failed_checks = [
        name
        for name, passed
        in checks.items()
        if not bool(passed)
    ]

    classification = (
        "stage7s_strategy_search_qualified"
        if not failed_checks
        else "stage7s_strategy_search_not_qualified"
    )

    strategy_classification = (
        "promotion_metrics_satisfied_but_not_authorized"
        if promotion_qualified
        else (
            "robust_candidate_found_requires_manual_review"
            if (
                activity_qualified
                and robustness_qualified
            )
            else (
                "candidate_activity_qualified_requires_more_learning"
                if activity_qualified
                else "no_activity_qualified_candidate"
            )
        )
    )

    summary = {
        "dataset_rows":
            int(len(dataset)),

        "symbols":
            int(
                dataset[
                    "provider_symbol"
                ].nunique()
            ),

        "canadian_rows":
            int(
                (
                    dataset["country"]
                    == "CA"
                ).sum()
            ),

        "us_rows":
            int(
                (
                    dataset["country"]
                    == "US"
                ).sum()
            ),

        "training_rows":
            int(len(training)),

        "validation_rows":
            int(len(validation)),

        "test_rows":
            int(len(test)),

        "candidate_count":
            int(
                len(candidate_frame)
            ),

        "eligible_candidate_count":
            int(
                candidate_frame[
                    "validation_eligible"
                ].sum()
            ),

        "selected_candidate_id":
            selected_candidate[
                "candidate_id"
            ],

        "selected_scope":
            selected_scope,

        "selected_mode":
            selected_mode,

        "selected_threshold":
            selected_threshold,

        "validation_trades":
            int(
                selected_candidate[
                    "validation_trades"
                ]
            ),

        "validation_coverage":
            float(
                selected_candidate[
                    "validation_coverage"
                ]
            ),

        "validation_net_sharpe":
            float(
                selected_candidate[
                    "validation_net_sharpe"
                ]
            ),

        "validation_net_annualized_return":
            float(
                selected_candidate[
                    "validation_net_annualized_return"
                ]
            ),

        "test_trades":
            int(
                selected_candidate[
                    "test_trades"
                ]
            ),

        "test_coverage":
            float(
                selected_candidate[
                    "test_coverage"
                ]
            ),

        "test_net_sharpe":
            float(
                selected_candidate[
                    "test_net_sharpe"
                ]
            ),

        "test_net_annualized_return":
            float(
                selected_candidate[
                    "test_net_annualized_return"
                ]
            ),

        "walk_forward_folds":
            int(len(walk_frame)),

        "positive_sharpe_folds":
            positive_sharpe_folds,

        "positive_return_folds":
            positive_return_folds,

        "activity_qualified":
            activity_qualified,

        "robustness_qualified":
            robustness_qualified,

        "test_qualified":
            test_qualified,

        "promotion_metrics_satisfied":
            promotion_qualified,

        "promotion_authorized":
            False,
    }

    selected_payload = {
        "generated_at":
            utc_now(),

        "selection_classification":
            selection_classification,

        "strategy_classification":
            strategy_classification,

        "selected_candidate":
            selected_candidate,

        "walk_forward_summary":
            {
                "folds":
                    int(
                        len(walk_frame)
                    ),

                "positive_sharpe_folds":
                    positive_sharpe_folds,

                "positive_return_folds":
                    positive_return_folds,
            },

        "authorization":
            artifact[
                "authorization"
            ],
    }

    selected_path.write_text(
        json.dumps(
            selected_payload,
            indent=2,
            sort_keys=True,
            allow_nan=False,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )

    result = {
        "objective":
            (
                "Stage 7S Strategy "
                "Threshold Search"
            ),

        "generated_at":
            utc_now(),

        "classification":
            classification,

        "selection_classification":
            selection_classification,

        "strategy_classification":
            strategy_classification,

        "passed":
            not failed_checks,

        "checks":
            checks,

        "failed_checks":
            failed_checks,

        "summary":
            summary,

        "selected_candidate":
            selected_candidate,

        "source":
            {
                "features":
                    str(features_path),

                "features_sha256":
                    sha256_file(
                        features_path
                    ),

                "stage7r_result":
                    str(
                        stage7r_result_path
                    ),

                "stage7r_result_sha256":
                    sha256_file(
                        stage7r_result_path
                    ),
            },

        "artifacts":
            {
                "candidate_csv":
                    str(
                        candidates_path
                    ),

                "walk_forward_csv":
                    str(walk_path),

                "selected_strategy_json":
                    str(
                        selected_path
                    ),

                "isolated_model":
                    str(model_path),

                "isolated_model_sha256":
                    sha256_file(
                        model_path
                    ),
            },

        "authorization":
            artifact[
                "authorization"
            ],

        "safety":
            {
                "repository_model_replaced":
                    False,

                "deployment_modified":
                    False,

                "database_rows_written":
                    False,

                "strategy_promoted":
                    False,

                "paper_orders_created":
                    False,

                "broker_requests":
                    False,

                "live_orders":
                    False,
            },
    }

    result_path.write_text(
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
            allow_nan=False,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )

    report_lines = [
        "=" * 100,
        (
            "NEUROVEST — STAGE 7S "
            "STRATEGY THRESHOLD SEARCH"
        ),
        "=" * 100,
        "",
        (
            "Qualification: "
            + (
                "PASS"
                if result["passed"]
                else "FAILED"
            )
        ),
        "",
        (
            "Classification: "
            + classification
        ),
        "",
        (
            "Selection classification: "
            + selection_classification
        ),
        "",
        (
            "Strategy classification: "
            + strategy_classification
        ),
        "",
        "CHECKS:",
    ]

    for name, passed in checks.items():
        report_lines.append(
            f"  {name:<58} {bool(passed)}"
        )

    report_lines.extend(
        [
            "",
            "SUMMARY:",
            json.dumps(
                summary,
                indent=2,
                sort_keys=True,
            ),
            "",
            "SELECTED CANDIDATE:",
            json.dumps(
                selected_candidate,
                indent=2,
                sort_keys=True,
                default=str,
            ),
            "",
            "No runtime model was replaced.",
            "No strategy was promoted.",
            "No paper orders were created.",
            "No broker requests were made.",
            "No live orders were created.",
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

    print()
    print("=" * 100)
    print(
        "STAGE 7S STRATEGY "
        "THRESHOLD SEARCH COMPLETE"
    )
    print("=" * 100)
    print()
    print(
        json.dumps(
            {
                "passed":
                    result["passed"],

                "classification":
                    classification,

                "selection_classification":
                    selection_classification,

                "strategy_classification":
                    strategy_classification,

                "failed_checks":
                    failed_checks,

                "summary":
                    summary,

                "result":
                    str(result_path),

                "report":
                    str(report_path),
            },
            indent=2,
            sort_keys=True,
            default=str,
        )
    )

    return (
        0
        if result["passed"]
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())

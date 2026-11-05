#!/usr/bin/env python3

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
import argparse
import hashlib
import json
import math
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


BASE_FEATURES = [
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

TARGET = "target_next_up"
FUTURE_RETURN = "future_return_1d"

RANDOM_SEED = 20260803
TRANSACTION_COST_BPS = 10.0
TRANSACTION_COST_RATE = TRANSACTION_COST_BPS / 10000.0

THRESHOLDS = [
    round(value, 2)
    for value in np.arange(
        0.52,
        0.621,
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

MINIMUM_TRADES = 100
MINIMUM_COVERAGE = 0.01


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def probability_one(
    model: Any,
    features: pd.DataFrame,
) -> np.ndarray:
    probability = model.predict_proba(
        features
    )

    classes = getattr(
        model,
        "classes_",
        None,
    )

    if (
        classes is None
        and hasattr(model, "named_steps")
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
        else probability.shape[1] - 1
    )

    return probability[:, index]


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
        target.value_counts().idxmax()
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
        "accuracy":
            accuracy,

        "baseline_accuracy":
            baseline_accuracy,

        "accuracy_delta":
            accuracy - baseline_accuracy,

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
            FUTURE_RETURN,
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
    else:
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
        * working[FUTURE_RETURN]
    )

    working["net_return"] = (
        working["gross_return"]
        - working["turnover"]
        * TRANSACTION_COST_RATE
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
            active_positions=(
                "position",
                lambda values:
                    int(
                        (
                            values != 0.0
                        ).sum()
                    ),
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

        total_return = gross - 1.0

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

    return {
        "trades":
            int(
                (
                    working["turnover"]
                    > 0.0
                ).sum()
            ),

        "coverage":
            float(active.mean()),

        "average_daily_positions":
            float(
                daily[
                    "active_positions"
                ].mean()
            )
            if not daily.empty
            else 0.0,

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
    }


def feature_families(
    dataset: pd.DataFrame,
) -> dict[str, list[str]]:
    epsilon = 1e-8

    dataset[
        "momentum_spread_5_20"
    ] = (
        dataset["return_5d"]
        - dataset["return_20d"]
    )

    dataset[
        "momentum_spread_10_20"
    ] = (
        dataset["return_10d"]
        - dataset["return_20d"]
    )

    dataset[
        "trend_spread_5_20"
    ] = (
        dataset["close_to_sma_5"]
        - dataset["close_to_sma_20"]
    )

    dataset[
        "trend_spread_20_50"
    ] = (
        dataset["close_to_sma_20"]
        - dataset["close_to_sma_50"]
    )

    dataset[
        "volatility_ratio_5_20"
    ] = (
        dataset["volatility_5d"]
        / (
            dataset["volatility_20d"]
            .abs()
            + epsilon
        )
    )

    dataset[
        "risk_adjusted_momentum"
    ] = (
        dataset["return_20d"]
        / (
            dataset["volatility_20d"]
            .abs()
            + epsilon
        )
    )

    dataset[
        "range_volatility_interaction"
    ] = (
        dataset["range_fraction"]
        * dataset["volatility_20d"]
    )

    dataset[
        "volume_return_interaction"
    ] = (
        dataset["volume_change_1d"]
        * dataset["return_1d"]
    )

    rank_sources = [
        "return_5d",
        "return_20d",
        "volatility_20d",
        "range_fraction",
        "volume_ratio_20d",
    ]

    rank_features = []

    for column in rank_sources:
        name = (
            f"cross_section_rank_{column}"
        )

        dataset[name] = (
            dataset.groupby(
                "timestamp",
                sort=False,
            )[column]
            .rank(
                pct=True,
                method="average",
            )
        )

        rank_features.append(name)

    interaction_features = [
        "momentum_spread_5_20",
        "momentum_spread_10_20",
        "trend_spread_5_20",
        "trend_spread_20_50",
        "volatility_ratio_5_20",
        "risk_adjusted_momentum",
        "range_volatility_interaction",
        "volume_return_interaction",
    ]

    return {
        "base":
            list(BASE_FEATURES),

        "base_plus_interactions":
            list(BASE_FEATURES)
            + interaction_features,

        "base_plus_cross_section":
            list(BASE_FEATURES)
            + rank_features,

        "full_evolved":
            list(BASE_FEATURES)
            + interaction_features
            + rank_features,
    }


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
                learning_rate=0.04,
                max_iter=260,
                max_leaf_nodes=31,
                min_samples_leaf=30,
                l2_regularization=1.0,
                random_state=RANDOM_SEED,
            ),

        "random_forest":
            lambda: RandomForestClassifier(
                n_estimators=200,
                max_depth=14,
                min_samples_leaf=15,
                max_features="sqrt",
                class_weight="balanced_subsample",
                n_jobs=-1,
                random_state=RANDOM_SEED,
            ),

        "extra_trees":
            lambda: ExtraTreesClassifier(
                n_estimators=220,
                max_depth=16,
                min_samples_leaf=12,
                max_features="sqrt",
                class_weight="balanced",
                n_jobs=-1,
                random_state=RANDOM_SEED,
            ),
    }


def apply_scope(
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
    feature_family: str,
    scope: str,
    mode: str,
    threshold: float,
) -> str:
    payload = (
        f"{model_name}|"
        f"{feature_family}|"
        f"{scope}|"
        f"{mode}|"
        f"{threshold:.2f}|"
        f"{TRANSACTION_COST_BPS}"
    )

    return (
        "stage7t_candidate_"
        + hashlib.sha256(
            payload.encode("utf-8")
        ).hexdigest()[:20]
    )


def main() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--features",
        required=True,
    )

    parser.add_argument(
        "--stage7s-result",
        required=True,
    )

    parser.add_argument(
        "--stage7s-selected",
        required=True,
    )

    parser.add_argument(
        "--output",
        required=True,
    )

    args = parser.parse_args()

    output_root = Path(args.output)
    output_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    leaderboard_path = (
        output_root
        / "evolution_leaderboard.csv"
    )

    walk_path = (
        output_root
        / "walk_forward.csv"
    )

    selected_path = (
        output_root
        / "selected_candidate.json"
    )

    model_path = (
        output_root
        / "stage7t_selected_model.joblib"
    )

    result_path = (
        output_root
        / "result.json"
    )

    report_path = (
        output_root
        / "report.txt"
    )

    dataset = pd.read_csv(
        args.features,
        low_memory=False,
    )

    stage7s_result = json.loads(
        Path(
            args.stage7s_result
        ).read_text(
            encoding="utf-8"
        )
    )

    stage7s_selected = json.loads(
        Path(
            args.stage7s_selected
        ).read_text(
            encoding="utf-8"
        )
    )

    required = {
        "timestamp",
        "provider_symbol",
        "country",
        TARGET,
        FUTURE_RETURN,
        *BASE_FEATURES,
    }

    missing = sorted(
        required
        - set(dataset.columns)
    )

    if missing:
        raise SystemExit(
            "BLOCKED: missing columns: "
            + ", ".join(missing)
        )

    dataset["timestamp"] = pd.to_datetime(
        dataset["timestamp"],
        errors="coerce",
        utc=True,
    )

    numeric = (
        BASE_FEATURES
        + [
            TARGET,
            FUTURE_RETURN,
        ]
    )

    for column in numeric:
        dataset[column] = pd.to_numeric(
            dataset[column],
            errors="coerce",
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
                *numeric,
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
        .reset_index(drop=True)
    )

    dataset[TARGET] = (
        dataset[TARGET].astype(int)
    )

    families = feature_families(
        dataset
    )

    dataset = dataset.replace(
        [
            np.inf,
            -np.inf,
        ],
        np.nan,
    )

    all_evolved_features = sorted(
        {
            feature
            for values in families.values()
            for feature in values
        }
    )

    dataset = dataset.dropna(
        subset=all_evolved_features
    ).reset_index(drop=True)

    unique_dates = np.array(
        sorted(
            dataset[
                "timestamp"
            ].unique()
        )
    )

    if len(unique_dates) < 300:
        raise SystemExit(
            "BLOCKED: insufficient dates."
        )

    train_boundary = unique_dates[
        int(len(unique_dates) * 0.60)
    ]

    validation_boundary = unique_dates[
        int(len(unique_dates) * 0.80)
    ]

    training = dataset[
        dataset["timestamp"]
        < train_boundary
    ].copy()

    validation = dataset[
        (
            dataset["timestamp"]
            >= train_boundary
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

    if not (
        training["timestamp"].max()
        < validation["timestamp"].min()
        < test["timestamp"].min()
    ):
        raise SystemExit(
            "BLOCKED: chronological overlap."
        )

    factories = model_factories()

    leaderboard_records: list[
        dict[str, Any]
    ] = []

    fitted_models: dict[
        tuple[str, str],
        Any,
    ] = {}

    print()
    print("=" * 100)
    print("STAGE 7T STRATEGY EVOLUTION")
    print("=" * 100)
    print()
    print(
        f"Rows: {len(dataset)}"
    )
    print(
        "Symbols: "
        f"{dataset['provider_symbol'].nunique()}"
    )
    print(
        "Feature families: "
        f"{len(families)}"
    )
    print(
        "Model families: "
        f"{len(factories)}"
    )

    for feature_name, feature_columns in families.items():
        for model_name, factory in factories.items():
            started = time.time()

            print()
            print(
                f"Training {model_name} "
                f"with {feature_name}"
            )

            model = factory()

            model.fit(
                training[feature_columns],
                training[TARGET],
            )

            fitted_models[
                (
                    model_name,
                    feature_name,
                )
            ] = model

            validation_probability = (
                probability_one(
                    model,
                    validation[
                        feature_columns
                    ],
                )
            )

            test_probability = (
                probability_one(
                    model,
                    test[
                        feature_columns
                    ],
                )
            )

            for scope in SCOPES:
                validation_scope = apply_scope(
                    validation,
                    scope,
                )

                test_scope = apply_scope(
                    test,
                    scope,
                )

                if (
                    validation_scope.empty
                    or test_scope.empty
                ):
                    continue

                validation_positions = (
                    validation.index.get_indexer(
                        validation_scope.index
                    )
                )

                test_positions = (
                    test.index.get_indexer(
                        test_scope.index
                    )
                )

                scoped_validation_probability = (
                    validation_probability[
                        validation_positions
                    ]
                )

                scoped_test_probability = (
                    test_probability[
                        test_positions
                    ]
                )

                validation_classification = (
                    classification_metrics(
                        validation_scope[TARGET],
                        scoped_validation_probability,
                    )
                )

                test_classification = (
                    classification_metrics(
                        test_scope[TARGET],
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

                        eligible = bool(
                            validation_strategy[
                                "trades"
                            ]
                            >= MINIMUM_TRADES
                            and validation_strategy[
                                "coverage"
                            ]
                            >= MINIMUM_COVERAGE
                        )

                        validation_score = (
                            validation_strategy[
                                "net_sharpe"
                            ]
                            + 0.25
                            * validation_strategy[
                                "net_annualized_return"
                            ]
                            + 0.10
                            * validation_classification[
                                "accuracy_delta"
                            ]
                            - 0.10
                            * abs(
                                validation_strategy[
                                    "maximum_drawdown"
                                ]
                            )
                        )

                        leaderboard_records.append(
                            {
                                "candidate_id":
                                    candidate_id(
                                        model_name=
                                            model_name,

                                        feature_family=
                                            feature_name,

                                        scope=
                                            scope,

                                        mode=
                                            mode,

                                        threshold=
                                            threshold,
                                    ),

                                "model_name":
                                    model_name,

                                "feature_family":
                                    feature_name,

                                "feature_count":
                                    len(
                                        feature_columns
                                    ),

                                "scope":
                                    scope,

                                "mode":
                                    mode,

                                "threshold":
                                    threshold,

                                "validation_eligible":
                                    eligible,

                                "validation_score":
                                    validation_score,

                                "validation_trades":
                                    validation_strategy[
                                        "trades"
                                    ],

                                "validation_coverage":
                                    validation_strategy[
                                        "coverage"
                                    ],

                                "validation_accuracy_delta":
                                    validation_classification[
                                        "accuracy_delta"
                                    ],

                                "validation_roc_auc":
                                    validation_classification[
                                        "roc_auc"
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

                                "test_trades":
                                    test_strategy[
                                        "trades"
                                    ],

                                "test_coverage":
                                    test_strategy[
                                        "coverage"
                                    ],

                                "test_accuracy_delta":
                                    test_classification[
                                        "accuracy_delta"
                                    ],

                                "test_roc_auc":
                                    test_classification[
                                        "roc_auc"
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

                                "training_seconds":
                                    time.time()
                                    - started,

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

    leaderboard = pd.DataFrame(
        leaderboard_records
    )

    if leaderboard.empty:
        raise SystemExit(
            "BLOCKED: no candidates generated."
        )

    eligible = leaderboard[
        leaderboard[
            "validation_eligible"
        ]
        == True
    ].copy()

    if eligible.empty:
        raise SystemExit(
            "BLOCKED: no candidate met "
            "minimum activity."
        )

    leaderboard = (
        leaderboard.sort_values(
            by=[
                "validation_eligible",
                "validation_score",
                "validation_net_sharpe",
                "validation_net_annualized_return",
                "validation_trades",
            ],
            ascending=[
                False,
                False,
                False,
                False,
                False,
            ],
            kind="stable",
        )
        .reset_index(drop=True)
    )

    leaderboard.insert(
        0,
        "rank",
        range(
            1,
            len(leaderboard) + 1,
        ),
    )

    leaderboard.to_csv(
        leaderboard_path,
        index=False,
    )

    selected_row = (
        eligible.sort_values(
            by=[
                "validation_score",
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
        .iloc[0]
    )

    selected = {
        key:
            (
                value.item()
                if hasattr(value, "item")
                else value
            )
        for key, value
        in selected_row.to_dict().items()
    }

    selected_model_name = str(
        selected["model_name"]
    )

    selected_feature_family = str(
        selected["feature_family"]
    )

    selected_scope = str(
        selected["scope"]
    )

    selected_mode = str(
        selected["mode"]
    )

    selected_threshold = float(
        selected["threshold"]
    )

    selected_features = families[
        selected_feature_family
    ]

    walk_records = []

    fold_ranges = [
        (0.50, 0.60),
        (0.60, 0.70),
        (0.70, 0.80),
        (0.80, 0.90),
        (0.90, 1.00),
    ]

    print()
    print("Selected candidate:")
    print(
        json.dumps(
            selected,
            indent=2,
            sort_keys=True,
            default=str,
        )
    )

    print()
    print("Running walk-forward evolution proof...")

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

        fold_test_scope = apply_scope(
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
                selected_features
            ],
            fold_train[TARGET],
        )

        fold_probability = (
            probability_one(
                fold_model,
                fold_test_scope[
                    selected_features
                ],
            )
        )

        fold_classification = (
            classification_metrics(
                fold_test_scope[TARGET],
                fold_probability,
            )
        )

        fold_strategy = (
            strategy_metrics(
                fold_test_scope,
                fold_probability,
                threshold=
                    selected_threshold,
                mode=
                    selected_mode,
            )
        )

        walk_records.append(
            {
                "fold":
                    fold_number,

                "training_rows":
                    len(fold_train),

                "test_rows":
                    len(fold_test_scope),

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
            }
        )

    walk = pd.DataFrame(
        walk_records
    )

    walk.to_csv(
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

    final_model.fit(
        development[
            selected_features
        ],
        development[TARGET],
    )

    artifact = {
        "model":
            final_model,

        "model_name":
            selected_model_name,

        "feature_family":
            selected_feature_family,

        "feature_columns":
            selected_features,

        "target_column":
            TARGET,

        "future_return_column":
            FUTURE_RETURN,

        "strategy":
            {
                "candidate_id":
                    selected[
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
                walk["net_sharpe"]
                > 0.0
            ).sum()
        )
        if not walk.empty
        else 0
    )

    positive_return_folds = (
        int(
            (
                walk[
                    "net_annualized_return"
                ]
                > 0.0
            ).sum()
        )
        if not walk.empty
        else 0
    )

    test_qualified = bool(
        selected["test_trades"]
        >= MINIMUM_TRADES
        and selected["test_coverage"]
        >= MINIMUM_COVERAGE
        and selected[
            "test_net_sharpe"
        ]
        > 0.0
        and selected[
            "test_net_annualized_return"
        ]
        > 0.0
    )

    walk_forward_qualified = bool(
        len(walk) == 5
        and positive_sharpe_folds >= 3
        and positive_return_folds >= 3
    )

    improvement_over_stage7s = bool(
        selected[
            "test_net_sharpe"
        ]
        > float(
            stage7s_result.get(
                "summary",
                {},
            ).get(
                "test_net_sharpe",
                0.0,
            )
        )
    )

    checks = {
        "dataset_loaded":
            bool(len(dataset) > 0),

        "four_feature_families_evaluated":
            bool(len(families) == 4),

        "four_model_families_evaluated":
            bool(len(factories) == 4),

        "all_candidates_generated":
            bool(
                len(leaderboard)
                == (
                    len(families)
                    * len(factories)
                    * len(SCOPES)
                    * len(MODES)
                    * len(THRESHOLDS)
                )
            ),

        "selected_candidate_present":
            bool(selected),

        "five_walk_forward_folds":
            bool(len(walk) == 5),

        "isolated_model_persisted":
            bool(model_path.is_file()),

        "strategy_not_promoted":
            True,

        "paper_execution_disabled":
            True,

        "broker_execution_disabled":
            True,

        "live_execution_disabled":
            True,
    }

    failed_checks = [
        name
        for name, passed
        in checks.items()
        if not bool(passed)
    ]

    classification = (
        "stage7t_strategy_evolution_qualified"
        if not failed_checks
        else "stage7t_strategy_evolution_failed"
    )

    strategy_classification = (
        "evolved_candidate_metrics_satisfied_but_not_authorized"
        if (
            test_qualified
            and walk_forward_qualified
        )
        else (
            "evolved_candidate_improved_requires_more_learning"
            if improvement_over_stage7s
            else "evolution_completed_without_robust_improvement"
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

        "feature_families":
            len(families),

        "model_families":
            len(factories),

        "candidate_count":
            int(len(leaderboard)),

        "eligible_candidates":
            int(
                leaderboard[
                    "validation_eligible"
                ].sum()
            ),

        "selected_candidate_id":
            selected["candidate_id"],

        "selected_model":
            selected_model_name,

        "selected_feature_family":
            selected_feature_family,

        "selected_feature_count":
            len(selected_features),

        "selected_scope":
            selected_scope,

        "selected_mode":
            selected_mode,

        "selected_threshold":
            selected_threshold,

        "validation_trades":
            int(
                selected[
                    "validation_trades"
                ]
            ),

        "validation_coverage":
            float(
                selected[
                    "validation_coverage"
                ]
            ),

        "validation_net_sharpe":
            float(
                selected[
                    "validation_net_sharpe"
                ]
            ),

        "validation_net_annualized_return":
            float(
                selected[
                    "validation_net_annualized_return"
                ]
            ),

        "test_trades":
            int(
                selected[
                    "test_trades"
                ]
            ),

        "test_coverage":
            float(
                selected[
                    "test_coverage"
                ]
            ),

        "test_net_sharpe":
            float(
                selected[
                    "test_net_sharpe"
                ]
            ),

        "test_net_annualized_return":
            float(
                selected[
                    "test_net_annualized_return"
                ]
            ),

        "walk_forward_folds":
            int(len(walk)),

        "positive_sharpe_folds":
            positive_sharpe_folds,

        "positive_return_folds":
            positive_return_folds,

        "test_qualified":
            test_qualified,

        "walk_forward_qualified":
            walk_forward_qualified,

        "improved_over_stage7s_test_sharpe":
            improvement_over_stage7s,

        "promotion_authorized":
            False,
    }

    selected_payload = {
        "generated_at":
            utc_now(),

        "classification":
            strategy_classification,

        "selected_candidate":
            selected,

        "selected_features":
            selected_features,

        "walk_forward":
            walk_records,

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
            "Stage 7T Strategy Evolution",

        "generated_at":
            utc_now(),

        "classification":
            classification,

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
            selected,

        "source":
            {
                "features":
                    args.features,

                "features_sha256":
                    sha256_file(
                        Path(args.features)
                    ),

                "stage7s_result":
                    args.stage7s_result,

                "stage7s_selected":
                    args.stage7s_selected,
            },

        "artifacts":
            {
                "leaderboard":
                    str(
                        leaderboard_path
                    ),

                "walk_forward":
                    str(walk_path),

                "selected_candidate":
                    str(selected_path),

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
                "runtime_model_replaced":
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
        "NEUROVEST — STAGE 7T STRATEGY EVOLUTION",
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
                selected,
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
        "\n".join(report_lines)
        + "\n",
        encoding="utf-8",
    )

    print()
    print("=" * 100)
    print("STAGE 7T STRATEGY EVOLUTION COMPLETE")
    print("=" * 100)
    print()
    print(
        json.dumps(
            {
                "passed":
                    result["passed"],

                "classification":
                    classification,

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

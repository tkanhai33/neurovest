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
    0.52,
    0.53,
    0.54,
    0.55,
    0.56,
    0.57,
    0.58,
    0.59,
    0.60,
]

SCOPES = (
    "CA",
    "US",
    "ALL",
)

MODES = (
    "long_only",
    "long_short",
)

MINIMUM_TRADES = 100
MINIMUM_COVERAGE = 0.01
MAXIMUM_TOP_FIVE_SHARE = 0.70


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
                            max_iter=1200,
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


def add_evolved_features(
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
            dataset[
                "volatility_20d"
            ].abs()
            + epsilon
        )
    )

    dataset[
        "risk_adjusted_momentum"
    ] = (
        dataset["return_20d"]
        / (
            dataset[
                "volatility_20d"
            ].abs()
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
            "cross_section_rank_"
            + column
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
    cleaned = (
        returns.replace(
            [np.inf, -np.inf],
            np.nan,
        )
        .dropna()
        .astype(float)
    )

    if cleaned.empty:
        return 0.0

    equity = (
        1.0
        + cleaned
    ).cumprod()

    drawdown = (
        equity
        / equity.cummax()
        - 1.0
    )

    return float(
        drawdown.min()
    )


def performance_metrics(
    returns: pd.Series,
) -> dict[str, Any]:
    cleaned = (
        returns.replace(
            [np.inf, -np.inf],
            np.nan,
        )
        .dropna()
        .astype(float)
    )

    if cleaned.empty:
        return {
            "days": 0,
            "total_return": 0.0,
            "annualized_return": 0.0,
            "annualized_volatility": 0.0,
            "sharpe": 0.0,
            "maximum_drawdown": 0.0,
        }

    gross = float(
        (
            1.0
            + cleaned
        ).prod()
    )

    total_return = gross - 1.0

    annualized_return = 0.0

    if gross > 0.0:
        annualized_return = float(
            gross
            ** (
                252.0
                / len(cleaned)
            )
            - 1.0
        )

    annualized_volatility = 0.0

    if len(cleaned) > 1:
        annualized_volatility = float(
            cleaned.std(
                ddof=1
            )
            * math.sqrt(252.0)
        )

    sharpe = 0.0

    if annualized_volatility > 0.0:
        sharpe = (
            annualized_return
            / annualized_volatility
        )

    return {
        "days":
            int(len(cleaned)),

        "total_return":
            float(total_return),

        "annualized_return":
            float(annualized_return),

        "annualized_volatility":
            float(
                annualized_volatility
            ),

        "sharpe":
            float(sharpe),

        "maximum_drawdown":
            maximum_drawdown(
                cleaned
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


def evaluate_strategy(
    frame: pd.DataFrame,
    probability: np.ndarray,
    *,
    threshold: float,
    mode: str,
) -> tuple[
    dict[str, Any],
    pd.DataFrame,
    pd.DataFrame,
]:
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

    working["cost"] = (
        working["turnover"]
        * TRANSACTION_COST_RATE
    )

    working["net_return"] = (
        working["gross_return"]
        - working["cost"]
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

    contributions = (
        working.groupby(
            "provider_symbol",
            sort=True,
        )
        .agg(
            net_return_sum=(
                "net_return",
                "sum",
            ),
            gross_return_sum=(
                "gross_return",
                "sum",
            ),
            active_rows=(
                "position",
                lambda values:
                    int(
                        (
                            values != 0.0
                        ).sum()
                    ),
            ),
            trades=(
                "turnover",
                lambda values:
                    int(
                        (
                            values > 0.0
                        ).sum()
                    ),
            ),
        )
        .reset_index()
        .sort_values(
            "net_return_sum",
            ascending=False,
            kind="stable",
        )
    )

    absolute_total = max(
        float(
            contributions[
                "net_return_sum"
            ].abs().sum()
        ),
        1e-12,
    )

    contributions[
        "absolute_contribution_share"
    ] = (
        contributions[
            "net_return_sum"
        ].abs()
        / absolute_total
    )

    metrics = performance_metrics(
        daily["net_return"]
    )

    active = (
        working["position"]
        != 0.0
    )

    metrics.update(
        {
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

            "top_1_contribution_share":
                float(
                    contributions[
                        "absolute_contribution_share"
                    ].head(1).sum()
                ),

            "top_5_contribution_share":
                float(
                    contributions[
                        "absolute_contribution_share"
                    ].head(5).sum()
                ),

            "top_10_contribution_share":
                float(
                    contributions[
                        "absolute_contribution_share"
                    ].head(10).sum()
                ),
        }
    )

    top_five = set(
        contributions[
            "provider_symbol"
        ].head(5)
    )

    reduced = working[
        ~working[
            "provider_symbol"
        ].isin(top_five)
    ].copy()

    reduced_daily = (
        reduced.groupby(
            "timestamp",
            sort=True,
        )["net_return"]
        .mean()
    )

    reduced_metrics = performance_metrics(
        reduced_daily
    )

    metrics.update(
        {
            "without_top_five_annualized_return":
                reduced_metrics[
                    "annualized_return"
                ],

            "without_top_five_sharpe":
                reduced_metrics[
                    "sharpe"
                ],

            "without_top_five_maximum_drawdown":
                reduced_metrics[
                    "maximum_drawdown"
                ],
        }
    )

    return (
        metrics,
        daily,
        contributions,
    )


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
        f"{TRANSACTION_COST_BPS}|"
        f"{RANDOM_SEED}"
    )

    return (
        "stage7w_candidate_"
        + hashlib.sha256(
            payload.encode(
                "utf-8"
            )
        ).hexdigest()[:20]
    )


def main() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--features",
        required=True,
    )

    parser.add_argument(
        "--stage7v-result",
        required=True,
    )

    parser.add_argument(
        "--output",
        required=True,
    )

    args = parser.parse_args()

    output_root = Path(
        args.output
    )

    output_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    result_path = (
        output_root
        / "result.json"
    )

    leaderboard_path = (
        output_root
        / "candidate_leaderboard.csv"
    )

    walk_path = (
        output_root
        / "walk_forward.csv"
    )

    contribution_path = (
        output_root
        / (
            "confirmation_"
            "symbol_contributions.csv"
        )
    )

    selected_path = (
        output_root
        / "selected_candidate.json"
    )

    model_path = (
        output_root
        / "stage7w_selected_model.joblib"
    )

    report_path = (
        output_root
        / "report.txt"
    )

    stage7v = json.loads(
        Path(
            args.stage7v_result
        ).read_text(
            encoding="utf-8"
        )
    )

    if (
        stage7v.get(
            "strategy_classification"
        )
        != "contribution_dependence_not_remediated"
    ):
        raise SystemExit(
            "BLOCKED: Stage 7V did not record "
            "the expected unresolved concentration failure."
        )

    dataset = pd.read_csv(
        args.features,
        low_memory=False,
    )

    required_base = {
        "timestamp",
        "provider_symbol",
        "country",
        TARGET,
        FUTURE_RETURN,
        *BASE_FEATURES,
    }

    missing_base = sorted(
        required_base
        - set(dataset.columns)
    )

    if missing_base:
        raise SystemExit(
            "BLOCKED: required base columns missing: "
            + ", ".join(
                missing_base
            )
        )

    dataset["timestamp"] = (
        pd.to_datetime(
            dataset["timestamp"],
            errors="coerce",
            utc=True,
        )
    )

    for column in (
        BASE_FEATURES
        + [
            TARGET,
            FUTURE_RETURN,
        ]
    ):
        dataset[column] = (
            pd.to_numeric(
                dataset[column],
                errors="coerce",
            )
        )

    dataset = (
        dataset.replace(
            [np.inf, -np.inf],
            np.nan,
        )
        .dropna(
            subset=[
                "timestamp",
                "provider_symbol",
                "country",
                TARGET,
                FUTURE_RETURN,
                *BASE_FEATURES,
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

    dataset[TARGET] = (
        dataset[TARGET].astype(int)
    )

    feature_families = (
        add_evolved_features(
            dataset
        )
    )

    all_features = sorted(
        {
            feature
            for family
            in feature_families.values()
            for feature in family
        }
    )

    dataset = (
        dataset.replace(
            [np.inf, -np.inf],
            np.nan,
        )
        .dropna(
            subset=all_features
        )
        .reset_index(
            drop=True
        )
    )

    unique_dates = np.array(
        sorted(
            dataset[
                "timestamp"
            ].unique()
        )
    )

    if len(unique_dates) < 300:
        raise SystemExit(
            "BLOCKED: insufficient trading dates."
        )

    training_boundary = unique_dates[
        int(
            len(unique_dates)
            * 0.60
        )
    ]

    confirmation_boundary = unique_dates[
        int(
            len(unique_dates)
            * 0.80
        )
    ]

    training = dataset[
        dataset["timestamp"]
        < training_boundary
    ].copy()

    remediation = dataset[
        (
            dataset["timestamp"]
            >= training_boundary
        )
        & (
            dataset["timestamp"]
            < confirmation_boundary
        )
    ].copy()

    confirmation = dataset[
        dataset["timestamp"]
        >= confirmation_boundary
    ].copy()

    if not (
        training[
            "timestamp"
        ].max()
        < remediation[
            "timestamp"
        ].min()
        <= remediation[
            "timestamp"
        ].max()
        < confirmation[
            "timestamp"
        ].min()
    ):
        raise SystemExit(
            "BLOCKED: chronological partitions overlap."
        )

    factories = model_factories()

    candidate_records = []
    trained_models = {}

    print()
    print("=" * 100)
    print(
        "STAGE 7W CONCENTRATION-AWARE "
        "CANDIDATE EVOLUTION"
    )
    print("=" * 100)
    print()
    print(
        f"Dataset rows: {len(dataset)}"
    )
    print(
        "Symbols: "
        f"{dataset['provider_symbol'].nunique()}"
    )
    print(
        f"Training rows: {len(training)}"
    )
    print(
        f"Remediation rows: {len(remediation)}"
    )
    print(
        f"Confirmation rows: {len(confirmation)}"
    )

    for feature_name, feature_columns in (
        feature_families.items()
    ):
        for model_name, factory in (
            factories.items()
        ):
            started = time.time()

            print()
            print(
                f"Training {model_name} "
                f"with {feature_name}"
            )

            model = factory()

            model.fit(
                training[
                    feature_columns
                ],
                training[TARGET],
            )

            trained_models[
                (
                    model_name,
                    feature_name,
                )
            ] = model

            remediation_probability = (
                probability_one(
                    model,
                    remediation[
                        feature_columns
                    ],
                )
            )

            for scope in SCOPES:
                scoped = apply_scope(
                    remediation,
                    scope,
                )

                if scoped.empty:
                    continue

                positions = (
                    remediation.index
                    .get_indexer(
                        scoped.index
                    )
                )

                scoped_probability = (
                    remediation_probability[
                        positions
                    ]
                )

                classification = (
                    classification_metrics(
                        scoped[TARGET],
                        scoped_probability,
                    )
                )

                for mode in MODES:
                    for threshold in THRESHOLDS:
                        (
                            strategy,
                            _,
                            _,
                        ) = evaluate_strategy(
                            scoped,
                            scoped_probability,
                            threshold=threshold,
                            mode=mode,
                        )

                        activity_qualified = bool(
                            strategy[
                                "trades"
                            ]
                            >= MINIMUM_TRADES
                            and strategy[
                                "coverage"
                            ]
                            >= MINIMUM_COVERAGE
                        )

                        concentration_qualified = bool(
                            strategy[
                                "top_5_contribution_share"
                            ]
                            < MAXIMUM_TOP_FIVE_SHARE
                        )

                        removal_qualified = bool(
                            strategy[
                                (
                                    "without_top_five_"
                                    "annualized_return"
                                )
                            ]
                            > 0.0
                            and strategy[
                                (
                                    "without_top_five_"
                                    "sharpe"
                                )
                            ]
                            > 0.0
                        )

                        remediation_eligible = bool(
                            activity_qualified
                            and concentration_qualified
                            and removal_qualified
                            and strategy[
                                "annualized_return"
                            ]
                            > 0.0
                            and strategy[
                                "sharpe"
                            ]
                            > 0.0
                        )

                        concentration_penalty = (
                            1.50
                            * strategy[
                                "top_5_contribution_share"
                            ]
                        )

                        removal_bonus = (
                            0.50
                            * max(
                                strategy[
                                    (
                                        "without_top_five_"
                                        "sharpe"
                                    )
                                ],
                                -5.0,
                            )
                        )

                        score = (
                            strategy[
                                "sharpe"
                            ]
                            + 0.25
                            * strategy[
                                "annualized_return"
                            ]
                            + 0.10
                            * classification[
                                "roc_auc"
                            ]
                            + removal_bonus
                            - concentration_penalty
                            - 0.10
                            * abs(
                                strategy[
                                    "maximum_drawdown"
                                ]
                            )
                        )

                        candidate_records.append(
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

                                "remediation_eligible":
                                    remediation_eligible,

                                "activity_qualified":
                                    activity_qualified,

                                "concentration_qualified":
                                    concentration_qualified,

                                "top_five_removal_qualified":
                                    removal_qualified,

                                "remediation_score":
                                    score,

                                "remediation_accuracy_delta":
                                    classification[
                                        "accuracy_delta"
                                    ],

                                "remediation_roc_auc":
                                    classification[
                                        "roc_auc"
                                    ],

                                "remediation_trades":
                                    strategy[
                                        "trades"
                                    ],

                                "remediation_coverage":
                                    strategy[
                                        "coverage"
                                    ],

                                "remediation_annualized_return":
                                    strategy[
                                        "annualized_return"
                                    ],

                                "remediation_sharpe":
                                    strategy[
                                        "sharpe"
                                    ],

                                "remediation_maximum_drawdown":
                                    strategy[
                                        "maximum_drawdown"
                                    ],

                                "remediation_top_1_share":
                                    strategy[
                                        "top_1_contribution_share"
                                    ],

                                "remediation_top_5_share":
                                    strategy[
                                        "top_5_contribution_share"
                                    ],

                                "remediation_top_10_share":
                                    strategy[
                                        "top_10_contribution_share"
                                    ],

                                "remediation_without_top_five_return":
                                    strategy[
                                        (
                                            "without_top_five_"
                                            "annualized_return"
                                        )
                                    ],

                                "remediation_without_top_five_sharpe":
                                    strategy[
                                        (
                                            "without_top_five_"
                                            "sharpe"
                                        )
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
        candidate_records
    )

    if leaderboard.empty:
        raise SystemExit(
            "BLOCKED: no candidates generated."
        )

    eligible = leaderboard[
        leaderboard[
            "remediation_eligible"
        ]
        == True
    ].copy()

    if eligible.empty:
        selected_row = (
            leaderboard.sort_values(
                by=[
                    "remediation_score",
                    "remediation_sharpe",
                    (
                        "remediation_without_"
                        "top_five_sharpe"
                    ),
                ],
                ascending=[
                    False,
                    False,
                    False,
                ],
                kind="stable",
            )
            .iloc[0]
        )

        selection_classification = (
            "no_concentration_qualified_candidate"
        )

    else:
        selected_row = (
            eligible.sort_values(
                by=[
                    "remediation_score",
                    (
                        "remediation_without_"
                        "top_five_sharpe"
                    ),
                    "remediation_sharpe",
                ],
                ascending=[
                    False,
                    False,
                    False,
                ],
                kind="stable",
            )
            .iloc[0]
        )

        selection_classification = (
            "concentration_qualified_candidate_selected"
        )

    selected = {
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

    leaderboard = (
        leaderboard.sort_values(
            by=[
                "remediation_eligible",
                "remediation_score",
                (
                    "remediation_without_"
                    "top_five_sharpe"
                ),
                "remediation_sharpe",
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

    selected_features = feature_families[
        selected_feature_family
    ]

    selected_model = trained_models[
        (
            selected_model_name,
            selected_feature_family,
        )
    ]

    confirmation_scope = apply_scope(
        confirmation,
        selected_scope,
    )

    confirmation_probability = (
        probability_one(
            selected_model,
            confirmation_scope[
                selected_features
            ],
        )
    )

    (
        confirmation_metrics,
        _,
        confirmation_contributions,
    ) = evaluate_strategy(
        confirmation_scope,
        confirmation_probability,
        threshold=selected_threshold,
        mode=selected_mode,
    )

    confirmation_contributions.to_csv(
        contribution_path,
        index=False,
    )

    confirmation_checks = {
        "confirmation_activity_qualified":
            bool(
                confirmation_metrics[
                    "trades"
                ]
                >= MINIMUM_TRADES
                and confirmation_metrics[
                    "coverage"
                ]
                >= MINIMUM_COVERAGE
            ),

        "confirmation_positive_return":
            bool(
                confirmation_metrics[
                    "annualized_return"
                ]
                > 0.0
            ),

        "confirmation_positive_sharpe":
            bool(
                confirmation_metrics[
                    "sharpe"
                ]
                > 0.0
            ),

        "confirmation_top_five_share_below_70_percent":
            bool(
                confirmation_metrics[
                    "top_5_contribution_share"
                ]
                < MAXIMUM_TOP_FIVE_SHARE
            ),

        "confirmation_positive_after_top_five_removal":
            bool(
                confirmation_metrics[
                    (
                        "without_top_five_"
                        "annualized_return"
                    )
                ]
                > 0.0
                and confirmation_metrics[
                    (
                        "without_top_five_"
                        "sharpe"
                    )
                ]
                > 0.0
            ),
    }

    failed_confirmation_checks = [
        name
        for name, passed
        in confirmation_checks.items()
        if not bool(passed)
    ]

    confirmation_qualified = bool(
        not failed_confirmation_checks
    )

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
    print("Running concentration-aware walk-forward proof...")

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

        fold_test = apply_scope(
            fold_test,
            selected_scope,
        )

        if (
            len(fold_train) < 5000
            or len(fold_test) < 1000
        ):
            continue

        print(
            f"  fold {fold_number}: "
            f"train={len(fold_train)} "
            f"test={len(fold_test)}"
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
                fold_test[
                    selected_features
                ],
            )
        )

        (
            fold_metrics,
            _,
            _,
        ) = evaluate_strategy(
            fold_test,
            fold_probability,
            threshold=selected_threshold,
            mode=selected_mode,
        )

        walk_records.append(
            {
                "fold":
                    fold_number,

                "training_rows":
                    int(
                        len(fold_train)
                    ),

                "test_rows":
                    int(
                        len(fold_test)
                    ),

                "trades":
                    fold_metrics[
                        "trades"
                    ],

                "coverage":
                    fold_metrics[
                        "coverage"
                    ],

                "annualized_return":
                    fold_metrics[
                        "annualized_return"
                    ],

                "sharpe":
                    fold_metrics[
                        "sharpe"
                    ],

                "maximum_drawdown":
                    fold_metrics[
                        "maximum_drawdown"
                    ],

                "top_5_contribution_share":
                    fold_metrics[
                        "top_5_contribution_share"
                    ],

                "without_top_five_annualized_return":
                    fold_metrics[
                        (
                            "without_top_five_"
                            "annualized_return"
                        )
                    ],

                "without_top_five_sharpe":
                    fold_metrics[
                        (
                            "without_top_five_"
                            "sharpe"
                        )
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

    positive_sharpe_folds = (
        int(
            (
                walk["sharpe"]
                > 0.0
            ).sum()
        )
        if not walk.empty
        else 0
    )

    positive_without_top_five_folds = (
        int(
            (
                walk[
                    (
                        "without_top_five_"
                        "sharpe"
                    )
                ]
                > 0.0
            ).sum()
        )
        if not walk.empty
        else 0
    )

    concentration_qualified_folds = (
        int(
            (
                walk[
                    "top_5_contribution_share"
                ]
                < MAXIMUM_TOP_FIVE_SHARE
            ).sum()
        )
        if not walk.empty
        else 0
    )

    walk_forward_qualified = bool(
        len(walk) == 5
        and positive_sharpe_folds >= 3
        and positive_without_top_five_folds >= 3
        and concentration_qualified_folds >= 3
    )

    development = dataset[
        dataset["timestamp"]
        < confirmation_boundary
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

        "strategy": {
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

            "maximum_top_five_contribution_share":
                MAXIMUM_TOP_FIVE_SHARE,

            "top_five_removal_required":
                True,
        },

        "trained_at":
            utc_now(),

        "authorization": {
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

    checks = {
        "dataset_loaded":
            bool(len(dataset) > 0),

        "four_feature_families_evaluated":
            bool(
                len(
                    feature_families
                )
                == 4
            ),

        "four_model_families_evaluated":
            bool(
                len(factories) == 4
            ),

        "all_candidate_combinations_evaluated":
            bool(
                len(leaderboard)
                == (
                    len(
                        feature_families
                    )
                    * len(factories)
                    * len(SCOPES)
                    * len(MODES)
                    * len(THRESHOLDS)
                )
            ),

        "candidate_selected_using_remediation_only":
            True,

        "confirmation_not_used_for_selection":
            True,

        "five_walk_forward_folds_completed":
            bool(
                len(walk) == 5
            ),

        "isolated_model_persisted":
            bool(
                model_path.is_file()
            ),

        "runtime_model_not_replaced":
            True,

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

    stage_passed = bool(
        not failed_checks
    )

    promotion_metrics_satisfied = bool(
        selected[
            "remediation_eligible"
        ]
        and confirmation_qualified
        and walk_forward_qualified
    )

    classification = (
        (
            "stage7w_concentration_aware_"
            "candidate_evolution_qualified"
        )
        if stage_passed
        else (
            "stage7w_concentration_aware_"
            "candidate_evolution_failed"
        )
    )

    strategy_classification = (
        (
            "concentration_robust_candidate_"
            "confirmed_but_not_authorized"
        )
        if promotion_metrics_satisfied
        else (
            "concentration_aware_learning_"
            "completed_without_robust_candidate"
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

        "training_rows":
            int(len(training)),

        "remediation_rows":
            int(len(remediation)),

        "confirmation_rows":
            int(len(confirmation)),

        "candidate_count":
            int(len(leaderboard)),

        "eligible_candidate_count":
            int(
                leaderboard[
                    "remediation_eligible"
                ].sum()
            ),

        "selected_candidate_id":
            selected[
                "candidate_id"
            ],

        "selected_model":
            selected_model_name,

        "selected_feature_family":
            selected_feature_family,

        "selected_scope":
            selected_scope,

        "selected_mode":
            selected_mode,

        "selected_threshold":
            selected_threshold,

        "remediation_trades":
            int(
                selected[
                    "remediation_trades"
                ]
            ),

        "remediation_sharpe":
            float(
                selected[
                    "remediation_sharpe"
                ]
            ),

        "remediation_annualized_return":
            float(
                selected[
                    (
                        "remediation_"
                        "annualized_return"
                    )
                ]
            ),

        "remediation_top_5_share":
            float(
                selected[
                    "remediation_top_5_share"
                ]
            ),

        "remediation_without_top_five_sharpe":
            float(
                selected[
                    (
                        "remediation_without_"
                        "top_five_sharpe"
                    )
                ]
            ),

        "confirmation_trades":
            int(
                confirmation_metrics[
                    "trades"
                ]
            ),

        "confirmation_coverage":
            float(
                confirmation_metrics[
                    "coverage"
                ]
            ),

        "confirmation_sharpe":
            float(
                confirmation_metrics[
                    "sharpe"
                ]
            ),

        "confirmation_annualized_return":
            float(
                confirmation_metrics[
                    "annualized_return"
                ]
            ),

        "confirmation_top_5_share":
            float(
                confirmation_metrics[
                    "top_5_contribution_share"
                ]
            ),

        "confirmation_without_top_five_sharpe":
            float(
                confirmation_metrics[
                    (
                        "without_top_five_"
                        "sharpe"
                    )
                ]
            ),

        "confirmation_without_top_five_annualized_return":
            float(
                confirmation_metrics[
                    (
                        "without_top_five_"
                        "annualized_return"
                    )
                ]
            ),

        "confirmation_qualified":
            confirmation_qualified,

        "failed_confirmation_checks":
            failed_confirmation_checks,

        "walk_forward_folds":
            int(len(walk)),

        "positive_sharpe_folds":
            positive_sharpe_folds,

        "positive_without_top_five_folds":
            positive_without_top_five_folds,

        "concentration_qualified_folds":
            concentration_qualified_folds,

        "walk_forward_qualified":
            walk_forward_qualified,

        "promotion_metrics_satisfied":
            promotion_metrics_satisfied,

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
            selected,

        "selected_features":
            selected_features,

        "confirmation_metrics":
            confirmation_metrics,

        "confirmation_checks":
            confirmation_checks,

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
            (
                "Stage 7W Concentration-Aware "
                "Candidate Evolution"
            ),

        "generated_at":
            utc_now(),

        "classification":
            classification,

        "strategy_classification":
            strategy_classification,

        "passed":
            stage_passed,

        "confirmation_qualified":
            confirmation_qualified,

        "walk_forward_qualified":
            walk_forward_qualified,

        "promotion_metrics_satisfied":
            promotion_metrics_satisfied,

        "checks":
            checks,

        "confirmation_checks":
            confirmation_checks,

        "failed_checks":
            failed_checks,

        "failed_confirmation_checks":
            failed_confirmation_checks,

        "summary":
            summary,

        "selected_candidate":
            selected,

        "confirmation_metrics":
            confirmation_metrics,

        "source": {
            "features":
                args.features,

            "features_sha256":
                sha256_file(
                    Path(
                        args.features
                    )
                ),

            "stage7v_result":
                args.stage7v_result,

            "stage7v_result_sha256":
                sha256_file(
                    Path(
                        args.stage7v_result
                    )
                ),
        },

        "artifacts": {
            "leaderboard":
                str(
                    leaderboard_path
                ),

            "walk_forward":
                str(walk_path),

            "confirmation_contributions":
                str(
                    contribution_path
                ),

            "selected_candidate":
                str(selected_path),

            "isolated_model":
                str(model_path),

            "isolated_model_sha256":
                sha256_file(
                    model_path
                ),
        },

        "authorization": {
            "continue_isolated_learning":
                True,

            "runtime_model_replacement":
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

        "safety": {
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
        (
            "NEUROVEST — STAGE 7W "
            "CONCENTRATION-AWARE CANDIDATE EVOLUTION"
        ),
        "=" * 100,
        "",
        (
            "Stage qualification: "
            + (
                "PASS"
                if stage_passed
                else "FAILED"
            )
        ),
        "",
        (
            "Confirmation qualification: "
            + (
                "PASS"
                if confirmation_qualified
                else "FAILED"
            )
        ),
        "",
        (
            "Walk-forward qualification: "
            + (
                "PASS"
                if walk_forward_qualified
                else "FAILED"
            )
        ),
        "",
        f"Classification: {classification}",
        (
            "Strategy classification: "
            + strategy_classification
        ),
        "",
        "CHECKS:",
    ]

    for name, passed in checks.items():
        report_lines.append(
            f"  {name:<68} {bool(passed)}"
        )

    report_lines.extend(
        [
            "",
            "CONFIRMATION CHECKS:",
        ]
    )

    for name, passed in (
        confirmation_checks.items()
    ):
        report_lines.append(
            f"  {name:<68} {bool(passed)}"
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
            (
                "Candidate selection included a "
                "top-five concentration penalty."
            ),
            (
                "Candidates were required to remain "
                "positive after removal of their "
                "five strongest contributors."
            ),
            (
                "The confirmation partition was not "
                "used for candidate selection."
            ),
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
    print(
        "STAGE 7W CONCENTRATION-AWARE "
        "CANDIDATE EVOLUTION COMPLETE"
    )
    print("=" * 100)
    print()
    print(
        json.dumps(
            {
                "passed":
                    stage_passed,

                "confirmation_qualified":
                    confirmation_qualified,

                "walk_forward_qualified":
                    walk_forward_qualified,

                "promotion_metrics_satisfied":
                    promotion_metrics_satisfied,

                "classification":
                    classification,

                "strategy_classification":
                    strategy_classification,

                "failed_checks":
                    failed_checks,

                "failed_confirmation_checks":
                    failed_confirmation_checks,

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
        if stage_passed
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())

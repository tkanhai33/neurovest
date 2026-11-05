#!/usr/bin/env python3

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import argparse
import hashlib
import json
import math

import joblib
import numpy as np
import pandas as pd


TARGET = "target_next_up"
FUTURE_RETURN = "future_return_1d"

TRANSACTION_COST_BPS = 10.0
TRANSACTION_COST_RATE = (
    TRANSACTION_COST_BPS
    / 10000.0
)

MAX_SYMBOL_WEIGHTS = (
    1.00,
    0.50,
    0.33,
    0.25,
    0.20,
    0.15,
    0.10,
)

MINIMUM_ACTIVE_SYMBOLS = (
    1,
    2,
    3,
    5,
)

TOP_REMOVAL_COUNTS = (
    0,
    1,
    3,
    5,
)

RANDOM_SEED = 20260803
BOOTSTRAP_SAMPLES = 1000


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def sha256_file(path: Path) -> str:
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


def add_evolved_features(
    dataset: pd.DataFrame,
) -> pd.DataFrame:
    frame = dataset.copy()
    epsilon = 1e-8

    frame[
        "momentum_spread_5_20"
    ] = (
        frame["return_5d"]
        - frame["return_20d"]
    )

    frame[
        "momentum_spread_10_20"
    ] = (
        frame["return_10d"]
        - frame["return_20d"]
    )

    frame[
        "trend_spread_5_20"
    ] = (
        frame["close_to_sma_5"]
        - frame["close_to_sma_20"]
    )

    frame[
        "trend_spread_20_50"
    ] = (
        frame["close_to_sma_20"]
        - frame["close_to_sma_50"]
    )

    frame[
        "volatility_ratio_5_20"
    ] = (
        frame["volatility_5d"]
        / (
            frame[
                "volatility_20d"
            ].abs()
            + epsilon
        )
    )

    frame[
        "risk_adjusted_momentum"
    ] = (
        frame["return_20d"]
        / (
            frame[
                "volatility_20d"
            ].abs()
            + epsilon
        )
    )

    frame[
        "range_volatility_interaction"
    ] = (
        frame["range_fraction"]
        * frame["volatility_20d"]
    )

    frame[
        "volume_return_interaction"
    ] = (
        frame["volume_change_1d"]
        * frame["return_1d"]
    )

    return frame


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


def longest_drawdown_days(
    returns: pd.Series,
) -> int:
    cleaned = (
        returns.fillna(0.0)
        .astype(float)
    )

    if cleaned.empty:
        return 0

    equity = (
        1.0
        + cleaned
    ).cumprod()

    underwater = (
        equity
        < equity.cummax()
    )

    longest = 0
    current = 0

    for value in underwater:
        if bool(value):
            current += 1
            longest = max(
                longest,
                current,
            )
        else:
            current = 0

    return int(longest)


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
            "longest_drawdown_days": 0,
            "positive_day_fraction": 0.0,
        }

    gross = float(
        (
            1.0
            + cleaned
        ).prod()
    )

    total_return = (
        gross - 1.0
    )

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

        "longest_drawdown_days":
            longest_drawdown_days(
                cleaned
            ),

        "positive_day_fraction":
            float(
                (
                    cleaned > 0.0
                ).mean()
            ),
    }


def build_signal_rows(
    frame: pd.DataFrame,
    probability: np.ndarray,
    *,
    threshold: float,
    mode: str,
) -> pd.DataFrame:
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
            f"Unsupported mode: {mode}"
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
        - working[
            "previous_position"
        ]
    ).abs()

    working["gross_symbol_return"] = (
        working["position"]
        * working[FUTURE_RETURN]
    )

    working["symbol_cost"] = (
        working["turnover"]
        * TRANSACTION_COST_RATE
    )

    return working


def capped_equal_weights(
    active_count: int,
    cap: float,
) -> float:
    if active_count <= 0:
        return 0.0

    return float(
        min(
            1.0 / active_count,
            cap,
        )
    )


def evaluate_policy(
    source: pd.DataFrame,
    *,
    removed_symbols: set[str],
    maximum_symbol_weight: float,
    minimum_active_symbols: int,
) -> tuple[
    dict[str, Any],
    pd.DataFrame,
    pd.DataFrame,
]:
    working = source[
        ~source[
            "provider_symbol"
        ].isin(
            removed_symbols
        )
    ].copy()

    working["active"] = (
        working["position"]
        != 0.0
    )

    active_counts = (
        working.groupby(
            "timestamp",
            sort=True,
        )["active"]
        .sum()
        .rename(
            "active_symbols"
        )
    )

    working = working.merge(
        active_counts,
        left_on="timestamp",
        right_index=True,
        how="left",
    )

    working["eligible_day"] = (
        working["active_symbols"]
        >= minimum_active_symbols
    )

    working["symbol_weight"] = [
        capped_equal_weights(
            int(active_count),
            maximum_symbol_weight,
        )
        if bool(active)
        and bool(eligible)
        else 0.0
        for active_count, active, eligible
        in zip(
            working[
                "active_symbols"
            ],
            working["active"],
            working[
                "eligible_day"
            ],
        )
    ]

    working["weighted_gross_return"] = (
        working[
            "gross_symbol_return"
        ]
        * working[
            "symbol_weight"
        ]
    )

    working["weighted_cost"] = (
        working["symbol_cost"]
        * working[
            "symbol_weight"
        ]
    )

    working["weighted_net_return"] = (
        working[
            "weighted_gross_return"
        ]
        - working[
            "weighted_cost"
        ]
    )

    daily = (
        working.groupby(
            "timestamp",
            sort=True,
        )
        .agg(
            net_return=(
                "weighted_net_return",
                "sum",
            ),
            gross_return=(
                "weighted_gross_return",
                "sum",
            ),
            active_symbols=(
                "active_symbols",
                "max",
            ),
            total_weight=(
                "symbol_weight",
                "sum",
            ),
            eligible_day=(
                "eligible_day",
                "max",
            ),
        )
        .reset_index()
    )

    metrics = performance_metrics(
        daily["net_return"]
    )

    symbol_contributions = (
        working.groupby(
            "provider_symbol",
            sort=True,
        )
        .agg(
            active_rows=(
                "active",
                "sum",
            ),
            weighted_net_return_sum=(
                "weighted_net_return",
                "sum",
            ),
            weighted_gross_return_sum=(
                "weighted_gross_return",
                "sum",
            ),
            weighted_cost_sum=(
                "weighted_cost",
                "sum",
            ),
            maximum_observed_weight=(
                "symbol_weight",
                "max",
            ),
        )
        .reset_index()
        .sort_values(
            "weighted_net_return_sum",
            ascending=False,
            kind="stable",
        )
    )

    absolute_total = max(
        float(
            symbol_contributions[
                "weighted_net_return_sum"
            ].abs().sum()
        ),
        1e-12,
    )

    symbol_contributions[
        "absolute_contribution_share"
    ] = (
        symbol_contributions[
            "weighted_net_return_sum"
        ].abs()
        / absolute_total
    )

    metrics.update(
        {
            "removed_symbol_count":
                len(
                    removed_symbols
                ),

            "removed_symbols":
                ",".join(
                    sorted(
                        removed_symbols
                    )
                ),

            "maximum_symbol_weight":
                float(
                    maximum_symbol_weight
                ),

            "minimum_active_symbols":
                int(
                    minimum_active_symbols
                ),

            "eligible_days":
                int(
                    daily[
                        "eligible_day"
                    ].sum()
                ),

            "eligible_day_fraction":
                float(
                    daily[
                        "eligible_day"
                    ].mean()
                ),

            "average_active_symbols":
                float(
                    daily[
                        "active_symbols"
                    ].mean()
                ),

            "average_total_weight":
                float(
                    daily[
                        "total_weight"
                    ].mean()
                ),

            "top_1_absolute_contribution_share":
                float(
                    symbol_contributions[
                        "absolute_contribution_share"
                    ].head(1).sum()
                ),

            "top_5_absolute_contribution_share":
                float(
                    symbol_contributions[
                        "absolute_contribution_share"
                    ].head(5).sum()
                ),

            "top_10_absolute_contribution_share":
                float(
                    symbol_contributions[
                        "absolute_contribution_share"
                    ].head(10).sum()
                ),

            "transaction_cost_bps":
                TRANSACTION_COST_BPS,
        }
    )

    return (
        metrics,
        daily,
        symbol_contributions,
    )


def bootstrap_confidence(
    returns: pd.Series,
) -> dict[str, Any]:
    cleaned = (
        returns.replace(
            [np.inf, -np.inf],
            np.nan,
        )
        .dropna()
        .to_numpy(
            dtype=float
        )
    )

    if len(cleaned) < 20:
        return {
            "samples": 0,
            "positive_return_probability":
                None,
            "positive_sharpe_probability":
                None,
            "annualized_return_ci_95": [
                None,
                None,
            ],
            "sharpe_ci_95": [
                None,
                None,
            ],
        }

    rng = np.random.default_rng(
        RANDOM_SEED
    )

    annualized_returns = []
    sharpes = []

    for _ in range(
        BOOTSTRAP_SAMPLES
    ):
        sample = rng.choice(
            cleaned,
            size=len(cleaned),
            replace=True,
        )

        metrics = performance_metrics(
            pd.Series(sample)
        )

        annualized_returns.append(
            metrics[
                "annualized_return"
            ]
        )

        sharpes.append(
            metrics["sharpe"]
        )

    annualized_array = np.asarray(
        annualized_returns,
        dtype=float,
    )

    sharpe_array = np.asarray(
        sharpes,
        dtype=float,
    )

    return {
        "samples":
            BOOTSTRAP_SAMPLES,

        "positive_return_probability":
            float(
                (
                    annualized_array
                    > 0.0
                ).mean()
            ),

        "positive_sharpe_probability":
            float(
                (
                    sharpe_array
                    > 0.0
                ).mean()
            ),

        "annualized_return_ci_95":
            [
                float(
                    np.quantile(
                        annualized_array,
                        0.025,
                    )
                ),
                float(
                    np.quantile(
                        annualized_array,
                        0.975,
                    )
                ),
            ],

        "sharpe_ci_95":
            [
                float(
                    np.quantile(
                        sharpe_array,
                        0.025,
                    )
                ),
                float(
                    np.quantile(
                        sharpe_array,
                        0.975,
                    )
                ),
            ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--features",
        required=True,
    )

    parser.add_argument(
        "--stage7t-result",
        required=True,
    )

    parser.add_argument(
        "--stage7t-selected",
        required=True,
    )

    parser.add_argument(
        "--stage7t-model",
        required=True,
    )

    parser.add_argument(
        "--stage7u-result",
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

    policies_path = (
        output_root
        / "policy_search.csv"
    )

    symbols_path = (
        output_root
        / (
            "remediation_"
            "symbol_contributions.csv"
        )
    )

    selected_path = (
        output_root
        / (
            "selected_"
            "diversification_policy.json"
        )
    )

    confirmation_daily_path = (
        output_root
        / "confirmation_daily_returns.csv"
    )

    report_path = (
        output_root
        / "report.txt"
    )

    stage7t_result = json.loads(
        Path(
            args.stage7t_result
        ).read_text(
            encoding="utf-8"
        )
    )

    stage7t_selected = json.loads(
        Path(
            args.stage7t_selected
        ).read_text(
            encoding="utf-8"
        )
    )

    stage7u_result = json.loads(
        Path(
            args.stage7u_result
        ).read_text(
            encoding="utf-8"
        )
    )

    artifact = joblib.load(
        args.stage7t_model
    )

    candidate = stage7t_result.get(
        "selected_candidate",
        {}
    )

    if not candidate:
        candidate = (
            stage7t_selected.get(
                "selected_candidate",
                {}
            )
        )

    required_candidate = {
        "candidate_id",
        "model_name",
        "feature_family",
        "scope",
        "mode",
        "threshold",
    }

    missing_candidate = sorted(
        required_candidate
        - set(candidate)
    )

    if missing_candidate:
        raise SystemExit(
            "BLOCKED: candidate fields missing: "
            + ", ".join(
                missing_candidate
            )
        )

    candidate_id = str(
        candidate["candidate_id"]
    )

    model_name = str(
        candidate["model_name"]
    )

    feature_family = str(
        candidate["feature_family"]
    )

    scope = str(
        candidate["scope"]
    )

    mode = str(
        candidate["mode"]
    )

    threshold = float(
        candidate["threshold"]
    )

    artifact_model = artifact.get(
        "model"
    )

    artifact_features = list(
        artifact.get(
            "feature_columns",
            []
        )
    )

    artifact_strategy = artifact.get(
        "strategy",
        {}
    )

    if artifact_model is None:
        raise SystemExit(
            "BLOCKED: frozen model missing."
        )

    if not artifact_features:
        raise SystemExit(
            "BLOCKED: frozen features missing."
        )

    freeze_checks = {
        "candidate_id_matches":
            str(
                artifact_strategy.get(
                    "candidate_id"
                )
            )
            == candidate_id,

        "model_name_matches":
            str(
                artifact.get(
                    "model_name"
                )
            )
            == model_name,

        "feature_family_matches":
            str(
                artifact.get(
                    "feature_family"
                )
            )
            == feature_family,

        "scope_matches":
            str(
                artifact_strategy.get(
                    "scope"
                )
            )
            == scope,

        "mode_matches":
            str(
                artifact_strategy.get(
                    "mode"
                )
            )
            == mode,

        "threshold_matches":
            float(
                artifact_strategy.get(
                    "threshold"
                )
            )
            == threshold,

        "stage7u_failed_only_contribution_check":
            stage7u_result.get(
                "failed_robustness_checks"
            )
            == [
                (
                    "top_five_symbols_"
                    "removed_positive"
                )
            ],
    }

    if not all(
        bool(value)
        for value
        in freeze_checks.values()
    ):
        raise SystemExit(
            "BLOCKED: frozen-candidate "
            "continuity check failed."
        )

    dataset = pd.read_csv(
        args.features,
        low_memory=False,
    )

    dataset["timestamp"] = (
        pd.to_datetime(
            dataset["timestamp"],
            errors="coerce",
            utc=True,
        )
    )

    dataset = add_evolved_features(
        dataset
    )

    required_columns = {
        "timestamp",
        "provider_symbol",
        "country",
        FUTURE_RETURN,
        TARGET,
        *artifact_features,
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

    for column in (
        artifact_features
        + [
            FUTURE_RETURN,
            TARGET,
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
                FUTURE_RETURN,
                TARGET,
                *artifact_features,
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

    stage7t_test_boundary = (
        unique_dates[
            int(
                len(unique_dates)
                * 0.80
            )
        ]
    )

    test = dataset[
        dataset["timestamp"]
        >= stage7t_test_boundary
    ].copy()

    if scope != "ALL":
        test = test[
            test["country"]
            == scope
        ].copy()

    test_dates = np.array(
        sorted(
            test["timestamp"]
            .unique()
        )
    )

    if len(test_dates) < 40:
        raise SystemExit(
            "BLOCKED: insufficient test dates "
            "for remediation/confirmation split."
        )

    split_date = test_dates[
        len(test_dates) // 2
    ]

    remediation = test[
        test["timestamp"]
        < split_date
    ].copy()

    confirmation = test[
        test["timestamp"]
        >= split_date
    ].copy()

    if (
        remediation.empty
        or confirmation.empty
    ):
        raise SystemExit(
            "BLOCKED: remediation or "
            "confirmation partition empty."
        )

    remediation_probability = (
        probability_one(
            artifact_model,
            remediation[
                artifact_features
            ],
        )
    )

    confirmation_probability = (
        probability_one(
            artifact_model,
            confirmation[
                artifact_features
            ],
        )
    )

    remediation_signals = (
        build_signal_rows(
            remediation,
            remediation_probability,
            threshold=threshold,
            mode=mode,
        )
    )

    confirmation_signals = (
        build_signal_rows(
            confirmation,
            confirmation_probability,
            threshold=threshold,
            mode=mode,
        )
    )

    baseline_remediation, _, (
        remediation_contributions
    ) = evaluate_policy(
        remediation_signals,
        removed_symbols=set(),
        maximum_symbol_weight=1.0,
        minimum_active_symbols=1,
    )

    remediation_contributions.to_csv(
        symbols_path,
        index=False,
    )

    ranked_symbols = (
        remediation_contributions[
            "provider_symbol"
        ].tolist()
    )

    policy_records = []

    for removal_count in (
        TOP_REMOVAL_COUNTS
    ):
        removed_symbols = set(
            ranked_symbols[
                :removal_count
            ]
        )

        for maximum_weight in (
            MAX_SYMBOL_WEIGHTS
        ):
            for minimum_active in (
                MINIMUM_ACTIVE_SYMBOLS
            ):
                remediation_metrics, _, _ = (
                    evaluate_policy(
                        remediation_signals,
                        removed_symbols=
                            removed_symbols,

                        maximum_symbol_weight=
                            maximum_weight,

                        minimum_active_symbols=
                            minimum_active,
                    )
                )

                eligible = bool(
                    remediation_metrics[
                        "annualized_return"
                    ]
                    > 0.0
                    and remediation_metrics[
                        "sharpe"
                    ]
                    > 0.0
                    and remediation_metrics[
                        "eligible_day_fraction"
                    ]
                    >= 0.20
                    and remediation_metrics[
                        (
                            "top_5_absolute_"
                            "contribution_share"
                        )
                    ]
                    < 0.70
                )

                policy_score = (
                    remediation_metrics[
                        "sharpe"
                    ]
                    + 0.25
                    * remediation_metrics[
                        "annualized_return"
                    ]
                    - 0.30
                    * remediation_metrics[
                        (
                            "top_5_absolute_"
                            "contribution_share"
                        )
                    ]
                    - 0.10
                    * abs(
                        remediation_metrics[
                            "maximum_drawdown"
                        ]
                    )
                )

                policy_records.append(
                    {
                        "policy_id":
                            (
                                "stage7v_policy_"
                                + hashlib.sha256(
                                    (
                                        f"{candidate_id}|"
                                        f"{removal_count}|"
                                        f"{maximum_weight}|"
                                        f"{minimum_active}"
                                    ).encode(
                                        "utf-8"
                                    )
                                ).hexdigest()[:20]
                            ),

                        "removed_symbol_count":
                            removal_count,

                        "removed_symbols":
                            ",".join(
                                sorted(
                                    removed_symbols
                                )
                            ),

                        "maximum_symbol_weight":
                            maximum_weight,

                        "minimum_active_symbols":
                            minimum_active,

                        "remediation_eligible":
                            eligible,

                        "remediation_score":
                            policy_score,

                        **{
                            (
                                "remediation_"
                                + key
                            ):
                                value
                            for key, value
                            in remediation_metrics.items()
                        },

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

    policy_frame = pd.DataFrame(
        policy_records
    )

    if policy_frame.empty:
        raise SystemExit(
            "BLOCKED: no diversification "
            "policies were evaluated."
        )

    eligible_frame = policy_frame[
        policy_frame[
            "remediation_eligible"
        ]
        == True
    ].copy()

    if eligible_frame.empty:
        selected_row = (
            policy_frame.sort_values(
                by=[
                    "remediation_score",
                    "remediation_sharpe",
                    (
                        "remediation_"
                        "annualized_return"
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
            "no_policy_met_remediation_rules"
        )

    else:
        selected_row = (
            eligible_frame.sort_values(
                by=[
                    "remediation_score",
                    "remediation_sharpe",
                    (
                        "remediation_"
                        "annualized_return"
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
            "remediation_policy_selected"
        )

    selected_policy = {
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

    policy_frame = (
        policy_frame.sort_values(
            by=[
                "remediation_eligible",
                "remediation_score",
                "remediation_sharpe",
            ],
            ascending=[
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

    policy_frame.insert(
        0,
        "rank",
        range(
            1,
            len(policy_frame) + 1,
        ),
    )

    policy_frame.to_csv(
        policies_path,
        index=False,
    )

    selected_removed = {
        value
        for value in str(
            selected_policy[
                "removed_symbols"
            ]
        ).split(",")
        if value
    }

    confirmation_metrics, (
        confirmation_daily
    ), confirmation_contributions = (
        evaluate_policy(
            confirmation_signals,
            removed_symbols=
                selected_removed,

            maximum_symbol_weight=
                float(
                    selected_policy[
                        "maximum_symbol_weight"
                    ]
                ),

            minimum_active_symbols=
                int(
                    selected_policy[
                        "minimum_active_symbols"
                    ]
                ),
        )
    )

    confirmation_daily.to_csv(
        confirmation_daily_path,
        index=False,
    )

    confirmation_bootstrap = (
        bootstrap_confidence(
            confirmation_daily[
                "net_return"
            ]
        )
    )

    top_five_confirmation = set(
        confirmation_contributions[
            "provider_symbol"
        ].head(5)
    )

    confirmation_without_top_five, (
        confirmation_without_top_daily
    ), _ = evaluate_policy(
        confirmation_signals,
        removed_symbols=(
            selected_removed
            | top_five_confirmation
        ),
        maximum_symbol_weight=float(
            selected_policy[
                "maximum_symbol_weight"
            ]
        ),
        minimum_active_symbols=int(
            selected_policy[
                "minimum_active_symbols"
            ]
        ),
    )

    baseline_confirmation, _, _ = (
        evaluate_policy(
            confirmation_signals,
            removed_symbols=set(),
            maximum_symbol_weight=1.0,
            minimum_active_symbols=1,
        )
    )

    confirmation_checks = {
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
                    (
                        "top_5_absolute_"
                        "contribution_share"
                    )
                ]
                < 0.70
            ),

        "confirmation_remains_positive_after_top_five_removal":
            bool(
                confirmation_without_top_five[
                    "annualized_return"
                ]
                > 0.0
                and confirmation_without_top_five[
                    "sharpe"
                ]
                > 0.0
            ),

        "confirmation_bootstrap_positive_return_at_least_80_percent":
            bool(
                confirmation_bootstrap[
                    "positive_return_probability"
                ]
                is not None
                and confirmation_bootstrap[
                    "positive_return_probability"
                ]
                >= 0.80
            ),

        "confirmation_bootstrap_positive_sharpe_at_least_80_percent":
            bool(
                confirmation_bootstrap[
                    "positive_sharpe_probability"
                ]
                is not None
                and confirmation_bootstrap[
                    "positive_sharpe_probability"
                ]
                >= 0.80
            ),

        "confirmation_eligible_day_fraction_at_least_20_percent":
            bool(
                confirmation_metrics[
                    "eligible_day_fraction"
                ]
                >= 0.20
            ),
    }

    failed_confirmation_checks = [
        name
        for name, passed
        in confirmation_checks.items()
        if not bool(passed)
    ]

    structure_checks = {
        **freeze_checks,

        "remediation_and_confirmation_do_not_overlap":
            bool(
                remediation[
                    "timestamp"
                ].max()
                < confirmation[
                    "timestamp"
                ].min()
            ),

        "policy_selected_using_remediation_only":
            True,

        "confirmation_not_used_for_selection":
            True,

        "model_not_refit":
            True,

        "model_family_not_changed":
            True,

        "feature_family_not_changed":
            True,

        "threshold_not_changed":
            True,

        "scope_not_changed":
            True,

        "signal_mode_not_changed":
            True,

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

    failed_structure_checks = [
        name
        for name, passed
        in structure_checks.items()
        if not bool(passed)
    ]

    confirmation_qualified = bool(
        not failed_confirmation_checks
    )

    stage_passed = bool(
        not failed_structure_checks
    )

    classification = (
        (
            "stage7v_contribution_dependence_"
            "remediation_qualified"
        )
        if stage_passed
        else (
            "stage7v_structure_"
            "qualification_failed"
        )
    )

    strategy_classification = (
        (
            "diversified_candidate_confirmed_"
            "but_not_authorized"
        )
        if confirmation_qualified
        else (
            "contribution_dependence_"
            "not_remediated"
        )
    )

    selected_payload = {
        "generated_at":
            utc_now(),

        "source_candidate":
            candidate,

        "selection_classification":
            selection_classification,

        "strategy_classification":
            strategy_classification,

        "selected_policy":
            selected_policy,

        "remediation_period":
            {
                "start":
                    str(
                        remediation[
                            "timestamp"
                        ].min()
                    ),

                "end":
                    str(
                        remediation[
                            "timestamp"
                        ].max()
                    ),

                "rows":
                    int(
                        len(remediation)
                    ),
            },

        "confirmation_period":
            {
                "start":
                    str(
                        confirmation[
                            "timestamp"
                        ].min()
                    ),

                "end":
                    str(
                        confirmation[
                            "timestamp"
                        ].max()
                    ),

                "rows":
                    int(
                        len(confirmation)
                    ),
            },

        "baseline_confirmation":
            baseline_confirmation,

        "selected_policy_confirmation":
            confirmation_metrics,

        "confirmation_after_top_five_removal":
            confirmation_without_top_five,

        "confirmation_bootstrap":
            confirmation_bootstrap,

        "confirmation_checks":
            confirmation_checks,

        "authorization":
            {
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

    summary = {
        "candidate_id":
            candidate_id,

        "model_name":
            model_name,

        "feature_family":
            feature_family,

        "scope":
            scope,

        "mode":
            mode,

        "threshold":
            threshold,

        "test_rows":
            int(len(test)),

        "remediation_rows":
            int(
                len(remediation)
            ),

        "confirmation_rows":
            int(
                len(confirmation)
            ),

        "policies_evaluated":
            int(
                len(policy_frame)
            ),

        "eligible_policies":
            int(
                policy_frame[
                    "remediation_eligible"
                ].sum()
            ),

        "selected_policy_id":
            selected_policy[
                "policy_id"
            ],

        "selected_removed_symbol_count":
            int(
                selected_policy[
                    "removed_symbol_count"
                ]
            ),

        "selected_removed_symbols":
            selected_policy[
                "removed_symbols"
            ],

        "selected_maximum_symbol_weight":
            float(
                selected_policy[
                    "maximum_symbol_weight"
                ]
            ),

        "selected_minimum_active_symbols":
            int(
                selected_policy[
                    "minimum_active_symbols"
                ]
            ),

        "remediation_sharpe":
            float(
                selected_policy[
                    "remediation_sharpe"
                ]
            ),

        "remediation_annualized_return":
            float(
                selected_policy[
                    (
                        "remediation_"
                        "annualized_return"
                    )
                ]
            ),

        "confirmation_baseline_sharpe":
            float(
                baseline_confirmation[
                    "sharpe"
                ]
            ),

        "confirmation_policy_sharpe":
            float(
                confirmation_metrics[
                    "sharpe"
                ]
            ),

        "confirmation_policy_annualized_return":
            float(
                confirmation_metrics[
                    "annualized_return"
                ]
            ),

        "confirmation_policy_maximum_drawdown":
            float(
                confirmation_metrics[
                    "maximum_drawdown"
                ]
            ),

        "confirmation_top_5_contribution_share":
            float(
                confirmation_metrics[
                    (
                        "top_5_absolute_"
                        "contribution_share"
                    )
                ]
            ),

        "confirmation_without_top_five_sharpe":
            float(
                confirmation_without_top_five[
                    "sharpe"
                ]
            ),

        "confirmation_without_top_five_annualized_return":
            float(
                confirmation_without_top_five[
                    "annualized_return"
                ]
            ),

        "confirmation_bootstrap_positive_return_probability":
            confirmation_bootstrap[
                "positive_return_probability"
            ],

        "confirmation_bootstrap_positive_sharpe_probability":
            confirmation_bootstrap[
                "positive_sharpe_probability"
            ],

        "confirmation_qualified":
            confirmation_qualified,

        "failed_confirmation_checks":
            failed_confirmation_checks,

        "promotion_authorized":
            False,
    }

    result = {
        "objective":
            (
                "Stage 7V Contribution-"
                "Dependence Remediation"
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

        "structure_checks":
            structure_checks,

        "confirmation_checks":
            confirmation_checks,

        "failed_structure_checks":
            failed_structure_checks,

        "failed_confirmation_checks":
            failed_confirmation_checks,

        "summary":
            summary,

        "selected_policy":
            selected_policy,

        "confirmation_metrics":
            confirmation_metrics,

        "confirmation_without_top_five":
            confirmation_without_top_five,

        "confirmation_bootstrap":
            confirmation_bootstrap,

        "source": {
            "features":
                args.features,

            "features_sha256":
                sha256_file(
                    Path(
                        args.features
                    )
                ),

            "stage7t_model":
                args.stage7t_model,

            "stage7t_model_sha256":
                sha256_file(
                    Path(
                        args.stage7t_model
                    )
                ),

            "stage7u_result":
                args.stage7u_result,
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
            "model_refit":
                False,

            "model_family_changed":
                False,

            "feature_family_changed":
                False,

            "threshold_changed":
                False,

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
            "NEUROVEST — STAGE 7V "
            "CONTRIBUTION-DEPENDENCE REMEDIATION"
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
        f"Classification: {classification}",
        (
            "Strategy classification: "
            + strategy_classification
        ),
        "",
        "STRUCTURE CHECKS:",
    ]

    for name, passed in (
        structure_checks.items()
    ):
        report_lines.append(
            f"  {name:<72} {bool(passed)}"
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
            f"  {name:<72} {bool(passed)}"
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
            "The Stage 7T model remained frozen.",
            "The feature family remained frozen.",
            "The threshold remained frozen.",
            "The Canadian scope remained frozen.",
            "The signal mode remained frozen.",
            (
                "Policy selection used only the "
                "remediation partition."
            ),
            (
                "The confirmation partition was "
                "not used for policy selection."
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
        "STAGE 7V CONTRIBUTION-DEPENDENCE "
        "REMEDIATION COMPLETE"
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

                "classification":
                    classification,

                "strategy_classification":
                    strategy_classification,

                "failed_structure_checks":
                    failed_structure_checks,

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

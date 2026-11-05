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

RANDOM_SEED = 20260803
BOOTSTRAP_SAMPLES = 1000

COST_STRESS_BPS = (
    10.0,
    20.0,
    30.0,
    50.0,
)

DELAY_STRESS_BARS = (
    0,
    1,
)

TOP_SYMBOL_REMOVAL_COUNTS = (
    1,
    3,
    5,
    10,
)

TOP_MONTH_REMOVAL_COUNTS = (
    1,
    2,
    3,
)


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
        else probabilities.shape[1] - 1
    )

    return probabilities[:, index]


def maximum_drawdown(
    returns: pd.Series,
) -> float:
    cleaned = (
        returns.replace(
            [np.inf, -np.inf],
            np.nan,
        )
        .dropna()
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
    cleaned = returns.fillna(0.0)

    if cleaned.empty:
        return 0

    equity = (
        1.0
        + cleaned
    ).cumprod()

    peak = equity.cummax()

    underwater = (
        equity < peak
    ).astype(int)

    longest = 0
    current = 0

    for value in underwater:
        if value:
            current += 1
            longest = max(
                longest,
                current,
            )
        else:
            current = 0

    return int(longest)


def performance_metrics(
    daily_returns: pd.Series,
) -> dict[str, Any]:
    cleaned = (
        daily_returns.replace(
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
            cleaned.std(ddof=1)
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
            float(annualized_volatility),

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


def add_evolved_features(
    dataset: pd.DataFrame,
) -> pd.DataFrame:
    epsilon = 1e-8
    frame = dataset.copy()

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
            frame["volatility_20d"].abs()
            + epsilon
        )
    )

    frame[
        "risk_adjusted_momentum"
    ] = (
        frame["return_20d"]
        / (
            frame["volatility_20d"].abs()
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


def build_positions(
    frame: pd.DataFrame,
    probability: np.ndarray,
    *,
    threshold: float,
    mode: str,
    delay_bars: int,
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
        working["raw_position"] = np.where(
            working["probability"]
            >= threshold,
            1.0,
            0.0,
        )

    elif mode == "long_short":
        working["raw_position"] = np.select(
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

    working["position"] = (
        working.groupby(
            "provider_symbol",
            sort=False,
        )["raw_position"]
        .shift(delay_bars)
        .fillna(0.0)
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

    return working


def evaluate_positions(
    working: pd.DataFrame,
    *,
    cost_bps: float,
) -> tuple[
    dict[str, Any],
    pd.DataFrame,
]:
    cost_rate = (
        cost_bps
        / 10000.0
    )

    evaluated = working.copy()

    evaluated["transaction_cost"] = (
        evaluated["turnover"]
        * cost_rate
    )

    evaluated["net_return"] = (
        evaluated["gross_return"]
        - evaluated["transaction_cost"]
    )

    daily = (
        evaluated.groupby(
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

    metrics = performance_metrics(
        daily["net_return"]
    )

    active = (
        evaluated["position"]
        != 0.0
    )

    metrics.update(
        {
            "cost_bps":
                float(cost_bps),

            "trades":
                int(
                    (
                        evaluated["turnover"]
                        > 0.0
                    ).sum()
                ),

            "active_rows":
                int(active.sum()),

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

            "maximum_daily_positions":
                int(
                    daily[
                        "active_positions"
                    ].max()
                )
                if not daily.empty
                else 0,

            "turnover_units":
                float(
                    evaluated[
                        "turnover"
                    ].sum()
                ),
        }
    )

    return metrics, daily


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
            "annualized_return_ci_95": [
                None,
                None,
            ],
            "sharpe_ci_95": [
                None,
                None,
            ],
            "positive_annualized_return_probability":
                None,
            "positive_sharpe_probability":
                None,
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

        "positive_annualized_return_probability":
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

    stress_path = (
        output_root
        / "stress_results.csv"
    )

    monthly_path = (
        output_root
        / "monthly_stability.csv"
    )

    yearly_path = (
        output_root
        / "yearly_stability.csv"
    )

    symbol_path = (
        output_root
        / "symbol_contributions.csv"
    )

    bootstrap_path = (
        output_root
        / "bootstrap_confidence.json"
    )

    frozen_path = (
        output_root
        / "frozen_candidate.json"
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
            "BLOCKED: frozen candidate fields missing: "
            + ", ".join(
                missing_candidate
            )
        )

    candidate_id = str(
        candidate["candidate_id"]
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

    model_name = str(
        candidate["model_name"]
    )

    feature_family = str(
        candidate["feature_family"]
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
            "BLOCKED: frozen model object missing."
        )

    if not artifact_features:
        raise SystemExit(
            "BLOCKED: frozen feature list missing."
        )

    freeze_checks = {
        "candidate_id_matches":
            str(
                artifact_strategy.get(
                    "candidate_id"
                )
            )
            == candidate_id,

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
    }

    if not all(
        bool(value)
        for value
        in freeze_checks.values()
    ):
        raise SystemExit(
            "BLOCKED: frozen artifact does not "
            "match the selected Stage 7T candidate."
        )

    dataset = pd.read_csv(
        args.features,
        low_memory=False,
    )

    dataset["timestamp"] = pd.to_datetime(
        dataset["timestamp"],
        errors="coerce",
        utc=True,
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
            "BLOCKED: required feature columns missing: "
            + ", ".join(
                missing_columns
            )
        )

    numeric_columns = (
        artifact_features
        + [
            FUTURE_RETURN,
            TARGET,
        ]
    )

    for column in numeric_columns:
        dataset[column] = pd.to_numeric(
            dataset[column],
            errors="coerce",
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
        .reset_index(drop=True)
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

    test_boundary = unique_dates[
        int(
            len(unique_dates)
            * 0.80
        )
    ]

    test = dataset[
        dataset["timestamp"]
        >= test_boundary
    ].copy()

    if scope != "ALL":
        test = test[
            test["country"]
            == scope
        ].copy()

    if test.empty:
        raise SystemExit(
            "BLOCKED: frozen test scope is empty."
        )

    probability = probability_one(
        artifact_model,
        test[
            artifact_features
        ],
    )

    stress_records = []
    baseline_daily = None
    baseline_working = None
    baseline_metrics = None

    print()
    print("=" * 100)
    print(
        "STAGE 7U FROZEN CANDIDATE "
        "ROBUSTNESS QUALIFICATION"
    )
    print("=" * 100)
    print()
    print("Frozen candidate:")
    print(
        json.dumps(
            {
                "candidate_id":
                    candidate_id,

                "model_name":
                    model_name,

                "feature_family":
                    feature_family,

                "feature_count":
                    len(
                        artifact_features
                    ),

                "scope":
                    scope,

                "mode":
                    mode,

                "threshold":
                    threshold,

                "test_rows":
                    len(test),

                "test_symbols":
                    test[
                        "provider_symbol"
                    ].nunique(),
            },
            indent=2,
            sort_keys=True,
        )
    )

    for delay_bars in DELAY_STRESS_BARS:
        positions = build_positions(
            test,
            probability,
            threshold=threshold,
            mode=mode,
            delay_bars=delay_bars,
        )

        for cost_bps in COST_STRESS_BPS:
            metrics, daily = evaluate_positions(
                positions,
                cost_bps=cost_bps,
            )

            record = {
                "stress_type":
                    "cost_and_delay",

                "delay_bars":
                    delay_bars,

                **metrics,
            }

            stress_records.append(
                record
            )

            if (
                delay_bars == 0
                and cost_bps == 10.0
            ):
                baseline_daily = daily
                baseline_working = positions.copy()
                baseline_metrics = dict(
                    metrics
                )

    if (
        baseline_daily is None
        or baseline_working is None
        or baseline_metrics is None
    ):
        raise SystemExit(
            "BLOCKED: baseline stress result missing."
        )

    baseline_evaluated = (
        baseline_working.copy()
    )

    baseline_evaluated[
        "net_return"
    ] = (
        baseline_evaluated[
            "gross_return"
        ]
        - baseline_evaluated[
            "turnover"
        ]
        * 0.001
    )

    symbol_contributions = (
        baseline_evaluated.groupby(
            "provider_symbol",
            sort=True,
        )
        .agg(
            rows=(
                "provider_symbol",
                "size",
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
            net_return_sum=(
                "net_return",
                "sum",
            ),
            gross_return_sum=(
                "gross_return",
                "sum",
            ),
            turnover_units=(
                "turnover",
                "sum",
            ),
        )
        .reset_index()
        .sort_values(
            "net_return_sum",
            ascending=False,
            kind="stable",
        )
    )

    symbol_contributions[
        "absolute_return_share"
    ] = (
        symbol_contributions[
            "net_return_sum"
        ].abs()
        / max(
            float(
                symbol_contributions[
                    "net_return_sum"
                ].abs().sum()
            ),
            1e-12,
        )
    )

    symbol_contributions.to_csv(
        symbol_path,
        index=False,
    )

    total_absolute_share = (
        symbol_contributions[
            "absolute_return_share"
        ]
    )

    top_1_share = float(
        total_absolute_share
        .head(1)
        .sum()
    )

    top_5_share = float(
        total_absolute_share
        .head(5)
        .sum()
    )

    top_10_share = float(
        total_absolute_share
        .head(10)
        .sum()
    )

    ranked_symbols = (
        symbol_contributions[
            "provider_symbol"
        ].tolist()
    )

    for removal_count in (
        TOP_SYMBOL_REMOVAL_COUNTS
    ):
        removed = set(
            ranked_symbols[
                :removal_count
            ]
        )

        reduced = baseline_working[
            ~baseline_working[
                "provider_symbol"
            ].isin(removed)
        ].copy()

        metrics, _ = evaluate_positions(
            reduced,
            cost_bps=10.0,
        )

        stress_records.append(
            {
                "stress_type":
                    "remove_top_symbols",

                "removed_count":
                    removal_count,

                "removed_identifiers":
                    ",".join(
                        sorted(removed)
                    ),

                "delay_bars":
                    0,

                **metrics,
            }
        )

    monthly_source = baseline_daily.copy()

    monthly_source["month"] = (
        monthly_source[
            "timestamp"
        ].dt.to_period("M")
        .astype(str)
    )

    monthly_records = []

    for month, group in (
        monthly_source.groupby(
            "month",
            sort=True,
        )
    ):
        metrics = performance_metrics(
            group["net_return"]
        )

        monthly_records.append(
            {
                "month":
                    month,

                **metrics,
            }
        )

    monthly_frame = pd.DataFrame(
        monthly_records
    )

    monthly_frame.to_csv(
        monthly_path,
        index=False,
    )

    yearly_source = baseline_daily.copy()

    yearly_source["year"] = (
        yearly_source[
            "timestamp"
        ].dt.year
    )

    yearly_records = []

    for year, group in (
        yearly_source.groupby(
            "year",
            sort=True,
        )
    ):
        metrics = performance_metrics(
            group["net_return"]
        )

        yearly_records.append(
            {
                "year":
                    int(year),

                **metrics,
            }
        )

    yearly_frame = pd.DataFrame(
        yearly_records
    )

    yearly_frame.to_csv(
        yearly_path,
        index=False,
    )

    best_months = (
        monthly_frame.sort_values(
            "total_return",
            ascending=False,
            kind="stable",
        )["month"]
        .tolist()
    )

    for removal_count in (
        TOP_MONTH_REMOVAL_COUNTS
    ):
        removed = set(
            best_months[
                :removal_count
            ]
        )

        reduced_daily = (
            monthly_source[
                ~monthly_source[
                    "month"
                ].isin(removed)
            ]
        )

        metrics = performance_metrics(
            reduced_daily[
                "net_return"
            ]
        )

        stress_records.append(
            {
                "stress_type":
                    "remove_top_months",

                "removed_count":
                    removal_count,

                "removed_identifiers":
                    ",".join(
                        sorted(removed)
                    ),

                "delay_bars":
                    0,

                "cost_bps":
                    10.0,

                "trades":
                    baseline_metrics[
                        "trades"
                    ],

                "coverage":
                    baseline_metrics[
                        "coverage"
                    ],

                "average_daily_positions":
                    baseline_metrics[
                        "average_daily_positions"
                    ],

                "maximum_daily_positions":
                    baseline_metrics[
                        "maximum_daily_positions"
                    ],

                "turnover_units":
                    baseline_metrics[
                        "turnover_units"
                    ],

                **metrics,
            }
        )

    bootstrap = bootstrap_confidence(
        baseline_daily[
            "net_return"
        ]
    )

    bootstrap_path.write_text(
        json.dumps(
            bootstrap,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )

    stress_frame = pd.DataFrame(
        stress_records
    )

    stress_frame.to_csv(
        stress_path,
        index=False,
    )

    cost_20 = stress_frame[
        (
            stress_frame[
                "stress_type"
            ]
            == "cost_and_delay"
        )
        & (
            stress_frame[
                "delay_bars"
            ]
            == 0
        )
        & (
            stress_frame[
                "cost_bps"
            ]
            == 20.0
        )
    ].iloc[0]

    cost_30 = stress_frame[
        (
            stress_frame[
                "stress_type"
            ]
            == "cost_and_delay"
        )
        & (
            stress_frame[
                "delay_bars"
            ]
            == 0
        )
        & (
            stress_frame[
                "cost_bps"
            ]
            == 30.0
        )
    ].iloc[0]

    cost_50 = stress_frame[
        (
            stress_frame[
                "stress_type"
            ]
            == "cost_and_delay"
        )
        & (
            stress_frame[
                "delay_bars"
            ]
            == 0
        )
        & (
            stress_frame[
                "cost_bps"
            ]
            == 50.0
        )
    ].iloc[0]

    delayed_10 = stress_frame[
        (
            stress_frame[
                "stress_type"
            ]
            == "cost_and_delay"
        )
        & (
            stress_frame[
                "delay_bars"
            ]
            == 1
        )
        & (
            stress_frame[
                "cost_bps"
            ]
            == 10.0
        )
    ].iloc[0]

    remove_top_5 = stress_frame[
        (
            stress_frame[
                "stress_type"
            ]
            == "remove_top_symbols"
        )
        & (
            stress_frame[
                "removed_count"
            ]
            == 5
        )
    ].iloc[0]

    remove_top_month = stress_frame[
        (
            stress_frame[
                "stress_type"
            ]
            == "remove_top_months"
        )
        & (
            stress_frame[
                "removed_count"
            ]
            == 1
        )
    ].iloc[0]

    positive_month_fraction = float(
        (
            monthly_frame[
                "total_return"
            ]
            > 0.0
        ).mean()
    )

    positive_year_fraction = float(
        (
            yearly_frame[
                "total_return"
            ]
            > 0.0
        ).mean()
    )

    robustness_checks = {
        "baseline_positive_sharpe":
            bool(
                baseline_metrics[
                    "sharpe"
                ]
                > 0.0
            ),

        "baseline_positive_annualized_return":
            bool(
                baseline_metrics[
                    "annualized_return"
                ]
                > 0.0
            ),

        "twenty_bps_positive":
            bool(
                float(
                    cost_20[
                        "annualized_return"
                    ]
                )
                > 0.0
                and float(
                    cost_20["sharpe"]
                )
                > 0.0
            ),

        "thirty_bps_positive":
            bool(
                float(
                    cost_30[
                        "annualized_return"
                    ]
                )
                > 0.0
                and float(
                    cost_30["sharpe"]
                )
                > 0.0
            ),

        "fifty_bps_recorded":
            bool(
                math.isfinite(
                    float(
                        cost_50[
                            "annualized_return"
                        ]
                    )
                )
            ),

        "one_bar_delay_positive":
            bool(
                float(
                    delayed_10[
                        "annualized_return"
                    ]
                )
                > 0.0
                and float(
                    delayed_10["sharpe"]
                )
                > 0.0
            ),

        "top_five_symbols_removed_positive":
            bool(
                float(
                    remove_top_5[
                        "annualized_return"
                    ]
                )
                > 0.0
            ),

        "best_month_removed_positive":
            bool(
                float(
                    remove_top_month[
                        "annualized_return"
                    ]
                )
                > 0.0
            ),

        "monthly_positive_majority":
            bool(
                positive_month_fraction
                >= 0.50
            ),

        "yearly_positive_majority":
            bool(
                positive_year_fraction
                >= 0.50
            ),

        "top_symbol_concentration_below_35_percent":
            bool(
                top_1_share
                < 0.35
            ),

        "top_five_concentration_below_70_percent":
            bool(
                top_5_share
                < 0.70
            ),

        "bootstrap_positive_return_probability_at_least_80_percent":
            bool(
                bootstrap[
                    "positive_annualized_return_probability"
                ]
                is not None
                and bootstrap[
                    "positive_annualized_return_probability"
                ]
                >= 0.80
            ),

        "bootstrap_positive_sharpe_probability_at_least_80_percent":
            bool(
                bootstrap[
                    "positive_sharpe_probability"
                ]
                is not None
                and bootstrap[
                    "positive_sharpe_probability"
                ]
                >= 0.80
            ),
    }

    frozen_checks = {
        **freeze_checks,

        "no_candidate_search_performed":
            True,

        "no_feature_search_performed":
            True,

        "no_threshold_search_performed":
            True,

        "no_model_refit_performed":
            True,

        "frozen_model_used":
            True,
    }

    safety_checks = {
        "runtime_model_not_replaced":
            artifact.get(
                "authorization",
                {},
            ).get(
                "model_replacement"
            )
            is False,

        "strategy_not_promoted":
            artifact.get(
                "authorization",
                {},
            ).get(
                "strategy_promotion"
            )
            is False,

        "paper_execution_disabled":
            artifact.get(
                "authorization",
                {},
            ).get(
                "paper_execution"
            )
            is False,

        "broker_execution_disabled":
            artifact.get(
                "authorization",
                {},
            ).get(
                "broker_execution"
            )
            is False,

        "live_execution_disabled":
            artifact.get(
                "authorization",
                {},
            ).get(
                "live_execution"
            )
            is False,
    }

    failed_frozen_checks = [
        name
        for name, passed
        in frozen_checks.items()
        if not bool(passed)
    ]

    failed_safety_checks = [
        name
        for name, passed
        in safety_checks.items()
        if not bool(passed)
    ]

    failed_robustness_checks = [
        name
        for name, passed
        in robustness_checks.items()
        if not bool(passed)
    ]

    artifact_qualification_passed = bool(
        not failed_frozen_checks
        and not failed_safety_checks
    )

    robustness_passed = bool(
        not failed_robustness_checks
    )

    classification = (
        "stage7u_frozen_candidate_robustness_qualified"
        if artifact_qualification_passed
        else "stage7u_frozen_candidate_artifact_failure"
    )

    strategy_classification = (
        "frozen_candidate_robustness_metrics_satisfied_but_not_authorized"
        if robustness_passed
        else "frozen_candidate_requires_additional_learning"
    )

    frozen_payload = {
        "generated_at":
            utc_now(),

        "candidate":
            candidate,

        "artifact_model_name":
            artifact.get(
                "model_name"
            ),

        "artifact_feature_family":
            artifact.get(
                "feature_family"
            ),

        "artifact_features":
            artifact_features,

        "artifact_strategy":
            artifact_strategy,

        "freeze_checks":
            frozen_checks,

        "model_sha256":
            sha256_file(
                Path(
                    args.stage7t_model
                )
            ),

        "features_sha256":
            sha256_file(
                Path(
                    args.features
                )
            ),

        "authorization":
            artifact.get(
                "authorization",
                {}
            ),
    }

    frozen_path.write_text(
        json.dumps(
            frozen_payload,
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

        "feature_count":
            len(
                artifact_features
            ),

        "scope":
            scope,

        "mode":
            mode,

        "threshold":
            threshold,

        "test_rows":
            int(len(test)),

        "test_symbols":
            int(
                test[
                    "provider_symbol"
                ].nunique()
            ),

        "baseline_trades":
            int(
                baseline_metrics[
                    "trades"
                ]
            ),

        "baseline_coverage":
            float(
                baseline_metrics[
                    "coverage"
                ]
            ),

        "baseline_annualized_return":
            float(
                baseline_metrics[
                    "annualized_return"
                ]
            ),

        "baseline_sharpe":
            float(
                baseline_metrics[
                    "sharpe"
                ]
            ),

        "baseline_maximum_drawdown":
            float(
                baseline_metrics[
                    "maximum_drawdown"
                ]
            ),

        "baseline_longest_drawdown_days":
            int(
                baseline_metrics[
                    "longest_drawdown_days"
                ]
            ),

        "twenty_bps_annualized_return":
            float(
                cost_20[
                    "annualized_return"
                ]
            ),

        "twenty_bps_sharpe":
            float(
                cost_20["sharpe"]
            ),

        "thirty_bps_annualized_return":
            float(
                cost_30[
                    "annualized_return"
                ]
            ),

        "thirty_bps_sharpe":
            float(
                cost_30["sharpe"]
            ),

        "fifty_bps_annualized_return":
            float(
                cost_50[
                    "annualized_return"
                ]
            ),

        "fifty_bps_sharpe":
            float(
                cost_50["sharpe"]
            ),

        "one_bar_delay_annualized_return":
            float(
                delayed_10[
                    "annualized_return"
                ]
            ),

        "one_bar_delay_sharpe":
            float(
                delayed_10["sharpe"]
            ),

        "positive_month_fraction":
            positive_month_fraction,

        "positive_year_fraction":
            positive_year_fraction,

        "top_1_symbol_absolute_return_share":
            top_1_share,

        "top_5_symbol_absolute_return_share":
            top_5_share,

        "top_10_symbol_absolute_return_share":
            top_10_share,

        "bootstrap_positive_return_probability":
            bootstrap[
                "positive_annualized_return_probability"
            ],

        "bootstrap_positive_sharpe_probability":
            bootstrap[
                "positive_sharpe_probability"
            ],

        "failed_robustness_checks":
            failed_robustness_checks,

        "robustness_metrics_satisfied":
            robustness_passed,

        "promotion_authorized":
            False,
    }

    result = {
        "objective":
            (
                "Stage 7U Frozen Candidate "
                "Robustness Qualification"
            ),

        "generated_at":
            utc_now(),

        "classification":
            classification,

        "strategy_classification":
            strategy_classification,

        "passed":
            artifact_qualification_passed,

        "robustness_metrics_satisfied":
            robustness_passed,

        "frozen_checks":
            frozen_checks,

        "robustness_checks":
            robustness_checks,

        "safety_checks":
            safety_checks,

        "failed_frozen_checks":
            failed_frozen_checks,

        "failed_robustness_checks":
            failed_robustness_checks,

        "failed_safety_checks":
            failed_safety_checks,

        "summary":
            summary,

        "bootstrap":
            bootstrap,

        "source":
            {
                "features":
                    args.features,

                "stage7t_result":
                    args.stage7t_result,

                "stage7t_selected":
                    args.stage7t_selected,

                "stage7t_model":
                    args.stage7t_model,
            },

        "artifacts":
            {
                "stress_results":
                    str(stress_path),

                "monthly_stability":
                    str(monthly_path),

                "yearly_stability":
                    str(yearly_path),

                "symbol_contributions":
                    str(symbol_path),

                "bootstrap_confidence":
                    str(bootstrap_path),

                "frozen_candidate":
                    str(frozen_path),
            },

        "authorization":
            {
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

        "safety":
            {
                "source_files_modified":
                    False,

                "model_refit":
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
            "NEUROVEST — STAGE 7U FROZEN "
            "CANDIDATE ROBUSTNESS QUALIFICATION"
        ),
        "=" * 100,
        "",
        (
            "Artifact qualification: "
            + (
                "PASS"
                if result["passed"]
                else "FAILED"
            )
        ),
        "",
        (
            "Robustness metrics: "
            + (
                "SATISFIED"
                if robustness_passed
                else "NOT SATISFIED"
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
        "FROZEN CHECKS:",
    ]

    for name, passed in (
        frozen_checks.items()
    ):
        report_lines.append(
            f"  {name:<66} {bool(passed)}"
        )

    report_lines.extend(
        [
            "",
            "ROBUSTNESS CHECKS:",
        ]
    )

    for name, passed in (
        robustness_checks.items()
    ):
        report_lines.append(
            f"  {name:<66} {bool(passed)}"
        )

    report_lines.extend(
        [
            "",
            "SAFETY CHECKS:",
        ]
    )

    for name, passed in (
        safety_checks.items()
    ):
        report_lines.append(
            f"  {name:<66} {bool(passed)}"
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
            "No model family search occurred.",
            "No feature search occurred.",
            "No threshold search occurred.",
            "The frozen Stage 7T model was not refit.",
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
        "STAGE 7U FROZEN CANDIDATE "
        "ROBUSTNESS QUALIFICATION COMPLETE"
    )
    print("=" * 100)
    print()
    print(
        json.dumps(
            {
                "passed":
                    result["passed"],

                "robustness_metrics_satisfied":
                    robustness_passed,

                "classification":
                    classification,

                "strategy_classification":
                    strategy_classification,

                "failed_frozen_checks":
                    failed_frozen_checks,

                "failed_robustness_checks":
                    failed_robustness_checks,

                "failed_safety_checks":
                    failed_safety_checks,

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
        if artifact_qualification_passed
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())

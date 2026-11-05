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

PAPER_ACCOUNT_VALUE = 100000.0
MAX_GROSS_EXPOSURE = 0.25
MAX_SYMBOL_EXPOSURE = 0.02
MINIMUM_ORDER_VALUE = 100.0
TRANSACTION_COST_BPS = 10.0


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
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def sha256_bytes(
    value: bytes,
) -> str:
    return hashlib.sha256(
        value
    ).hexdigest()


def add_interaction_features(
    frame: pd.DataFrame,
) -> pd.DataFrame:
    result = frame.copy()
    epsilon = 1e-8

    result["momentum_spread_5_20"] = (
        result["return_5d"]
        - result["return_20d"]
    )

    result["momentum_spread_10_20"] = (
        result["return_10d"]
        - result["return_20d"]
    )

    result["trend_spread_5_20"] = (
        result["close_to_sma_5"]
        - result["close_to_sma_20"]
    )

    result["trend_spread_20_50"] = (
        result["close_to_sma_20"]
        - result["close_to_sma_50"]
    )

    result["volatility_ratio_5_20"] = (
        result["volatility_5d"]
        / (
            result["volatility_20d"].abs()
            + epsilon
        )
    )

    result["risk_adjusted_momentum"] = (
        result["return_20d"]
        / (
            result["volatility_20d"].abs()
            + epsilon
        )
    )

    result["range_volatility_interaction"] = (
        result["range_fraction"]
        * result["volatility_20d"]
    )

    result["volume_return_interaction"] = (
        result["volume_change_1d"]
        * result["return_1d"]
    )

    return result


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

    values = list(
        classes
        if classes is not None
        else [0, 1]
    )

    index = (
        values.index(1)
        if 1 in values
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
        1.0 + cleaned
    ).cumprod()

    return float(
        (
            equity
            / equity.cummax()
            - 1.0
        ).min()
    )


def strategy_metrics(
    frame: pd.DataFrame,
) -> dict[str, Any]:
    daily = (
        frame.groupby(
            "timestamp",
            sort=True,
        )["net_return"]
        .mean()
    )

    if daily.empty:
        return {
            "days": 0,
            "trades": 0,
            "annualized_return": 0.0,
            "annualized_volatility": 0.0,
            "sharpe": 0.0,
            "maximum_drawdown": 0.0,
        }

    gross = float(
        (
            1.0 + daily
        ).prod()
    )

    annualized_return = (
        gross
        ** (
            252.0 / len(daily)
        )
        - 1.0
        if gross > 0.0
        else 0.0
    )

    annualized_volatility = (
        float(
            daily.std(ddof=1)
            * math.sqrt(252.0)
        )
        if len(daily) > 1
        else 0.0
    )

    sharpe = (
        annualized_return
        / annualized_volatility
        if annualized_volatility > 0.0
        else 0.0
    )

    return {
        "days":
            int(len(daily)),

        "trades":
            int(
                (
                    frame["turnover"]
                    > 0.0
                ).sum()
            ),

        "annualized_return":
            float(
                annualized_return
            ),

        "annualized_volatility":
            annualized_volatility,

        "sharpe":
            float(sharpe),

        "maximum_drawdown":
            maximum_drawdown(daily),
    }


def main() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--features",
        required=True,
    )

    parser.add_argument(
        "--stage7w-result",
        required=True,
    )

    parser.add_argument(
        "--stage7w-selected",
        required=True,
    )

    parser.add_argument(
        "--stage7w-model",
        required=True,
    )

    parser.add_argument(
        "--output",
        required=True,
    )

    args = parser.parse_args()

    root = Path(args.output)

    predictions_path = (
        root
        / "reproduced_predictions.csv"
    )

    signals_path = (
        root
        / "frozen_signals.csv"
    )

    intents_path = (
        root
        / "paper_order_intents.csv"
    )

    package_path = (
        root
        / "paper_readiness_package.json"
    )

    result_path = (
        root
        / "result.json"
    )

    report_path = (
        root
        / "report.txt"
    )

    stage7w = json.loads(
        Path(
            args.stage7w_result
        ).read_text(
            encoding="utf-8"
        )
    )

    selected = json.loads(
        Path(
            args.stage7w_selected
        ).read_text(
            encoding="utf-8"
        )
    )

    artifact = joblib.load(
        args.stage7w_model
    )

    candidate = stage7w.get(
        "selected_candidate",
        {}
    )

    artifact_strategy = artifact.get(
        "strategy",
        {}
    )

    feature_columns = list(
        artifact.get(
            "feature_columns",
            []
        )
    )

    model = artifact.get("model")

    if not candidate:
        raise SystemExit(
            "BLOCKED: Stage 7W candidate missing."
        )

    if model is None:
        raise SystemExit(
            "BLOCKED: frozen model missing."
        )

    if not feature_columns:
        raise SystemExit(
            "BLOCKED: frozen feature list missing."
        )

    candidate_id = str(
        candidate.get("candidate_id")
    )

    scope = str(
        candidate.get("scope")
    )

    mode = str(
        candidate.get("mode")
    )

    threshold = float(
        candidate.get("threshold")
    )

    continuity_checks = {
        "stage7w_passed":
            stage7w.get("passed") is True,

        "promotion_metrics_satisfied":
            stage7w.get(
                "promotion_metrics_satisfied"
            )
            is True,

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

        "runtime_integration_disabled":
            artifact.get(
                "authorization",
                {},
            ).get(
                "runtime_integration"
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

    if not all(
        bool(value)
        for value
        in continuity_checks.values()
    ):
        raise SystemExit(
            "BLOCKED: Stage 7W continuity "
            "verification failed."
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

    dataset = add_interaction_features(
        dataset
    )

    required = {
        "timestamp",
        "provider_symbol",
        "country",
        TARGET,
        FUTURE_RETURN,
        *feature_columns,
    }

    missing = sorted(
        required
        - set(dataset.columns)
    )

    if missing:
        raise SystemExit(
            "BLOCKED: required columns missing: "
            + ", ".join(missing)
        )

    for column in (
        feature_columns
        + [TARGET, FUTURE_RETURN]
    ):
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
                TARGET,
                FUTURE_RETURN,
                *feature_columns,
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

    dates = np.array(
        sorted(
            dataset["timestamp"]
            .unique()
        )
    )

    confirmation_boundary = dates[
        int(len(dates) * 0.80)
    ]

    confirmation = dataset[
        dataset["timestamp"]
        >= confirmation_boundary
    ].copy()

    if scope != "ALL":
        confirmation = confirmation[
            confirmation["country"]
            == scope
        ].copy()

    if confirmation.empty:
        raise SystemExit(
            "BLOCKED: confirmation scope is empty."
        )

    first_probability = probability_one(
        model,
        confirmation[
            feature_columns
        ],
    )

    second_probability = probability_one(
        model,
        confirmation[
            feature_columns
        ],
    )

    first_bytes = np.asarray(
        first_probability,
        dtype=np.float64,
    ).tobytes()

    second_bytes = np.asarray(
        second_probability,
        dtype=np.float64,
    ).tobytes()

    first_hash = sha256_bytes(
        first_bytes
    )

    second_hash = sha256_bytes(
        second_bytes
    )

    prediction_frame = confirmation[
        [
            "timestamp",
            "provider_symbol",
            "country",
            TARGET,
            FUTURE_RETURN,
        ]
    ].copy()

    prediction_frame[
        "probability_run_1"
    ] = first_probability

    prediction_frame[
        "probability_run_2"
    ] = second_probability

    prediction_frame[
        "probability_difference"
    ] = (
        prediction_frame[
            "probability_run_1"
        ]
        - prediction_frame[
            "probability_run_2"
        ]
    ).abs()

    prediction_frame.to_csv(
        predictions_path,
        index=False,
    )

    if mode == "long_only":
        prediction_frame["position"] = (
            prediction_frame[
                "probability_run_1"
            ]
            >= threshold
        ).astype(float)

    elif mode == "long_short":
        prediction_frame["position"] = (
            np.select(
                [
                    prediction_frame[
                        "probability_run_1"
                    ]
                    >= threshold,

                    prediction_frame[
                        "probability_run_1"
                    ]
                    <= 1.0 - threshold,
                ],
                [1.0, -1.0],
                default=0.0,
            )
        )

    else:
        raise SystemExit(
            "BLOCKED: unsupported frozen mode."
        )

    prediction_frame = (
        prediction_frame.sort_values(
            [
                "provider_symbol",
                "timestamp",
            ],
            kind="stable",
        )
    )

    prediction_frame[
        "previous_position"
    ] = (
        prediction_frame.groupby(
            "provider_symbol",
            sort=False,
        )["position"]
        .shift(1)
        .fillna(0.0)
    )

    prediction_frame["turnover"] = (
        prediction_frame["position"]
        - prediction_frame[
            "previous_position"
        ]
    ).abs()

    prediction_frame["gross_return"] = (
        prediction_frame["position"]
        * prediction_frame[
            FUTURE_RETURN
        ]
    )

    prediction_frame["net_return"] = (
        prediction_frame[
            "gross_return"
        ]
        - prediction_frame["turnover"]
        * (
            TRANSACTION_COST_BPS
            / 10000.0
        )
    )

    prediction_frame.to_csv(
        signals_path,
        index=False,
    )

    metrics = strategy_metrics(
        prediction_frame
    )

    latest_timestamp = (
        prediction_frame[
            "timestamp"
        ].max()
    )

    latest = prediction_frame[
        prediction_frame["timestamp"]
        == latest_timestamp
    ].copy()

    latest = latest[
        latest["position"] != 0.0
    ].copy()

    active_count = int(
        len(latest)
    )

    gross_budget = (
        PAPER_ACCOUNT_VALUE
        * MAX_GROSS_EXPOSURE
    )

    equal_order_value = (
        gross_budget / active_count
        if active_count > 0
        else 0.0
    )

    capped_order_value = min(
        equal_order_value,
        PAPER_ACCOUNT_VALUE
        * MAX_SYMBOL_EXPOSURE,
    )

    intents = []

    for row in latest.itertuples(
        index=False
    ):
        side = (
            "BUY"
            if float(row.position) > 0.0
            else "SELL"
        )

        order_value = (
            capped_order_value
            if capped_order_value
            >= MINIMUM_ORDER_VALUE
            else 0.0
        )

        if order_value <= 0.0:
            continue

        intent_payload = (
            f"{candidate_id}|"
            f"{row.provider_symbol}|"
            f"{latest_timestamp}|"
            f"{side}|"
            f"{order_value:.2f}"
        )

        intents.append(
            {
                "intent_id":
                    (
                        "stage7x_intent_"
                        + hashlib.sha256(
                            intent_payload.encode(
                                "utf-8"
                            )
                        ).hexdigest()[:20]
                    ),

                "candidate_id":
                    candidate_id,

                "timestamp":
                    str(latest_timestamp),

                "symbol":
                    row.provider_symbol,

                "side":
                    side,

                "probability":
                    float(
                        row.probability_run_1
                    ),

                "threshold":
                    threshold,

                "target_order_value":
                    float(order_value),

                "maximum_symbol_exposure":
                    MAX_SYMBOL_EXPOSURE,

                "maximum_gross_exposure":
                    MAX_GROSS_EXPOSURE,

                "paper_authorized":
                    False,

                "submitted":
                    False,

                "broker_request_created":
                    False,

                "live_order_created":
                    False,
            }
        )

    intent_fields = [
        "intent_id",
        "candidate_id",
        "timestamp",
        "symbol",
        "side",
        "probability",
        "threshold",
        "target_order_value",
        "maximum_symbol_exposure",
        "maximum_gross_exposure",
        "paper_authorized",
        "submitted",
        "broker_request_created",
        "live_order_created",
    ]

    pd.DataFrame(
        intents,
        columns=intent_fields,
    ).to_csv(
        intents_path,
        index=False,
    )

    intent_gross_value = float(
        sum(
            abs(
                record[
                    "target_order_value"
                ]
            )
            for record in intents
        )
    )

    reproducibility_checks = {
        "prediction_lengths_match":
            len(first_probability)
            == len(second_probability),

        "prediction_arrays_equal":
            bool(
                np.array_equal(
                    first_probability,
                    second_probability,
                )
            ),

        "prediction_hashes_match":
            first_hash == second_hash,

        "maximum_prediction_difference_zero":
            float(
                prediction_frame[
                    "probability_difference"
                ].max()
            )
            == 0.0,

        "candidate_continuity_verified":
            all(
                bool(value)
                for value
                in continuity_checks.values()
            ),

        "confirmation_positive_return":
            metrics[
                "annualized_return"
            ]
            > 0.0,

        "confirmation_positive_sharpe":
            metrics["sharpe"] > 0.0,

        "paper_intents_not_authorized":
            all(
                record[
                    "paper_authorized"
                ]
                is False
                for record in intents
            ),

        "paper_intents_not_submitted":
            all(
                record["submitted"]
                is False
                for record in intents
            ),

        "gross_exposure_within_cap":
            intent_gross_value
            <= (
                PAPER_ACCOUNT_VALUE
                * MAX_GROSS_EXPOSURE
                + 1e-8
            ),

        "each_symbol_within_cap":
            all(
                record[
                    "target_order_value"
                ]
                <= (
                    PAPER_ACCOUNT_VALUE
                    * MAX_SYMBOL_EXPOSURE
                    + 1e-8
                )
                for record in intents
            ),

        "runtime_model_not_replaced":
            True,

        "strategy_not_promoted":
            True,

        "broker_requests_not_created":
            True,

        "live_orders_not_created":
            True,
    }

    failed_checks = [
        name
        for name, passed
        in reproducibility_checks.items()
        if not bool(passed)
    ]

    passed = not failed_checks

    classification = (
        "stage7x_frozen_reproducibility_and_paper_readiness_qualified"
        if passed
        else "stage7x_reproducibility_or_boundary_failure"
    )

    package = {
        "generated_at":
            utc_now(),

        "candidate_id":
            candidate_id,

        "model_name":
            artifact.get(
                "model_name"
            ),

        "feature_family":
            artifact.get(
                "feature_family"
            ),

        "feature_columns":
            feature_columns,

        "scope":
            scope,

        "mode":
            mode,

        "threshold":
            threshold,

        "model_sha256":
            sha256_file(
                Path(
                    args.stage7w_model
                )
            ),

        "features_sha256":
            sha256_file(
                Path(
                    args.features
                )
            ),

        "prediction_sha256":
            first_hash,

        "paper_account_value":
            PAPER_ACCOUNT_VALUE,

        "maximum_gross_exposure":
            MAX_GROSS_EXPOSURE,

        "maximum_symbol_exposure":
            MAX_SYMBOL_EXPOSURE,

        "latest_signal_timestamp":
            str(latest_timestamp),

        "paper_intent_count":
            len(intents),

        "paper_intent_gross_value":
            intent_gross_value,

        "metrics":
            metrics,

        "authorization": {
            "paper_readiness_package_created":
                True,

            "paper_execution_authorized":
                False,

            "runtime_model_replacement":
                False,

            "strategy_promotion":
                False,

            "broker_execution":
                False,

            "live_execution":
                False,
        },
    }

    package_path.write_text(
        json.dumps(
            package,
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
            artifact.get(
                "model_name"
            ),

        "feature_family":
            artifact.get(
                "feature_family"
            ),

        "scope":
            scope,

        "mode":
            mode,

        "threshold":
            threshold,

        "confirmation_rows":
            int(
                len(prediction_frame)
            ),

        "confirmation_symbols":
            int(
                prediction_frame[
                    "provider_symbol"
                ].nunique()
            ),

        "prediction_hash":
            first_hash,

        "annualized_return":
            metrics[
                "annualized_return"
            ],

        "sharpe":
            metrics["sharpe"],

        "maximum_drawdown":
            metrics[
                "maximum_drawdown"
            ],

        "paper_intent_count":
            len(intents),

        "paper_intent_gross_value":
            intent_gross_value,

        "paper_execution_authorized":
            False,
    }

    result = {
        "objective":
            (
                "Stage 7X Frozen Candidate "
                "Reproducibility and Paper Readiness"
            ),

        "generated_at":
            utc_now(),

        "classification":
            classification,

        "passed":
            passed,

        "checks":
            reproducibility_checks,

        "continuity_checks":
            continuity_checks,

        "failed_checks":
            failed_checks,

        "summary":
            summary,

        "package":
            package,

        "artifacts": {
            "predictions":
                str(predictions_path),

            "signals":
                str(signals_path),

            "paper_order_intents":
                str(intents_path),

            "paper_readiness_package":
                str(package_path),
        },

        "authorization": {
            "paper_readiness_qualified":
                passed,

            "paper_execution_authorized":
                False,

            "runtime_model_replacement":
                False,

            "strategy_promotion":
                False,

            "broker_execution":
                False,

            "live_execution":
                False,
        },

        "safety": {
            "training_started":
                False,

            "model_refit":
                False,

            "runtime_model_replaced":
                False,

            "strategy_promoted":
                False,

            "paper_orders_submitted":
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

    lines = [
        "=" * 100,
        (
            "NEUROVEST — STAGE 7X FROZEN "
            "REPRODUCIBILITY AND PAPER READINESS"
        ),
        "=" * 100,
        "",
        (
            "Qualification: "
            + (
                "PASS"
                if passed
                else "FAILED"
            )
        ),
        "",
        f"Classification: {classification}",
        "",
        "CHECKS:",
    ]

    for name, check_passed in (
        reproducibility_checks.items()
    ):
        lines.append(
            f"  {name:<68} {bool(check_passed)}"
        )

    lines.extend(
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
                "The frozen Stage 7W model "
                "was not retrained."
            ),
            (
                "Predictions were reproduced "
                "twice and hashed."
            ),
            (
                "Paper-order intents were "
                "generated but not authorized."
            ),
            "No runtime model was replaced.",
            "No strategy was promoted.",
            "No paper order was submitted.",
            "No broker request was created.",
            "No live order was created.",
            "Terminal remains open.",
        ]
    )

    report_path.write_text(
        "\n".join(lines)
        + "\n",
        encoding="utf-8",
    )

    print()
    print("=" * 100)
    print(
        "STAGE 7X FROZEN REPRODUCIBILITY "
        "AND PAPER READINESS COMPLETE"
    )
    print("=" * 100)
    print()
    print(
        json.dumps(
            {
                "passed":
                    passed,

                "classification":
                    classification,

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

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

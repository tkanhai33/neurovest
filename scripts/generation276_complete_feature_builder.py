#!/usr/bin/env python3
"""
Generation 276 isolated complete feature builder.

This file builds only offline feature and target columns from a
provided raw OHLCV file. It performs no network access, model training,
registration, promotion, parent replacement, runtime activation, or
order execution.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import argparse
import json
import math
import sys

import numpy as np
import pandas as pd


BASE_FEATURES = (
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
)

TARGET = "target_next_up"

RAW_REQUIRED = (
    "timestamp",
    "provider_symbol",
    "open",
    "high",
    "low",
    "close",
    "volume",
)


def load_frame(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(
            path,
            low_memory=False,
        )

    if suffix in {
        ".parquet",
        ".pq",
    }:
        return pd.read_parquet(
            path
        )

    raise ValueError(
        f"Unsupported raw input format: {path}"
    )


def write_frame(
    frame: pd.DataFrame,
    path: Path,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    suffix = path.suffix.lower()

    if suffix == ".csv":
        frame.to_csv(
            path,
            index=False,
        )

        return

    if suffix in {
        ".parquet",
        ".pq",
    }:
        frame.to_parquet(
            path,
            index=False,
        )

        return

    raise ValueError(
        f"Unsupported output format: {path}"
    )


def build_base_features(
    raw: pd.DataFrame,
) -> pd.DataFrame:
    missing = sorted(
        set(RAW_REQUIRED)
        - set(raw.columns)
    )

    if missing:
        raise ValueError(
            "Raw input is missing required columns: "
            + ", ".join(missing)
        )

    frame = raw.copy()

    frame["timestamp"] = pd.to_datetime(
        frame["timestamp"],
        errors="coerce",
        utc=True,
    )

    frame["provider_symbol"] = (
        frame["provider_symbol"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    for column in (
        "open",
        "high",
        "low",
        "close",
        "volume",
    ):
        frame[column] = pd.to_numeric(
            frame[column],
            errors="coerce",
        )

    frame = frame.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    frame = frame.dropna(
        subset=list(RAW_REQUIRED)
    )

    frame = (
        frame
        .sort_values(
            [
                "provider_symbol",
                "timestamp",
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

    grouped = frame.groupby(
        "provider_symbol",
        sort=False,
        group_keys=False,
    )

    for periods in (
        1,
        5,
        10,
        20,
    ):
        frame[
            f"return_{periods}d"
        ] = grouped[
            "close"
        ].pct_change(
            periods=periods,
            fill_method=None,
        )

    frame["volatility_5d"] = (
        frame.groupby(
            "provider_symbol",
            sort=False,
        )["return_1d"]
        .transform(
            lambda values:
                values.rolling(
                    window=5,
                    min_periods=5,
                ).std()
        )
    )

    frame["volatility_20d"] = (
        frame.groupby(
            "provider_symbol",
            sort=False,
        )["return_1d"]
        .transform(
            lambda values:
                values.rolling(
                    window=20,
                    min_periods=20,
                ).std()
        )
    )

    close_denominator = frame[
        "close"
    ].replace(
        0.0,
        np.nan,
    )

    frame["range_fraction"] = (
        frame["high"]
        - frame["low"]
    ) / close_denominator

    for window in (
        5,
        20,
        50,
    ):
        moving_average = (
            frame.groupby(
                "provider_symbol",
                sort=False,
            )["close"]
            .transform(
                lambda values:
                    values.rolling(
                        window=window,
                        min_periods=window,
                    ).mean()
            )
        )

        frame[
            f"close_to_sma_{window}"
        ] = (
            frame["close"]
            / moving_average.replace(
                0.0,
                np.nan,
            )
        ) - 1.0

    frame["volume_change_1d"] = (
        grouped[
            "volume"
        ].pct_change(
            periods=1,
            fill_method=None,
        )
    )

    volume_average_20 = (
        frame.groupby(
            "provider_symbol",
            sort=False,
        )["volume"]
        .transform(
            lambda values:
                values.rolling(
                    window=20,
                    min_periods=20,
                ).mean()
        )
    )

    frame["volume_ratio_20d"] = (
        frame["volume"]
        / volume_average_20.replace(
            0.0,
            np.nan,
        )
    )

    next_close = grouped[
        "close"
    ].shift(-1)

    frame[TARGET] = np.where(
        next_close.notna(),
        (
            next_close
            > frame["close"]
        ).astype(int),
        np.nan,
    )

    return frame


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build isolated Generation 276 base features and target "
            "from a local raw OHLCV dataset."
        )
    )

    parser.add_argument(
        "--input",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--output",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--contract-output",
        required=True,
        type=Path,
    )

    return parser


def main() -> int:
    args = build_parser().parse_args()

    raw = load_frame(
        args.input
    )

    built = build_base_features(
        raw
    )

    write_frame(
        built,
        args.output,
    )

    contract = {
        "classification":
            "generation276_isolated_base_builder_completed",

        "passed":
            True,

        "input":
            str(args.input),

        "output":
            str(args.output),

        "input_rows":
            int(len(raw)),

        "output_rows":
            int(len(built)),

        "produced_features":
            list(BASE_FEATURES),

        "produced_target":
            TARGET,

        "network_access":
            False,

        "training_performed":
            False,

        "registration_performed":
            False,

        "promotion_performed":
            False,

        "runtime_activation":
            False,

        "orders_submitted":
            0,
    }

    args.contract_output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    args.contract_output.write_text(
        json.dumps(
            contract,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )

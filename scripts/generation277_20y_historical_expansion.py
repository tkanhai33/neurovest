#!/usr/bin/env python3

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import argparse
import csv
import hashlib
import json
import math
import sys
import time
import traceback

import pandas as pd

from backend.app.stacks.market_data.yfinance_historical_bars_adapter import (
    get_historical_bars,
)


DEFAULT_FROZEN_DATASET = Path(
    "runtime/training/"
    "generation274_challenger_confirmation_freeze_20260806_085814/"
    "evidence/inputs/training_dataset.csv"
)


RAW_COLUMNS = (
    "timestamp",
    "provider_symbol",
    "open",
    "high",
    "low",
    "close",
    "volume",
)


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

    if isinstance(value, float):
        if not math.isfinite(value):
            return None

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


def sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def normalize_timestamp(
    value: Any,
) -> str | None:
    if value is None:
        return None

    parsed = pd.to_datetime(
        value,
        errors="coerce",
        utc=True,
    )

    if pd.isna(parsed):
        return None

    return parsed.isoformat()


def finite_number(
    value: Any,
) -> float | None:
    try:
        result = float(value)
    except Exception:
        return None

    if not math.isfinite(result):
        return None

    return result


def normalize_bar(
    symbol: str,
    bar: dict[str, Any],
) -> dict[str, Any] | None:
    timestamp = None

    for key in (
        "timestamp",
        "date",
        "datetime",
        "time",
        "bar_time",
    ):
        if key in bar:
            timestamp = normalize_timestamp(
                bar.get(key)
            )

            if timestamp is not None:
                break

    if timestamp is None:
        return None

    normalized = {
        "timestamp":
            timestamp,

        "provider_symbol":
            symbol,

        "open":
            finite_number(
                bar.get("open")
            ),

        "high":
            finite_number(
                bar.get("high")
            ),

        "low":
            finite_number(
                bar.get("low")
            ),

        "close":
            finite_number(
                bar.get("close")
            ),

        "volume":
            finite_number(
                bar.get("volume")
            ),
    }

    if any(
        normalized[column] is None
        for column in (
            "open",
            "high",
            "low",
            "close",
            "volume",
        )
    ):
        return None

    return normalized


parser = argparse.ArgumentParser(
    description=(
        "Generation 277 — 15-20 year "
        "historical market expansion."
    )
)

parser.add_argument(
    "--output-root",
    required=True,
)

parser.add_argument(
    "--frozen-dataset",
    default=str(
        DEFAULT_FROZEN_DATASET
    ),
)

parser.add_argument(
    "--years",
    type=int,
    default=20,
)

parser.add_argument(
    "--interval",
    default="1d",
)

parser.add_argument(
    "--request-delay",
    type=float,
    default=0.35,
)

args = parser.parse_args()

if args.years < 15:
    raise SystemExit(
        "Generation 277 requires "
        "at least 15 years."
    )

if args.years > 25:
    raise SystemExit(
        "BLOCKED: unreasonable historical "
        "window requested."
    )

output_root = Path(
    args.output_root
)

frozen_dataset = Path(
    args.frozen_dataset
)

raw_root = (
    output_root
    / "raw"
)

evidence_root = (
    output_root
    / "evidence"
)

for path in (
    output_root,
    raw_root,
    evidence_root,
):
    path.mkdir(
        parents=True,
        exist_ok=True,
    )

progress_path = (
    output_root
    / "progress.json"
)

result_path = (
    output_root
    / "result.json"
)

report_path = (
    output_root
    / "report.txt"
)

coverage_path = (
    output_root
    / "symbol_coverage.csv"
)

failure_path = (
    output_root
    / "failed_symbols.csv"
)

combined_path = (
    output_root
    / "generation277_raw_20y_ohlcv.csv"
)

manifest_path = (
    output_root
    / "raw_manifest.json"
)

if not frozen_dataset.is_file():
    raise SystemExit(
        "BLOCKED: frozen dataset missing: "
        + str(
            frozen_dataset
        )
    )

frozen_hash_before = sha256_file(
    frozen_dataset
)

header = list(
    pd.read_csv(
        frozen_dataset,
        nrows=0,
    ).columns
)

if (
    "provider_symbol"
    not in header
):
    raise SystemExit(
        "BLOCKED: provider_symbol "
        "column missing."
    )

frozen_symbols = sorted(
    {
        str(value)
        .strip()
        .upper()
        for value
        in pd.read_csv(
            frozen_dataset,
            usecols=[
                "provider_symbol"
            ],
            low_memory=False,
        )[
            "provider_symbol"
        ]
        .dropna()
        .tolist()
        if str(value).strip()
    }
)

if len(
    frozen_symbols
) != 370:
    raise SystemExit(
        "BLOCKED: expected 370 symbols, got "
        + str(
            len(
                frozen_symbols
            )
        )
    )

end_date = datetime.now(
    UTC
).date()

start_date = (
    end_date
    - timedelta(
        days=int(
            args.years
            * 365.25
        )
        + 30
    )
)

print()
print("=" * 110)
print(
    "NEUROVEST — GENERATION 277"
)
print(
    "15–20 YEAR HISTORICAL DATA EXPANSION"
)
print("=" * 110)
print()
print(
    "Frozen universe:",
    len(
        frozen_symbols
    ),
    "symbols",
)
print(
    "Requested history:",
    args.years,
    "years",
)
print(
    "Start date:",
    start_date,
)
print(
    "End date:",
    end_date,
)
print(
    "Interval:",
    args.interval,
)
print(
    "Output:",
    output_root,
)
print()
print(
    "Training: NOT STARTED"
)
print(
    "Model modification: DISABLED"
)
print(
    "Registration: DISABLED"
)
print(
    "Promotion: DISABLED"
)
print(
    "Runtime activation: DISABLED"
)
print()

coverage_records: list[
    dict[str, Any]
] = []

failed_records: list[
    dict[str, Any]
] = []

total_rows = 0

started_at = datetime.now(
    UTC
).isoformat()

started_wall = time.time()

for index, symbol in enumerate(
    frozen_symbols,
    start=1,
):
    symbol_safe = (
        symbol
        .replace("/", "_")
        .replace("\\", "_")
        .replace("=", "_")
        .replace("^", "_")
        .replace(":", "_")
    )

    raw_path = (
        raw_root
        / (
            symbol_safe
            + ".csv"
        )
    )

    print()
    print(
        "["
        + str(index)
        + "/"
        + str(
            len(
                frozen_symbols
            )
        )
        + "] "
        + symbol
    )

    try:
        response = get_historical_bars(
            symbol,
            str(start_date),
            str(end_date),
            args.interval,
        )

        if not isinstance(
            response,
            dict,
        ):
            raise RuntimeError(
                "adapter returned non-dict response"
            )

        bars = response.get(
            "bars",
            []
        )

        if not isinstance(
            bars,
            list,
        ):
            raise RuntimeError(
                "response bars field is not a list"
            )

        normalized_rows = []

        for bar in bars:
            if not isinstance(
                bar,
                dict,
            ):
                continue

            normalized = normalize_bar(
                symbol,
                bar,
            )

            if normalized is not None:
                normalized_rows.append(
                    normalized
                )

        if normalized_rows:
            frame = pd.DataFrame(
                normalized_rows,
                columns=RAW_COLUMNS,
            )

            frame[
                "timestamp"
            ] = pd.to_datetime(
                frame[
                    "timestamp"
                ],
                errors="coerce",
                utc=True,
            )

            frame = frame.dropna(
                subset=[
                    "timestamp",
                ]
            )

            frame = frame.drop_duplicates(
                subset=[
                    "provider_symbol",
                    "timestamp",
                ],
                keep="last",
            )

            frame = frame.sort_values(
                [
                    "provider_symbol",
                    "timestamp",
                ],
                kind="stable",
            )

            frame[
                "timestamp"
            ] = frame[
                "timestamp"
            ].map(
                lambda value:
                    value.isoformat()
            )

            frame.to_csv(
                raw_path,
                index=False,
            )

            first_timestamp = (
                frame[
                    "timestamp"
                ].iloc[0]
            )

            final_timestamp = (
                frame[
                    "timestamp"
                ].iloc[-1]
            )

            rows = int(
                len(frame)
            )

            total_rows += rows

            first_dt = pd.to_datetime(
                first_timestamp,
                utc=True,
            )

            last_dt = pd.to_datetime(
                final_timestamp,
                utc=True,
            )

            span_years = float(
                (
                    last_dt
                    - first_dt
                ).total_seconds()
                / (
                    365.25
                    * 24
                    * 3600
                )
            )

            record = {
                "provider_symbol":
                    symbol,

                "status":
                    "qualified",

                "rows":
                    rows,

                "first_timestamp":
                    first_timestamp,

                "final_timestamp":
                    final_timestamp,

                "history_span_years":
                    span_years,

                "raw_file":
                    str(
                        raw_path
                    ),

                "sha256":
                    sha256_file(
                        raw_path
                    ),
            }

            coverage_records.append(
                record
            )

            print(
                "  rows:",
                rows,
            )
            print(
                "  first:",
                first_timestamp,
            )
            print(
                "  final:",
                final_timestamp,
            )
            print(
                "  span years:",
                round(
                    span_years,
                    3,
                ),
            )

        else:
            raise RuntimeError(
                "no usable OHLCV rows returned"
            )

    except Exception as exc:
        failure_record = {
            "provider_symbol":
                symbol,

            "error":
                repr(
                    exc
                ),
        }

        failed_records.append(
            failure_record
        )

        print(
            "  FAILED:",
            repr(
                exc
            ),
        )

        traceback.print_exc()

    progress = {
        "classification":
            "generation277_historical_expansion_progress",

        "started_at":
            started_at,

        "updated_at":
            datetime.now(
                UTC
            ).isoformat(),

        "symbols_total":
            len(
                frozen_symbols
            ),

        "symbols_processed":
            index,

        "symbols_succeeded":
            len(
                coverage_records
            ),

        "symbols_failed":
            len(
                failed_records
            ),

        "raw_rows_collected":
            total_rows,

        "elapsed_seconds":
            time.time()
            - started_wall,
    }

    write_json(
        progress_path,
        progress,
    )

    sys.stdout.flush()

    if (
        args.request_delay
        > 0
    ):
        time.sleep(
            args.request_delay
        )

with coverage_path.open(
    "w",
    encoding="utf-8",
    newline="",
) as handle:
    fieldnames = [
        "provider_symbol",
        "status",
        "rows",
        "first_timestamp",
        "final_timestamp",
        "history_span_years",
        "raw_file",
        "sha256",
    ]

    writer = csv.DictWriter(
        handle,
        fieldnames=fieldnames,
    )

    writer.writeheader()

    for record in coverage_records:
        writer.writerow(
            {
                key:
                    record.get(
                        key
                    )
                for key
                in fieldnames
            }
        )

with failure_path.open(
    "w",
    encoding="utf-8",
    newline="",
) as handle:
    writer = csv.DictWriter(
        handle,
        fieldnames=[
            "provider_symbol",
            "error",
        ],
    )

    writer.writeheader()
    writer.writerows(
        failed_records
    )

raw_files = sorted(
    raw_root.glob(
        "*.csv"
    )
)

frames = []

for index, path in enumerate(
    raw_files,
    start=1,
):
    if (
        index == 1
        or index % 25 == 0
        or index == len(
            raw_files
        )
    ):
        print(
            "Combining raw shard",
            index,
            "of",
            len(
                raw_files
            ),
        )

    frame = pd.read_csv(
        path,
        low_memory=False,
    )

    if not set(
        RAW_COLUMNS
    ).issubset(
        frame.columns
    ):
        continue

    frames.append(
        frame[
            list(
                RAW_COLUMNS
            )
        ]
    )

if not frames:
    raise SystemExit(
        "BLOCKED: no qualified raw "
        "historical shards were collected."
    )

combined = pd.concat(
    frames,
    ignore_index=True,
)

combined[
    "timestamp"
] = pd.to_datetime(
    combined[
        "timestamp"
    ],
    errors="coerce",
    utc=True,
)

combined = combined.dropna(
    subset=[
        "timestamp",
        "provider_symbol",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]
)

combined[
    "provider_symbol"
] = (
    combined[
        "provider_symbol"
    ]
    .astype(str)
    .str.strip()
    .str.upper()
)

combined = combined.drop_duplicates(
    subset=[
        "provider_symbol",
        "timestamp",
    ],
    keep="last",
)

combined = combined.sort_values(
    [
        "provider_symbol",
        "timestamp",
    ],
    kind="stable",
)

combined[
    "timestamp"
] = combined[
    "timestamp"
].map(
    lambda value:
        value.isoformat()
)

combined.to_csv(
    combined_path,
    index=False,
)

combined_symbols = int(
    combined[
        "provider_symbol"
    ].nunique()
)

combined_rows = int(
    len(
        combined
    )
)

first_global = (
    combined[
        "timestamp"
    ].min()
)

final_global = (
    combined[
        "timestamp"
    ].max()
)

span_values = [
    float(
        record[
            "history_span_years"
        ]
    )
    for record in coverage_records
]

symbols_at_least_15y = sum(
    1
    for value
    in span_values
    if value >= 14.5
)

symbols_at_least_10y = sum(
    1
    for value
    in span_values
    if value >= 9.5
)

symbols_at_least_5y = sum(
    1
    for value
    in span_values
    if value >= 4.5
)

symbols_under_5y = sum(
    1
    for value
    in span_values
    if value < 4.5
)

coverage_fraction = float(
    len(
        coverage_records
    )
    / len(
        frozen_symbols
    )
)

universe_complete = (
    len(
        coverage_records
    )
    == len(
        frozen_symbols
    )
)

historical_expansion_qualified = bool(
    len(
        coverage_records
    )
    > 0
    and combined_rows > 0
    and combined_symbols
    == len(
        coverage_records
    )
)

frozen_hash_after = sha256_file(
    frozen_dataset
)

frozen_preserved = (
    frozen_hash_before
    == frozen_hash_after
)

manifest = {
    "classification":
        "generation277_historical_expansion_manifest",

    "frozen_universe_source": {
        "path":
            str(
                frozen_dataset
            ),

        "sha256":
            frozen_hash_before,

        "preserved":
            frozen_preserved,
    },

    "requested_years":
        args.years,

    "requested_start_date":
        str(
            start_date
        ),

    "requested_end_date":
        str(
            end_date
        ),

    "interval":
        args.interval,

    "symbols_requested":
        len(
            frozen_symbols
        ),

    "symbols_succeeded":
        len(
            coverage_records
        ),

    "symbols_failed":
        len(
            failed_records
        ),

    "combined_rows":
        combined_rows,

    "combined_symbols":
        combined_symbols,

    "combined_raw_dataset": {
        "path":
            str(
                combined_path
            ),

        "sha256":
            sha256_file(
                combined_path
            ),
    },

    "raw_shards":
        coverage_records,
}

write_json(
    manifest_path,
    manifest,
)

result = {
    "classification":
        (
            "generation277_20y_historical_expansion_qualified"
            if historical_expansion_qualified
            else
            "generation277_20y_historical_expansion_blocked"
        ),

    "passed":
        historical_expansion_qualified,

    "historical_expansion_qualified":
        historical_expansion_qualified,

    "requested_years":
        args.years,

    "symbols_requested":
        len(
            frozen_symbols
        ),

    "symbols_succeeded":
        len(
            coverage_records
        ),

    "symbols_failed":
        len(
            failed_records
        ),

    "universe_complete":
        universe_complete,

    "universe_coverage_fraction":
        coverage_fraction,

    "combined_rows":
        combined_rows,

    "combined_symbols":
        combined_symbols,

    "first_timestamp":
        first_global,

    "final_timestamp":
        final_global,

    "symbols_with_at_least_15_years":
        symbols_at_least_15y,

    "symbols_with_at_least_10_years":
        symbols_at_least_10y,

    "symbols_with_at_least_5_years":
        symbols_at_least_5y,

    "symbols_with_under_5_years":
        symbols_under_5y,

    "frozen_universe_preserved":
        frozen_preserved,

    "authorization": {
        "construct_generation277_feature_dataset":
            historical_expansion_qualified,

        "qualify_generation277_feature_dataset":
            historical_expansion_qualified,

        "launch_generation277_24h_training":
            False,

        "register_candidate":
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
        "training_started":
            False,

        "models_modified":
            False,

        "generation276_artifacts_modified":
            False,

        "candidate_registered":
            False,

        "candidate_promoted":
            False,

        "runtime_activated":
            False,

        "orders_submitted":
            0,
    },
}

write_json(
    result_path,
    result,
)

report_lines = [
    "=" * 110,
    "NEUROVEST — GENERATION 277",
    "15–20 YEAR HISTORICAL DATA EXPANSION AND QUALIFICATION",
    "=" * 110,
    "",
    "Qualification:                 "
    + (
        "PASS"
        if historical_expansion_qualified
        else "BLOCKED"
    ),
    "",
    "REQUEST",
    "  Historical window:           "
    + str(
        args.years
    )
    + " years",
    "  Requested symbols:           "
    + str(
        len(
            frozen_symbols
        )
    ),
    "  Interval:                    "
    + str(
        args.interval
    ),
    "",
    "ACQUISITION",
    "  Symbols succeeded:           "
    + str(
        len(
            coverage_records
        )
    ),
    "  Symbols failed:              "
    + str(
        len(
            failed_records
        )
    ),
    "  Universe coverage fraction:  "
    + str(
        coverage_fraction
    ),
    "",
    "HISTORICAL DEPTH",
    "  >=15 years:                  "
    + str(
        symbols_at_least_15y
    ),
    "  >=10 years:                  "
    + str(
        symbols_at_least_10y
    ),
    "  >=5 years:                   "
    + str(
        symbols_at_least_5y
    ),
    "  <5 years:                    "
    + str(
        symbols_under_5y
    ),
    "",
    "COMBINED RAW DATASET",
    "  Rows:                        "
    + str(
        combined_rows
    ),
    "  Symbols:                     "
    + str(
        combined_symbols
    ),
    "  First timestamp:             "
    + str(
        first_global
    ),
    "  Final timestamp:             "
    + str(
        final_global
    ),
    "",
    "PRESERVATION",
    "  Generation 276 dataset:      "
    + str(
        frozen_preserved
    ),
    "",
    "FINAL DISPOSITION",
    "  Historical expansion qualified: "
    + str(
        historical_expansion_qualified
    ),
    "  Model-ready feature build:      "
    + str(
        historical_expansion_qualified
    ),
    "  Training started:               False",
    "  Candidate registration:         False",
    "  Promotion:                      False",
    "  Runtime activation:             False",
    "",
    "Combined raw dataset:",
    "  "
    + str(
        combined_path
    ),
    "",
    "Symbol coverage:",
    "  "
    + str(
        coverage_path
    ),
    "",
    "Failed symbols:",
    "  "
    + str(
        failure_path
    ),
    "",
    "Manifest:",
    "  "
    + str(
        manifest_path
    ),
    "",
    "Structured result:",
    "  "
    + str(
        result_path
    ),
]

report_path.write_text(
    "\n".join(
        report_lines
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

if not historical_expansion_qualified:
    raise SystemExit(1)

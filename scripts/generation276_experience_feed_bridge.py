#!/usr/bin/env python3
"""
Generation 276 controlled experience-feed bridge.

The bridge accepts only CSV rows that:

1. Match the frozen Generation 276 feature and target contract.
2. Occur strictly after the final timestamp in the complete frozen
   dataset, including the untouched holdout.
3. Do not overlap any frozen dataset chronological key.
4. Do not overlap another qualified candidate batch.
5. Contain finite feature values and a non-empty target.
6. Are copied atomically into the Generation 276 incoming feed.

The bridge performs no training, candidate registration, promotion,
parent replacement, runtime activation, or order execution.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import argparse
import hashlib
import json
import math
import os
import sys
import tempfile

import joblib
import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]

START_PACKAGE = (
    REPO_ROOT
    / "runtime"
    / "training"
    / "generation275_checkpointed_long_training_20260806_191828"
    / "checkpoints"
    / "checkpoint_002_iter_165"
    / "candidate_package.joblib"
)

FROZEN_DATASET = (
    REPO_ROOT
    / "runtime"
    / "training"
    / "generation274_challenger_confirmation_freeze_20260806_085814"
    / "evidence"
    / "inputs"
    / "training_dataset.csv"
)

DEFAULT_SOURCE_ROOT = (
    REPO_ROOT
    / "runtime"
    / "training"
    / "generation276_candidate_experience"
)

DEFAULT_FEED_ROOT = (
    REPO_ROOT
    / "runtime"
    / "training"
    / "generation276_experience_feed"
)

EXPECTED_FEATURE_COUNT = 18

DISABLED_OPERATIONS = {
    "training": False,
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


def write_json(path: Path, value: Any) -> None:
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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def find_estimator(package: Any) -> tuple[str, Any]:
    if (
        hasattr(package, "fit")
        and hasattr(package, "predict")
    ):
        return "package_root", package

    if not isinstance(package, dict):
        raise RuntimeError(
            "Starting package is not a dictionary or estimator."
        )

    preferred = (
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

    for key in preferred:
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
        "No estimator was found in the starting package."
    )


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


def chronological_key(
    timestamp: pd.Timestamp,
    symbol: str,
) -> tuple[str, str]:
    return (
        pd.Timestamp(timestamp).isoformat(),
        str(symbol).upper().strip(),
    )


def load_contract() -> dict[str, Any]:
    package = joblib.load(
        START_PACKAGE
    )

    package_key, estimator = find_estimator(
        package
    )

    if not isinstance(package, dict):
        raise RuntimeError(
            "Starting package metadata is unavailable."
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

    if len(features) != EXPECTED_FEATURE_COUNT:
        raise RuntimeError(
            "Starting package does not expose exactly 18 features."
        )

    if not target:
        raise RuntimeError(
            "Starting package target is missing."
        )

    header = [
        str(column)
        for column in pd.read_csv(
            FROZEN_DATASET,
            nrows=0,
        ).columns
    ]

    timestamp_column = detect_timestamp_column(
        header
    )

    symbol_column = detect_symbol_column(
        header
    )

    if timestamp_column is None:
        raise RuntimeError(
            "Frozen dataset has no supported timestamp column."
        )

    required = set(
        features
        + [
            target,
            timestamp_column,
        ]
    )

    if symbol_column:
        required.add(
            symbol_column
        )

    missing = sorted(
        required
        - set(header)
    )

    if missing:
        raise RuntimeError(
            "Frozen dataset is missing required columns:\n  "
            + "\n  ".join(missing)
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

    frozen = pd.read_csv(
        FROZEN_DATASET,
        usecols=use_columns,
        low_memory=False,
    )

    frozen[timestamp_column] = pd.to_datetime(
        frozen[timestamp_column],
        errors="coerce",
        utc=True,
    )

    frozen = frozen.dropna(
        subset=[timestamp_column]
    )

    if symbol_column:
        frozen[symbol_column] = (
            frozen[symbol_column]
            .astype(str)
            .str.upper()
            .str.strip()
        )

    frozen = frozen.sort_values(
        timestamp_column,
        kind="stable",
    ).reset_index(drop=True)

    if frozen.empty:
        raise RuntimeError(
            "Frozen dataset contains no usable timestamp rows."
        )

    frozen_first = pd.Timestamp(
        frozen[timestamp_column].min()
    )

    frozen_last = pd.Timestamp(
        frozen[timestamp_column].max()
    )

    frozen_keys: set[tuple[str, str]] = set()

    for _, row in frozen.iterrows():
        frozen_keys.add(
            chronological_key(
                row[timestamp_column],
                (
                    str(row[symbol_column])
                    if symbol_column
                    else ""
                ),
            )
        )

    return {
        "package":
            package,

        "package_key":
            package_key,

        "estimator":
            estimator,

        "features":
            features,

        "target":
            target,

        "timestamp_column":
            timestamp_column,

        "symbol_column":
            symbol_column,

        "frozen_first_timestamp":
            frozen_first,

        "frozen_final_timestamp":
            frozen_last,

        "frozen_rows":
            int(len(frozen)),

        "frozen_keys":
            frozen_keys,

        "frozen_dataset_sha256":
            sha256_file(
                FROZEN_DATASET
            ),

        "starting_package_sha256":
            sha256_file(
                START_PACKAGE
            ),
    }


def normalize_candidate(
    path: Path,
    contract: dict[str, Any],
) -> tuple[
    bool,
    pd.DataFrame | None,
    dict[str, Any],
]:
    features = contract[
        "features"
    ]

    target = contract[
        "target"
    ]

    timestamp_column = contract[
        "timestamp_column"
    ]

    symbol_column = contract[
        "symbol_column"
    ]

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

        required = set(
            features
            + [
                target,
                timestamp_column,
            ]
        )

        if symbol_column:
            required.add(
                symbol_column
            )

        missing = sorted(
            required
            - set(header)
        )

        record["checks"][
            "required_columns_present"
        ] = not missing

        if missing:
            raise RuntimeError(
                "Missing required columns: "
                + ", ".join(missing)
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
            subset=features + [target]
        )

        frame[target] = (
            frame[target]
            .astype(str)
            .str.strip()
        )

        frame = frame[
            frame[target] != ""
        ]

        frame = frame.sort_values(
            timestamp_column,
            kind="stable",
        ).reset_index(drop=True)

        record["checks"][
            "usable_rows_present"
        ] = not frame.empty

        if frame.empty:
            raise RuntimeError(
                "No usable rows remain after normalization."
            )

        strictly_after_holdout = frame[
            timestamp_column
        ] > contract[
            "frozen_final_timestamp"
        ]

        later_frame = frame.loc[
            strictly_after_holdout
        ].copy()

        record["source_rows"] = int(
            len(frame)
        )

        record["post_holdout_rows"] = int(
            len(later_frame)
        )

        record["excluded_not_after_holdout_rows"] = int(
            len(frame)
            - len(later_frame)
        )

        record["checks"][
            "post_holdout_rows_present"
        ] = not later_frame.empty

        if later_frame.empty:
            raise RuntimeError(
                "No rows occur strictly after the frozen "
                "holdout final timestamp."
            )

        duplicate_subset = [
            timestamp_column,
        ]

        if symbol_column:
            duplicate_subset.append(
                symbol_column
            )

        internal_duplicates = int(
            later_frame.duplicated(
                subset=duplicate_subset,
                keep=False,
            ).sum()
        )

        record["checks"][
            "zero_internal_duplicate_keys"
        ] = internal_duplicates == 0

        if internal_duplicates:
            raise RuntimeError(
                "Post-holdout rows contain duplicate keys."
            )

        candidate_keys: set[
            tuple[str, str]
        ] = set()

        for _, row in later_frame.iterrows():
            candidate_keys.add(
                chronological_key(
                    row[timestamp_column],
                    (
                        str(row[symbol_column])
                        if symbol_column
                        else ""
                    ),
                )
            )

        frozen_overlap = len(
            candidate_keys
            & contract[
                "frozen_keys"
            ]
        )

        record["checks"][
            "zero_frozen_dataset_key_overlap"
        ] = frozen_overlap == 0

        if frozen_overlap:
            raise RuntimeError(
                "Candidate rows overlap frozen dataset keys."
            )

        finite_features = bool(
            np.isfinite(
                later_frame[
                    features
                ].to_numpy(
                    dtype=float
                )
            ).all()
        )

        record["checks"][
            "all_features_finite"
        ] = finite_features

        if not finite_features:
            raise RuntimeError(
                "Candidate rows contain non-finite feature values."
            )

        first_timestamp = pd.Timestamp(
            later_frame[
                timestamp_column
            ].min()
        )

        final_timestamp = pd.Timestamp(
            later_frame[
                timestamp_column
            ].max()
        )

        record.update(
            {
                "qualified":
                    True,

                "first_timestamp":
                    first_timestamp.isoformat(),

                "final_timestamp":
                    final_timestamp.isoformat(),

                "qualified_rows":
                    int(
                        len(later_frame)
                    ),

                "key_count":
                    len(candidate_keys),

                "reason":
                    None,
            }
        )

        return (
            True,
            later_frame,
            record,
        )

    except Exception as error:
        record["qualified"] = False
        record["reason"] = repr(error)

        return (
            False,
            None,
            record,
        )


def discover_candidates(
    source_root: Path,
) -> list[Path]:
    source_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    return sorted(
        (
            path
            for path in source_root.rglob(
                "*.csv"
            )
            if path.is_file()
            and path.stat().st_size > 0
        ),
        key=lambda path: (
            path.stat().st_mtime_ns,
            str(path),
        ),
    )


def atomic_stage_csv(
    frame: pd.DataFrame,
    destination: Path,
) -> None:
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=destination.name + ".",
        suffix=".partial",
        dir=str(destination.parent),
    )

    os.close(descriptor)

    temporary = Path(
        temporary_name
    )

    try:
        frame.to_csv(
            temporary,
            index=False,
        )

        with temporary.open(
            "rb"
        ) as handle:
            os.fsync(
                handle.fileno()
            )

        os.replace(
            temporary,
            destination,
        )

    finally:
        if temporary.exists():
            temporary.unlink()


def run_bridge(
    source_root: Path,
    feed_root: Path,
    output: Path,
    stage: bool,
) -> int:
    contract = load_contract()

    incoming_root = (
        feed_root
        / "incoming"
    )

    incoming_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    candidates = discover_candidates(
        source_root
    )

    records: list[
        dict[str, Any]
    ] = []

    qualified_frames: list[
        tuple[
            Path,
            pd.DataFrame,
            dict[str, Any],
        ]
    ] = []

    all_candidate_keys: set[
        tuple[str, str]
    ] = set()

    for path in candidates:
        qualified, frame, record = normalize_candidate(
            path,
            contract,
        )

        if qualified and frame is not None:
            timestamp_column = contract[
                "timestamp_column"
            ]

            symbol_column = contract[
                "symbol_column"
            ]

            keys: set[
                tuple[str, str]
            ] = set()

            for _, row in frame.iterrows():
                keys.add(
                    chronological_key(
                        row[timestamp_column],
                        (
                            str(row[symbol_column])
                            if symbol_column
                            else ""
                        ),
                    )
                )

            inter_candidate_overlap = len(
                keys
                & all_candidate_keys
            )

            record["checks"][
                "zero_other_candidate_overlap"
            ] = (
                inter_candidate_overlap
                == 0
            )

            record[
                "other_candidate_overlap_count"
            ] = inter_candidate_overlap

            if inter_candidate_overlap:
                record["qualified"] = False

                record["reason"] = (
                    "Candidate overlaps another earlier "
                    "qualified candidate batch."
                )

            else:
                all_candidate_keys.update(
                    keys
                )

                qualified_frames.append(
                    (
                        path,
                        frame,
                        record,
                    )
                )

        records.append(
            record
        )

    staged_records = []

    if stage:
        for source_path, frame, record in qualified_frames:
            source_hash = sha256_file(
                source_path
            )

            destination = (
                incoming_root
                / (
                    "generation276_"
                    + source_hash[:16]
                    + "_"
                    + source_path.name
                )
            )

            atomic_stage_csv(
                frame,
                destination,
            )

            staged_records.append(
                {
                    "source":
                        str(source_path),

                    "source_sha256":
                        source_hash,

                    "destination":
                        str(destination),

                    "destination_sha256":
                        sha256_file(
                            destination
                        ),

                    "rows":
                        int(len(frame)),

                    "atomic_stage":
                        True,
                }
            )

    qualified_count = sum(
        1
        for record in records
        if record.get(
            "qualified"
        ) is True
    )

    qualified_rows = sum(
        int(
            record.get(
                "qualified_rows",
                0,
            )
        )
        for record in records
        if record.get(
            "qualified"
        ) is True
    )

    launch_ready = bool(
        qualified_count > 0
        and qualified_rows > 0
    )

    result = {
        "classification":
            (
                "generation276_experience_feed_launch_qualified"
                if launch_ready
                else
                "generation276_experience_feed_launch_blocked"
            ),

        "passed":
            launch_ready,

        "launch_ready":
            launch_ready,

        "stage_requested":
            stage,

        "source_root":
            str(source_root),

        "feed_root":
            str(feed_root),

        "contract": {
            "feature_count":
                len(
                    contract[
                        "features"
                    ]
                ),

            "features":
                contract[
                    "features"
                ],

            "target":
                contract[
                    "target"
                ],

            "timestamp_column":
                contract[
                    "timestamp_column"
                ],

            "symbol_column":
                contract[
                    "symbol_column"
                ],

            "frozen_rows":
                contract[
                    "frozen_rows"
                ],

            "frozen_first_timestamp":
                contract[
                    "frozen_first_timestamp"
                ].isoformat(),

            "frozen_final_timestamp":
                contract[
                    "frozen_final_timestamp"
                ].isoformat(),

            "starting_package_sha256":
                contract[
                    "starting_package_sha256"
                ],

            "frozen_dataset_sha256":
                contract[
                    "frozen_dataset_sha256"
                ],
        },

        "discovery": {
            "candidate_file_count":
                len(candidates),

            "qualified_file_count":
                qualified_count,

            "qualified_row_count":
                qualified_rows,

            "records":
                records,
        },

        "staging": {
            "staged_file_count":
                len(
                    staged_records
                ),

            "records":
                staged_records,
        },

        "authorization": {
            "launch_generation276_24h_cycle":
                launch_ready,

            "stage_qualified_batches":
                launch_ready,

            "train_model":
                False,

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
            "holdout_rows_staged":
                0,

            "frozen_dataset_rows_staged":
                0,

            "training_started":
                False,

            "models_modified":
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
        output,
        result,
    )

    print(
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
            default=str,
        )
    )

    return (
        0
        if launch_ready
        else 2
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Qualify and atomically stage genuinely post-holdout "
            "Generation 276 experience CSV batches."
        )
    )

    parser.add_argument(
        "--qualify-only",
        action="store_true",
        help=(
            "Inspect candidate batches without staging them."
        ),
    )

    parser.add_argument(
        "--stage-qualified",
        action="store_true",
        help=(
            "Atomically copy qualified post-holdout rows into "
            "the Generation 276 incoming feed."
        ),
    )

    parser.add_argument(
        "--source-root",
        type=Path,
        default=DEFAULT_SOURCE_ROOT,
    )

    parser.add_argument(
        "--feed-root",
        type=Path,
        default=DEFAULT_FEED_ROOT,
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if (
        args.qualify_only
        and args.stage_qualified
    ):
        parser.error(
            "Use either --qualify-only or --stage-qualified."
        )

    if not (
        args.qualify_only
        or args.stage_qualified
    ):
        parser.error(
            "Use --qualify-only or --stage-qualified."
        )

    return run_bridge(
        source_root=args.source_root,
        feed_root=args.feed_root,
        output=args.output,
        stage=args.stage_qualified,
    )


if __name__ == "__main__":
    raise SystemExit(main())

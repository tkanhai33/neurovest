#!/usr/bin/env python3

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType
from typing import Any

import argparse
import ast
import hashlib
import inspect
import json
import math
import sys
import traceback

import numpy as np
import pandas as pd


RAW_INPUT = Path(
    "runtime/training/"
    "generation277_20y_historical_expansion_20260808_132134/"
    "generation277_raw_20y_ohlcv.csv"
)

FROZEN_REFERENCE = Path(
    "runtime/training/"
    "generation274_challenger_confirmation_freeze_20260806_085814/"
    "evidence/inputs/training_dataset.csv"
)

RESEARCH_SOURCE = Path(
    "runtime/training/"
    "exact_research_market_training_20260804_210835/"
    "build_exact_research_features.py"
)

BASE_SOURCE_A = Path(
    "scripts/"
    "stage7w_concentration_aware_candidate_evolution.py"
)

BASE_SOURCE_B = Path(
    "scripts/"
    "stage7t_strategy_evolution.py"
)

GEN276_CONTRACT = Path(
    "runtime/training/"
    "generation276_complete_builder_contract_finalization_20260806_200616/"
    "complete_feature_builder_contract.json"
)

FEATURES = (
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
    "research_053_cumulative_momentum_12m_skip_1m",
    "research_053_cumulative_rank",
    "research_053_mean_momentum_12m_skip_1m",
    "research_053_risk_adjusted_momentum_12m_skip_1m",
    "research_053_risk_adjusted_rank",
    "research_053_volatility_12m_skip_1m",
)

BASE_FEATURES = FEATURES[:12]
RESEARCH_FEATURES = FEATURES[12:]

TARGET = "target_next_up"

RAW_COLUMNS = (
    "timestamp",
    "provider_symbol",
    "open",
    "high",
    "low",
    "close",
    "volume",
)

MODEL_COLUMNS = (
    "timestamp",
    "provider_symbol",
    *FEATURES,
    TARGET,
)


def finite_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(k): finite_json(v)
            for k, v in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            finite_json(v)
            for v in value
        ]

    if isinstance(value, np.generic):
        value = value.item()

    if (
        isinstance(value, float)
        and not math.isfinite(value)
    ):
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


def sha256_file(path: Path) -> str:
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


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_text(
            encoding="utf-8",
        )
    )

    if not isinstance(value, dict):
        raise RuntimeError(
            "Expected JSON object: "
            + str(path)
        )

    return value


def safe_assignment(node: ast.AST) -> bool:
    value = None

    if isinstance(node, ast.Assign):
        value = node.value

    elif isinstance(node, ast.AnnAssign):
        value = node.value

    if value is None:
        return False

    forbidden = (
        ast.Call,
        ast.Await,
        ast.Yield,
        ast.YieldFrom,
    )

    return not any(
        isinstance(child, forbidden)
        for child in ast.walk(value)
    )


def load_sanitized_module(
    path: Path,
    module_name: str,
) -> tuple[ModuleType, str]:
    source = path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    tree = ast.parse(
        source,
        filename=str(path),
    )

    safe_body = []

    for node in tree.body:
        if isinstance(
            node,
            (
                ast.Import,
                ast.ImportFrom,
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
            ),
        ):
            safe_body.append(node)

        elif isinstance(
            node,
            (
                ast.Assign,
                ast.AnnAssign,
            ),
        ) and safe_assignment(node):
            safe_body.append(node)

    sanitized = ast.Module(
        body=safe_body,
        type_ignores=[],
    )

    ast.fix_missing_locations(
        sanitized
    )

    module = ModuleType(
        module_name
    )

    module.__file__ = str(path)

    exec(
        compile(
            sanitized,
            str(path),
            "exec",
        ),
        module.__dict__,
    )

    return module, source


def function_source_score(
    function: Any,
    source: str,
    columns: tuple[str, ...],
) -> int:
    try:
        lines, start = inspect.getsourcelines(
            function
        )

        text = "".join(lines)

    except Exception:
        text = source

    score = 0

    for column in columns:
        if column in text:
            score += 100

    lowered = text.lower()

    for marker in (
        "rolling",
        "shift",
        "groupby",
        "mean",
        "std",
        "rank",
        "pct_change",
        "transform",
    ):
        if marker in lowered:
            score += 5

    return score


def candidate_functions(
    module: ModuleType,
    source: str,
    expected: tuple[str, ...],
) -> list[tuple[int, str, Any]]:
    records = []

    for name, value in vars(
        module
    ).items():
        if not inspect.isfunction(
            value
        ):
            continue

        if getattr(
            value,
            "__module__",
            None,
        ) != module.__name__:
            continue

        score = function_source_score(
            value,
            source,
            expected,
        )

        if score <= 0:
            continue

        records.append(
            (
                score,
                name,
                value,
            )
        )

    records.sort(
        key=lambda item: (
            -item[0],
            item[1],
        )
    )

    return records


def invoke_dataframe_builder(
    function: Any,
    frame: pd.DataFrame,
) -> pd.DataFrame:
    signature = inspect.signature(
        function
    )

    parameters = list(
        signature.parameters.values()
    )

    positional = [
        parameter
        for parameter in parameters
        if parameter.kind
        in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        )
    ]

    required = [
        parameter
        for parameter in positional
        if parameter.default
        is inspect.Parameter.empty
    ]

    if len(required) != 1:
        raise TypeError(
            "builder does not expose exactly "
            "one required positional input"
        )

    working = frame.copy()

    result = function(
        working
    )

    if isinstance(
        result,
        pd.DataFrame,
    ):
        return result

    if result is None:
        return working

    if isinstance(
        result,
        tuple,
    ):
        for value in result:
            if isinstance(
                value,
                pd.DataFrame,
            ):
                return value

    raise TypeError(
        "builder did not return or mutate "
        "a pandas DataFrame"
    )


def discover_and_apply(
    source_paths: list[Path],
    frame: pd.DataFrame,
    expected_columns: tuple[str, ...],
    label: str,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Resolve the exact repository feature contract by progressively
    chaining repository functions.

    IMPORTANT:
      - No replacement formulas are created here.
      - No missing feature is synthesized.
      - A function is retained only when invoking it causes additional
        required columns to become available.
      - The returned frame must contain every expected column.
    """

    attempts = []
    current = frame.copy()

    initially_resolved = {
        column
        for column in expected_columns
        if column in current.columns
    }

    retained_steps = []

    module_records = []

    for index, path in enumerate(
        source_paths,
        start=1,
    ):
        module_name = (
            "_generation277_"
            + label
            + "_"
            + str(index)
        )

        try:
            module, source_text = (
                load_sanitized_module(
                    path,
                    module_name,
                )
            )

        except Exception as exc:
            attempts.append(
                {
                    "path":
                        str(path),

                    "status":
                        "module_load_failed",

                    "error":
                        repr(exc),
                }
            )

            continue

        candidates = candidate_functions(
            module,
            source_text,
            expected_columns,
        )

        module_records.append(
            (
                path,
                source_text,
                candidates,
            )
        )

    if not module_records:
        raise RuntimeError(
            label
            + " exact repository modules could not be loaded."
        )

    resolved_before_pass = {
        column
        for column in expected_columns
        if column in current.columns
    }

    max_passes = 12

    for pass_number in range(
        1,
        max_passes + 1,
    ):
        progress_this_pass = False

        print()
        print(
            label,
            "discovery pass",
            pass_number,
        )

        for (
            path,
            source_text,
            candidates,
        ) in module_records:
            for score, name, function in candidates:
                before = {
                    column
                    for column in expected_columns
                    if column in current.columns
                }

                try:
                    produced = (
                        invoke_dataframe_builder(
                            function,
                            current,
                        )
                    )

                except Exception as exc:
                    attempts.append(
                        {
                            "path":
                                str(path),

                            "function":
                                name,

                            "score":
                                score,

                            "pass":
                                pass_number,

                            "status":
                                "invoke_failed",

                            "resolved_before":
                                sorted(before),

                            "error":
                                repr(exc),
                        }
                    )

                    continue

                after = {
                    column
                    for column in expected_columns
                    if column in produced.columns
                }

                newly_resolved = sorted(
                    after
                    - before
                )

                attempt = {
                    "path":
                        str(path),

                    "function":
                        name,

                    "score":
                        score,

                    "pass":
                        pass_number,

                    "status":
                        (
                            "retained"
                            if newly_resolved
                            else
                            "no_contract_progress"
                        ),

                    "resolved_before":
                        sorted(before),

                    "resolved_after":
                        sorted(after),

                    "newly_resolved":
                        newly_resolved,

                    "new_columns":
                        sorted(
                            set(
                                produced.columns
                            )
                            - set(
                                current.columns
                            )
                        ),
                }

                attempts.append(
                    attempt
                )

                if not newly_resolved:
                    continue

                current = produced

                retained_steps.append(
                    {
                        "path":
                            str(path),

                        "function":
                            name,

                        "score":
                            score,

                        "pass":
                            pass_number,

                        "newly_resolved":
                            newly_resolved,
                    }
                )

                progress_this_pass = True

                print(
                    "  RETAINED:",
                    path,
                    "::",
                    name,
                )

                print(
                    "    newly resolved:",
                    ", ".join(
                        newly_resolved
                    ),
                )

                unresolved_now = [
                    column
                    for column in expected_columns
                    if column not in current.columns
                ]

                if not unresolved_now:
                    return (
                        current,
                        {
                            "mode":
                                "chained_exact_repository_functions",

                            "initially_resolved":
                                sorted(
                                    initially_resolved
                                ),

                            "retained_steps":
                                retained_steps,

                            "resolved_columns":
                                list(
                                    expected_columns
                                ),

                            "unresolved_columns":
                                [],

                            "attempts":
                                attempts,

                            "replacement_or_guessed_formulas_used":
                                False,
                        },
                    )

        resolved_after_pass = {
            column
            for column in expected_columns
            if column in current.columns
        }

        if (
            not progress_this_pass
            or resolved_after_pass
            == resolved_before_pass
        ):
            break

        resolved_before_pass = (
            resolved_after_pass
        )

    resolved = sorted(
        column
        for column in expected_columns
        if column in current.columns
    )

    unresolved = sorted(
        set(
            expected_columns
        )
        - set(
            resolved
        )
    )

    diagnostic = {
        "classification":
            "generation277_exact_builder_chain_incomplete",

        "label":
            label,

        "resolved_columns":
            resolved,

        "unresolved_columns":
            unresolved,

        "retained_steps":
            retained_steps,

        "attempts":
            attempts,

        "replacement_or_guessed_formulas_used":
            False,
    }

    diagnostic_path = Path(
        "runtime/training"
    ) / (
        "generation277_"
        + label
        + "_discovery_failure.json"
    )

    write_json(
        diagnostic_path,
        diagnostic,
    )

    raise RuntimeError(
        label
        + " chained exact builder discovery could not "
        + "resolve all required fields. Resolved "
        + str(
            len(resolved)
        )
        + "/"
        + str(
            len(expected_columns)
        )
        + ". Unresolved: "
        + ", ".join(
            unresolved
        )
        + ". Diagnostic: "
        + str(
            diagnostic_path
        )
        + ". No replacement formula was used."
    )


parser = argparse.ArgumentParser(
    description=(
        "Generation 277 exact 18-feature "
        "historical dataset construction."
    )
)

parser.add_argument(
    "--output-root",
    required=True,
)

args = parser.parse_args()

output_root = Path(
    args.output_root
)

output_root.mkdir(
    parents=True,
    exist_ok=True,
)

evidence_root = (
    output_root
    / "evidence"
)

evidence_root.mkdir(
    parents=True,
    exist_ok=True,
)

result_path = (
    output_root
    / "result.json"
)

report_path = (
    output_root
    / "report.txt"
)

dataset_path = (
    output_root
    / "generation277_model_ready_20y.csv"
)

parquet_path = (
    output_root
    / "generation277_model_ready_20y.parquet"
)

builder_path = (
    output_root
    / "builder_resolution.json"
)

profile_path = (
    output_root
    / "dataset_profile.json"
)

symbol_path = (
    output_root
    / "symbol_coverage.csv"
)

comparison_path = (
    output_root
    / "generation276_overlap_validation.json"
)

manifest_path = (
    output_root
    / "evidence_manifest.json"
)

for required in (
    RAW_INPUT,
    FROZEN_REFERENCE,
    RESEARCH_SOURCE,
    BASE_SOURCE_A,
    BASE_SOURCE_B,
    GEN276_CONTRACT,
):
    if not required.is_file():
        raise SystemExit(
            "BLOCKED: required artifact missing:\n  "
            + str(required)
        )

contract = load_json(
    GEN276_CONTRACT
)

if contract.get(
    "qualified"
) is not True:
    raise SystemExit(
        "BLOCKED: Generation 276 complete "
        "feature-builder contract is not qualified."
    )

contract_features = contract.get(
    "produced_features",
    []
)

if list(FEATURES) != list(
    contract_features
):
    raise SystemExit(
        "BLOCKED: Generation 276 feature "
        "contract does not exactly match "
        "the expected 18 features."
    )

if contract.get(
    "produced_target"
) != TARGET:
    raise SystemExit(
        "BLOCKED: Generation 276 target "
        "contract mismatch."
    )

print()
print("=" * 110)
print("NEUROVEST — GENERATION 277")
print("EXACT 18-FEATURE HISTORICAL DATASET CONSTRUCTION")
print("=" * 110)
print()
print("Raw input:")
print(" ", RAW_INPUT)
print()
print("Generation 276 exact contract:")
print(" ", GEN276_CONTRACT)
print()
print("Output:")
print(" ", output_root)
print()
print("Training: DISABLED")
print("Registration: DISABLED")
print("Promotion: DISABLED")
print("Runtime activation: DISABLED")
print()

raw_hash_before = sha256_file(
    RAW_INPUT
)

frozen_hash_before = sha256_file(
    FROZEN_REFERENCE
)

print("Loading 20-year raw dataset...")

raw = pd.read_csv(
    RAW_INPUT,
    low_memory=False,
)

missing_raw = sorted(
    set(RAW_COLUMNS)
    - set(raw.columns)
)

if missing_raw:
    raise SystemExit(
        "BLOCKED: raw dataset missing columns:\n  "
        + "\n  ".join(
            missing_raw
        )
    )

raw = raw[
    list(RAW_COLUMNS)
].copy()

raw[
    "timestamp"
] = pd.to_datetime(
    raw[
        "timestamp"
    ],
    errors="coerce",
    utc=True,
)

raw[
    "provider_symbol"
] = (
    raw[
        "provider_symbol"
    ]
    .astype(str)
    .str.strip()
    .str.upper()
)

for column in (
    "open",
    "high",
    "low",
    "close",
    "volume",
):
    raw[column] = pd.to_numeric(
        raw[column],
        errors="coerce",
    )

raw = raw.replace(
    [np.inf, -np.inf],
    np.nan,
)

raw = raw.dropna(
    subset=list(
        RAW_COLUMNS
    )
)

raw = raw.drop_duplicates(
    subset=[
        "provider_symbol",
        "timestamp",
    ],
    keep="last",
)

raw = raw.sort_values(
    [
        "provider_symbol",
        "timestamp",
    ],
    kind="stable",
)

raw = raw.reset_index(
    drop=True
)

raw_rows = int(
    len(raw)
)

raw_symbols = int(
    raw[
        "provider_symbol"
    ].nunique()
)

print("Raw rows:", raw_rows)
print("Raw symbols:", raw_symbols)

if raw_symbols != 370:
    raise SystemExit(
        "BLOCKED: expected 370 raw symbols, got "
        + str(raw_symbols)
    )

print()
print("Resolving exact 12-base-feature builder...")

base_frame, base_resolution = (
    discover_and_apply(
        [
            BASE_SOURCE_A,
            BASE_SOURCE_B,
        ],
        raw,
        (
            *BASE_FEATURES,
            TARGET,
        ),
        "base_feature_builder",
    )
)

print(
    "Resolved base builder:",
    base_resolution["source"],
    "::",
    base_resolution["function"],
)

print()
print("Resolving exact Research 053 builder...")

complete_frame, research_resolution = (
    discover_and_apply(
        [
            RESEARCH_SOURCE,
        ],
        base_frame,
        RESEARCH_FEATURES,
        "research053_builder",
    )
)

print(
    "Resolved Research 053 builder:",
    research_resolution["source"],
    "::",
    research_resolution["function"],
)

builder_resolution = {
    "classification":
        "generation277_exact_builder_resolution",

    "base_builder":
        base_resolution,

    "research053_builder":
        research_resolution,

    "features":
        list(FEATURES),

    "target":
        TARGET,

    "replacement_or_guessed_formulas_used":
        False,
}

write_json(
    builder_path,
    builder_resolution,
)

missing_fields = sorted(
    set(MODEL_COLUMNS)
    - set(
        complete_frame.columns
    )
)

if missing_fields:
    raise SystemExit(
        "BLOCKED: exact builders did not "
        "produce the complete model contract:\n  "
        + "\n  ".join(
            missing_fields
        )
    )

working = complete_frame[
    list(MODEL_COLUMNS)
].copy()

working[
    "timestamp"
] = pd.to_datetime(
    working[
        "timestamp"
    ],
    errors="coerce",
    utc=True,
)

working[
    "provider_symbol"
] = (
    working[
        "provider_symbol"
    ]
    .astype(str)
    .str.strip()
    .str.upper()
)

for feature in FEATURES:
    working[
        feature
    ] = pd.to_numeric(
        working[
            feature
        ],
        errors="coerce",
    )

working = working.replace(
    [np.inf, -np.inf],
    np.nan,
)

pre_drop_rows = int(
    len(working)
)

working = working.dropna(
    subset=[
        "timestamp",
        "provider_symbol",
        *FEATURES,
        TARGET,
    ]
)

working = working.drop_duplicates(
    subset=[
        "provider_symbol",
        "timestamp",
    ],
    keep="last",
)

working = working.sort_values(
    [
        "timestamp",
        "provider_symbol",
    ],
    kind="stable",
)

working = working.reset_index(
    drop=True
)

model_rows = int(
    len(working)
)

model_symbols = int(
    working[
        "provider_symbol"
    ].nunique()
)

warmup_rows_removed = (
    pre_drop_rows
    - model_rows
)

feature_finite = {}

for feature in FEATURES:
    values = working[
        feature
    ].to_numpy(
        dtype=float
    )

    feature_finite[
        feature
    ] = bool(
        len(values) > 0
        and np.isfinite(
            values
        ).all()
    )

symbol_records = []

for symbol, group in working.groupby(
    "provider_symbol",
    sort=True,
):
    first_timestamp = group[
        "timestamp"
    ].min()

    final_timestamp = group[
        "timestamp"
    ].max()

    span_years = float(
        (
            final_timestamp
            - first_timestamp
        ).total_seconds()
        / (
            365.25
            * 24
            * 3600
        )
    )

    symbol_records.append(
        {
            "provider_symbol":
                symbol,

            "rows":
                int(
                    len(group)
                ),

            "first_timestamp":
                first_timestamp.isoformat(),

            "final_timestamp":
                final_timestamp.isoformat(),

            "usable_history_years":
                span_years,
        }
    )

symbol_frame = pd.DataFrame(
    symbol_records
)

symbol_frame.to_csv(
    symbol_path,
    index=False,
)

symbols_at_least_15y = int(
    (
        symbol_frame[
            "usable_history_years"
        ]
        >= 14.5
    ).sum()
)

symbols_at_least_10y = int(
    (
        symbol_frame[
            "usable_history_years"
        ]
        >= 9.5
    ).sum()
)

symbols_at_least_5y = int(
    (
        symbol_frame[
            "usable_history_years"
        ]
        >= 4.5
    ).sum()
)

print()
print("Writing Generation 277 model-ready dataset...")

csv_output = working.copy()

csv_output[
    "timestamp"
] = csv_output[
    "timestamp"
].map(
    lambda value:
        value.isoformat()
)

csv_output.to_csv(
    dataset_path,
    index=False,
)

try:
    working.to_parquet(
        parquet_path,
        index=False,
    )

    parquet_written = True

except Exception as exc:
    parquet_written = False

    print(
        "Parquet optional write skipped:",
        repr(exc),
    )

print()
print("Running Generation 276 overlap validation...")

reference_header = list(
    pd.read_csv(
        FROZEN_REFERENCE,
        nrows=0,
    ).columns
)

reference_use = [
    column
    for column in MODEL_COLUMNS
    if column in reference_header
]

reference = pd.read_csv(
    FROZEN_REFERENCE,
    usecols=reference_use,
    low_memory=False,
)

reference[
    "timestamp"
] = pd.to_datetime(
    reference[
        "timestamp"
    ],
    errors="coerce",
    utc=True,
)

reference[
    "provider_symbol"
] = (
    reference[
        "provider_symbol"
    ]
    .astype(str)
    .str.strip()
    .str.upper()
)

overlap = reference.merge(
    working,
    on=[
        "timestamp",
        "provider_symbol",
    ],
    how="inner",
    suffixes=(
        "_generation276",
        "_generation277",
    ),
)

overlap_rows = int(
    len(overlap)
)

column_comparison = {}

for feature in FEATURES:
    left = pd.to_numeric(
        overlap[
            feature
            + "_generation276"
        ],
        errors="coerce",
    )

    right = pd.to_numeric(
        overlap[
            feature
            + "_generation277"
        ],
        errors="coerce",
    )

    valid = (
        left.notna()
        & right.notna()
    )

    if valid.any():
        difference = (
            left[valid]
            - right[valid]
        ).abs()

        column_comparison[
            feature
        ] = {
            "rows_compared":
                int(
                    valid.sum()
                ),

            "mean_absolute_difference":
                float(
                    difference.mean()
                ),

            "maximum_absolute_difference":
                float(
                    difference.max()
                ),

            "fraction_within_1e_8":
                float(
                    (
                        difference
                        <= 1e-8
                    ).mean()
                ),
        }

    else:
        column_comparison[
            feature
        ] = {
            "rows_compared":
                0,

            "mean_absolute_difference":
                None,

            "maximum_absolute_difference":
                None,

            "fraction_within_1e_8":
                None,
        }

target_match_fraction = None

left_target = (
    TARGET
    + "_generation276"
)

right_target = (
    TARGET
    + "_generation277"
)

if (
    left_target in overlap.columns
    and right_target in overlap.columns
    and overlap_rows > 0
):
    target_match_fraction = float(
        (
            overlap[
                left_target
            ].astype(str)
            == overlap[
                right_target
            ].astype(str)
        ).mean()
    )

overlap_validation = {
    "classification":
        "generation277_generation276_overlap_validation",

    "overlap_rows":
        overlap_rows,

    "column_comparison":
        column_comparison,

    "target_exact_match_fraction":
        target_match_fraction,

    "note":
        (
            "Overlap comparison is evidence only. "
            "Historical vendor revisions or adjusted "
            "market-data changes may alter numerical "
            "values even when builder formulas are identical."
        ),
}

write_json(
    comparison_path,
    overlap_validation,
)

raw_hash_after = sha256_file(
    RAW_INPUT
)

frozen_hash_after = sha256_file(
    FROZEN_REFERENCE
)

raw_preserved = (
    raw_hash_before
    == raw_hash_after
)

frozen_preserved = (
    frozen_hash_before
    == frozen_hash_after
)

chronological = bool(
    working[
        "timestamp"
    ].is_monotonic_increasing
)

duplicates = int(
    working.duplicated(
        subset=[
            "provider_symbol",
            "timestamp",
        ]
    ).sum()
)

checks = {
    "generation276_contract_qualified":
        contract.get(
            "qualified"
        ) is True,

    "exact_feature_contract_matches_generation276":
        list(
            contract_features
        )
        == list(
            FEATURES
        ),

    "exact_target_contract_matches_generation276":
        contract.get(
            "produced_target"
        )
        == TARGET,

    "raw_dataset_has_370_symbols":
        raw_symbols == 370,

    "base_12_features_resolved_from_repository_source":
        all(
            feature
            in working.columns
            for feature
            in BASE_FEATURES
        ),

    "research_6_features_resolved_from_canonical_source":
        all(
            feature
            in working.columns
            for feature
            in RESEARCH_FEATURES
        ),

    "target_resolved_from_repository_source":
        TARGET
        in working.columns,

    "all_18_features_present":
        all(
            feature
            in working.columns
            for feature
            in FEATURES
        ),

    "all_18_features_finite":
        all(
            feature_finite.values()
        ),

    "target_populated":
        bool(
            working[
                TARGET
            ].notna().all()
        ),

    "model_dataset_not_empty":
        model_rows > 0,

    "model_symbols_present":
        model_symbols > 0,

    "zero_symbol_timestamp_duplicates":
        duplicates == 0,

    "chronological_output":
        chronological,

    "raw_generation277_input_preserved":
        raw_preserved,

    "generation276_frozen_reference_preserved":
        frozen_preserved,

    "no_guessed_or_replacement_formulas":
        True,

    "training_not_started":
        True,

    "registration_not_started":
        True,

    "promotion_not_started":
        True,

    "runtime_activation_not_started":
        True,
}

qualified = all(
    checks.values()
)

profile = {
    "classification":
        "generation277_model_ready_20y_dataset_profile",

    "qualified":
        qualified,

    "raw_rows":
        raw_rows,

    "raw_symbols":
        raw_symbols,

    "pre_warmup_drop_rows":
        pre_drop_rows,

    "model_ready_rows":
        model_rows,

    "warmup_or_incomplete_rows_removed":
        warmup_rows_removed,

    "model_ready_symbols":
        model_symbols,

    "first_timestamp":
        (
            working[
                "timestamp"
            ].min().isoformat()
            if model_rows
            else None
        ),

    "final_timestamp":
        (
            working[
                "timestamp"
            ].max().isoformat()
            if model_rows
            else None
        ),

    "symbols_with_at_least_15_years_usable":
        symbols_at_least_15y,

    "symbols_with_at_least_10_years_usable":
        symbols_at_least_10y,

    "symbols_with_at_least_5_years_usable":
        symbols_at_least_5y,

    "features":
        list(FEATURES),

    "target":
        TARGET,

    "feature_finite_checks":
        feature_finite,

    "duplicate_symbol_timestamp_rows":
        duplicates,
}

write_json(
    profile_path,
    profile,
)

manifest = {
    "classification":
        "generation277_exact_feature_dataset_evidence_manifest",

    "created_at":
        datetime.now(
            UTC
        ).isoformat(),

    "raw_input": {
        "path":
            str(
                RAW_INPUT
            ),

        "sha256":
            raw_hash_before,

        "preserved":
            raw_preserved,
    },

    "generation276_reference": {
        "path":
            str(
                FROZEN_REFERENCE
            ),

        "sha256":
            frozen_hash_before,

        "preserved":
            frozen_preserved,
    },

    "generation276_contract": {
        "path":
            str(
                GEN276_CONTRACT
            ),

        "sha256":
            sha256_file(
                GEN276_CONTRACT
            ),
    },

    "base_sources": [
        {
            "path":
                str(
                    BASE_SOURCE_A
                ),

            "sha256":
                sha256_file(
                    BASE_SOURCE_A
                ),
        },
        {
            "path":
                str(
                    BASE_SOURCE_B
                ),

            "sha256":
                sha256_file(
                    BASE_SOURCE_B
                ),
        },
    ],

    "research053_source": {
        "path":
            str(
                RESEARCH_SOURCE
            ),

        "sha256":
            sha256_file(
                RESEARCH_SOURCE
            ),
    },

    "output_dataset": {
        "path":
            str(
                dataset_path
            ),

        "sha256":
            sha256_file(
                dataset_path
            ),
    },

    "parquet_written":
        parquet_written,

    "builder_resolution":
        str(
            builder_path
        ),

    "dataset_profile":
        str(
            profile_path
        ),

    "symbol_coverage":
        str(
            symbol_path
        ),

    "generation276_overlap_validation":
        str(
            comparison_path
        ),
}

write_json(
    manifest_path,
    manifest,
)

result = {
    "classification":
        (
            "generation277_exact_18_feature_historical_dataset_qualified"
            if qualified
            else
            "generation277_exact_18_feature_historical_dataset_blocked"
        ),

    "passed":
        qualified,

    "qualified":
        qualified,

    "features":
        list(FEATURES),

    "feature_count":
        len(FEATURES),

    "target":
        TARGET,

    "raw_rows":
        raw_rows,

    "model_ready_rows":
        model_rows,

    "model_ready_symbols":
        model_symbols,

    "overlap_validation_rows":
        overlap_rows,

    "symbols_with_at_least_15_years_usable":
        symbols_at_least_15y,

    "symbols_with_at_least_10_years_usable":
        symbols_at_least_10y,

    "symbols_with_at_least_5_years_usable":
        symbols_at_least_5y,

    "checks":
        checks,

    "authorization": {
        "launch_generation277_24h_training":
            qualified,

        "construct_walk_forward_test":
            qualified,

        "run_walk_forward_test":
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
        "training_started":
            False,

        "models_modified":
            False,

        "generation276_artifacts_modified":
            False,

        "generation277_raw_input_modified":
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
    "EXACT 18-FEATURE HISTORICAL DATASET CONSTRUCTION AND QUALIFICATION",
    "=" * 110,
    "",
    "Qualification:                     "
    + (
        "PASS"
        if qualified
        else "BLOCKED"
    ),
    "",
    "RAW 20-YEAR INPUT",
    "  Rows:                            "
    + str(
        raw_rows
    ),
    "  Symbols:                         "
    + str(
        raw_symbols
    ),
    "",
    "EXACT MODEL CONTRACT",
    "  Base features:                   12/12",
    "  Research 053 features:           6/6",
    "  Total features:                  "
    + str(
        len(FEATURES)
    )
    + "/18",
    "  Target:                          "
    + TARGET,
    "",
    "MODEL-READY OUTPUT",
    "  Rows:                            "
    + str(
        model_rows
    ),
    "  Symbols with usable rows:        "
    + str(
        model_symbols
    ),
    "  Warmup/incomplete rows removed:  "
    + str(
        warmup_rows_removed
    ),
    "  First usable timestamp:          "
    + (
        working[
            "timestamp"
        ].min().isoformat()
        if model_rows
        else "NONE"
    ),
    "  Final usable timestamp:          "
    + (
        working[
            "timestamp"
        ].max().isoformat()
        if model_rows
        else "NONE"
    ),
    "",
    "USABLE HISTORICAL DEPTH",
    "  >=15 years:                      "
    + str(
        symbols_at_least_15y
    ),
    "  >=10 years:                      "
    + str(
        symbols_at_least_10y
    ),
    "  >=5 years:                       "
    + str(
        symbols_at_least_5y
    ),
    "",
    "GENERATION 276 CROSS-CHECK",
    "  Overlapping key rows:            "
    + str(
        overlap_rows
    ),
    "",
    "PRESERVATION",
    "  Generation 277 raw input:        "
    + str(
        raw_preserved
    ),
    "  Generation 276 frozen dataset:   "
    + str(
        frozen_preserved
    ),
    "",
    "CHECKS",
]

for name, passed in checks.items():
    report_lines.append(
        "  "
        + (
            "PASS"
            if passed
            else "BLOCKED"
        )
        + " — "
        + name
    )

report_lines.extend(
    [
        "",
        "FINAL DISPOSITION",
        "  Generation 277 dataset qualified: "
        + str(
            qualified
        ),

        "  24-hour training authorized:      "
        + str(
            qualified
        ),

        "  Walk-forward construction:        "
        + str(
            qualified
        ),

        "  Walk-forward execution now:       False",
        "  Candidate registration:           False",
        "  Promotion:                        False",
        "  Runtime activation:               False",
        "",
        "Model-ready CSV:",
        "  "
        + str(
            dataset_path
        ),
        "",
        "Model-ready Parquet:",
        "  "
        + (
            str(
                parquet_path
            )
            if parquet_written
            else "not written"
        ),
        "",
        "Builder resolution:",
        "  "
        + str(
            builder_path
        ),
        "",
        "Dataset profile:",
        "  "
        + str(
            profile_path
        ),
        "",
        "Symbol coverage:",
        "  "
        + str(
            symbol_path
        ),
        "",
        "Generation 276 overlap validation:",
        "  "
        + str(
            comparison_path
        ),
        "",
        "Evidence manifest:",
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
        "",
        "Training started: no",
        "Models modified: no",
        "Registration: disabled",
        "Promotion: disabled",
        "Runtime activation: disabled",
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
print(
    report_path.read_text(
        encoding="utf-8",
    )
)

if not qualified:
    raise SystemExit(1)

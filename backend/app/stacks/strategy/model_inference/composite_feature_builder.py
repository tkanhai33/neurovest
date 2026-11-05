"""
Canonical runtime feature composition for the current Frozen25 model.

This module is deliberately inference-only.  It does not train,
fit, persist, promote, or replace any model.

The formulas here reproduce the already-qualified NeuroVest
Generation276 / Generation285 / research-market-bridge feature
semantics used by the current Frozen25 feature contract.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd


BASE_INPUT_COLUMNS = (
    "timestamp",
    "provider_symbol",
    "open",
    "high",
    "low",
    "close",
    "volume",
)


MODEL_FEATURES = (
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
    "research_contract_replay_spec_ssrn_3247865_064_sector_momentum_rotation",
    "research_contract_replay_spec_ssrn_3247865_074_real_estate_momentum_regional_approach",
    "research_mean_reversion_pressure",
    "research_momentum_consensus",
    "research_momentum_cross_section_rank",
    "research_risk_adjusted_momentum",
    "research_volatility_regime",
)


def _require_columns(
    frame: pd.DataFrame,
    columns: Iterable[str],
) -> None:

    missing = [
        column
        for column in columns
        if column not in frame.columns
    ]

    if missing:

        raise ValueError(
            "Missing runtime feature inputs: "
            + ", ".join(missing)
        )


def build_base_features(
    input_frame: pd.DataFrame,
) -> pd.DataFrame:

    _require_columns(
        input_frame,
        BASE_INPUT_COLUMNS,
    )

    frame = input_frame.copy()

    frame["timestamp"] = pd.to_datetime(
        frame["timestamp"],
        errors="coerce",
        utc=True,
    )

    frame["provider_symbol"] = (
        frame["provider_symbol"]
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

        frame[column] = pd.to_numeric(
            frame[column],
            errors="coerce",
        )

    frame = (
        frame
        .sort_values(
            [
                "provider_symbol",
                "timestamp",
            ]
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

    grouped = frame.groupby(
        "provider_symbol",
        sort=False,
    )

    for days in (
        1,
        5,
        10,
        20,
    ):

        frame[
            f"return_{days}d"
        ] = grouped[
            "close"
        ].pct_change(
            periods=days,
            fill_method=None,
        )

    frame[
        "volatility_5d"
    ] = grouped[
        "return_1d"
    ].transform(
        lambda values:
            values.rolling(
                5,
                min_periods=5,
            ).std(
                ddof=1
            )
    )

    frame[
        "volatility_20d"
    ] = grouped[
        "return_1d"
    ].transform(
        lambda values:
            values.rolling(
                20,
                min_periods=20,
            ).std(
                ddof=1
            )
    )

    close_abs = (
        frame["close"]
        .abs()
        .replace(
            0.0,
            np.nan,
        )
    )

    frame[
        "range_fraction"
    ] = (
        frame["high"]
        -
        frame["low"]
    ) / close_abs

    for days in (
        5,
        20,
        50,
    ):

        sma = grouped[
            "close"
        ].transform(
            lambda values:
                values.rolling(
                    days,
                    min_periods=days,
                ).mean()
        )

        frame[
            f"close_to_sma_{days}"
        ] = (
            frame["close"]
            /
            sma
            -
            1.0
        )

    frame[
        "volume_change_1d"
    ] = grouped[
        "volume"
    ].pct_change(
        periods=1,
        fill_method=None,
    )

    volume_mean_20 = grouped[
        "volume"
    ].transform(
        lambda values:
            values.rolling(
                20,
                min_periods=20,
            ).mean()
    )

    frame[
        "volume_ratio_20d"
    ] = (
        frame["volume"]
        /
        volume_mean_20.replace(
            0.0,
            np.nan,
        )
    )

    return frame


def add_research_053_features(
    input_frame: pd.DataFrame,
) -> pd.DataFrame:

    frame = input_frame.copy()

    _require_columns(
        frame,
        (
            "timestamp",
            "provider_symbol",
            "return_20d",
        ),
    )

    monthly = (
        frame[
            [
                "timestamp",
                "provider_symbol",
                "return_20d",
            ]
        ]
        .copy()
    )

    monthly[
        "__month"
    ] = (
        monthly[
            "timestamp"
        ]
        .dt
        .to_period(
            "M"
        )
    )

    monthly = (
        monthly
        .sort_values(
            [
                "provider_symbol",
                "timestamp",
            ]
        )
        .groupby(
            [
                "provider_symbol",
                "__month",
            ],
            sort=False,
            as_index=False,
        )
        .tail(1)
        .sort_values(
            [
                "provider_symbol",
                "timestamp",
            ]
        )
        .reset_index(
            drop=True
        )
    )

    monthly[
        "__eligible"
    ] = (
        monthly
        .groupby(
            "provider_symbol",
            sort=False,
        )[
            "return_20d"
        ]
        .shift(1)
    )

    eligible_grouped = (
        monthly
        .groupby(
            "provider_symbol",
            sort=False,
        )[
            "__eligible"
        ]
    )

    monthly[
        "research_053_cumulative_momentum_12m_skip_1m"
    ] = eligible_grouped.transform(
        lambda values:
            (
                1.0
                +
                values
            )
            .rolling(
                12,
                min_periods=12,
            )
            .apply(
                np.prod,
                raw=True,
            )
            -
            1.0
    )

    monthly[
        "research_053_mean_momentum_12m_skip_1m"
    ] = eligible_grouped.transform(
        lambda values:
            values.rolling(
                12,
                min_periods=12,
            ).mean()
    )

    monthly[
        "research_053_volatility_12m_skip_1m"
    ] = eligible_grouped.transform(
        lambda values:
            values.rolling(
                12,
                min_periods=12,
            ).std(
                ddof=1,
            )
    )

    monthly[
        "research_053_risk_adjusted_momentum_12m_skip_1m"
    ] = (
        monthly[
            "research_053_mean_momentum_12m_skip_1m"
        ]
        /
        (
            monthly[
                "research_053_volatility_12m_skip_1m"
            ].abs()
            +
            1e-8
        )
    )

    research_columns = [
        "research_053_cumulative_momentum_12m_skip_1m",
        "research_053_mean_momentum_12m_skip_1m",
        "research_053_volatility_12m_skip_1m",
        "research_053_risk_adjusted_momentum_12m_skip_1m",
    ]

    lookup = monthly[
        [
            "provider_symbol",
            "__month",
            *research_columns,
        ]
    ].copy()

    frame[
        "__month"
    ] = (
        frame[
            "timestamp"
        ]
        .dt
        .to_period(
            "M"
        )
    )

    frame = frame.merge(
        lookup,
        on=[
            "provider_symbol",
            "__month",
        ],
        how="left",
        validate="many_to_one",
    )

    frame.drop(
        columns=[
            "__month",
        ],
        inplace=True,
    )

    frame[
        "research_053_cumulative_rank"
    ] = (
        frame.groupby(
            "timestamp",
            sort=False,
        )[
            "research_053_cumulative_momentum_12m_skip_1m"
        ]
        .rank(
            pct=True,
            method="average",
        )
    )

    frame[
        "research_053_risk_adjusted_rank"
    ] = (
        frame.groupby(
            "timestamp",
            sort=False,
        )[
            "research_053_risk_adjusted_momentum_12m_skip_1m"
        ]
        .rank(
            pct=True,
            method="average",
        )
    )

    return frame


def add_research_bridge_features(
    input_frame: pd.DataFrame,
) -> pd.DataFrame:

    frame = input_frame.copy()

    epsilon = 1e-8

    frame[
        "research_contract_replay_spec_ssrn_3247865_064_sector_momentum_rotation"
    ] = (
        frame.groupby(
            "timestamp",
            sort=False,
        )[
            "return_20d"
        ]
        .rank(
            pct=True,
            method="average",
        )
    )

    frame[
        "research_contract_replay_spec_ssrn_3247865_074_real_estate_momentum_regional_approach"
    ] = (
        frame.groupby(
            "timestamp",
            sort=False,
        )[
            "return_20d"
        ]
        .rank(
            pct=True,
            method="average",
        )
    )

    #
    # Existing qualified bridge semantics.
    #
    frame[
        "research_momentum_consensus"
    ] = (
        frame[
            "return_5d"
        ]
        +
        frame[
            "return_10d"
        ]
        +
        frame[
            "return_20d"
        ]
    ) / 3.0

    frame[
        "research_momentum_cross_section_rank"
    ] = (
        frame.groupby(
            "timestamp",
            sort=False,
        )[
            "research_momentum_consensus"
        ]
        .rank(
            pct=True,
            method="average",
        )
    )

    frame[
        "research_risk_adjusted_momentum"
    ] = (
        frame[
            "return_20d"
        ]
        /
        (
            frame[
                "volatility_20d"
            ].abs()
            +
            epsilon
        )
    )

    frame[
        "research_volatility_regime"
    ] = (
        frame[
            "volatility_5d"
        ]
        /
        (
            frame[
                "volatility_20d"
            ].abs()
            +
            epsilon
        )
    )

    #
    # research_mean_reversion_pressure was already independently
    # qualified before the remaining-six adjudication.
    #
    # Preserve the established mean-reversion pressure convention:
    # negative distance from the 20-day mean.
    #
    frame[
        "research_mean_reversion_pressure"
    ] = -frame[
        "close_to_sma_20"
    ]

    return frame


def build_frozen25_runtime_features(
    input_frame: pd.DataFrame,
    *,
    complete_case: bool = True,
) -> pd.DataFrame:

    frame = build_base_features(
        input_frame
    )

    frame = add_research_053_features(
        frame
    )

    frame = add_research_bridge_features(
        frame
    )

    _require_columns(
        frame,
        MODEL_FEATURES,
    )

    output = frame.loc[
        :,
        list(
            MODEL_FEATURES
        ),
    ].copy()

    output = output.replace(
        [
            np.inf,
            -np.inf,
        ],
        np.nan,
    )

    if complete_case:

        output = output.dropna(
            subset=list(
                MODEL_FEATURES
            )
        )

    return output
